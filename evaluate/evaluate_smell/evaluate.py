"""
evaluate.py — Pipeline de avaliação de refatoração de code smells com LLMs.

Camadas de avaliação:
  L1 — BLEU-4              Similaridade lexical da saída vs ground truth
  L2 — Compilation Rate    Código sintaticamente válido (javac)
  L3 — PRR                 Parameter Reduction Rate — apenas LPL/PO/DC
  L4 — SRR via PMD         Smell removido segundo regra PMD calibrada
  L5 — pass@k (k=1,3,5)   Corretude com múltiplas tentativas

Uso:
  python evaluate.py                      # dataset embutido
  python evaluate.py --yaml dataset.yaml  # YAML
  python evaluate.py --skip-passk         # sem L5
"""
import transformers.utils.import_utils as _tfu
_tfu.check_torch_load_is_safe = lambda: None

import transformers.modeling_utils as _tmu
_tmu.check_torch_load_is_safe = lambda: None

import argparse
import functools
import sys

from smell_eval.config import CONFIG, CaseResult, LayerResult
from smell_eval.preflight import check_all
from smell_eval.data.dataset import load_test_cases
from smell_eval.models.inference import load_model, run_inference, models_available
from smell_eval.layers.layer1_bleu        import evaluate as eval_bleu
from smell_eval.layers.layer2_compilation import evaluate as eval_compile
from smell_eval.layers.layer3_prr         import evaluate as eval_prr
from smell_eval.layers.layer4_pmd         import evaluate as eval_pmd
from smell_eval.layers.layer5_passk       import evaluate_passk
from smell_eval.report.builder            import build, print_report, save


def _run_layers(tc, output_base: str, output_ft: str,
                tok_b, mdl_b, tok_ft, mdl_ft,
                skip_passk: bool,
                results: list) -> CaseResult:

    r = CaseResult(
        case_index=0,
        smell_type=tc.smell_type,
        description=tc.description,
        source=tc.source,
        input_code=tc.input_code,
        expected_output=tc.expected_output,
        base_output=output_base,
        finetuned_output=output_ft,
    )

    print("  [L1] BLEU-4...")
    r.bleu_base      = eval_bleu(output_base, tc.expected_output)
    r.bleu_finetuned = eval_bleu(output_ft,   tc.expected_output)

    print("  [L2] Compilation...")
    r.compile_base      = eval_compile(output_base)
    r.compile_finetuned = eval_compile(output_ft)

    print("  [L3] Parameter Reduction Rate...")
    r.prr_base      = eval_prr(tc.input_code, output_base, tc.smell_type)
    r.prr_finetuned = eval_prr(tc.input_code, output_ft,   tc.smell_type)

    print("  [L4] SRR via PMD...")
    try:
        # Se compilação falhou, PMD vai crashar com StackOverflow
        if r.compile_base.passed is False:
            r.srr_base = LayerResult(
                score=-1.0,
                details={"skipped": "compilation failed - PMD skipped to avoid crash"},
            )
        else:
            r.srr_base = eval_pmd(tc.input_code, output_base, tc.smell_type)

        if r.compile_finetuned.passed is False:
            r.srr_finetuned = LayerResult(
                score=-1.0,
                details={"skipped": "compilation failed - PMD skipped to avoid crash"},
            )
        else:
            r.srr_finetuned = eval_pmd(tc.input_code, output_ft, tc.smell_type)

    except RuntimeError as e:
        # PMD crashou no before 
        print(f"\n[ABORT] PMD execution error in case '{tc.smell_type}':")
        print(f"  {e}")
        print("  Partial results saved to disk.")
        report = build(results)
        save(report, CONFIG["output_json"])
        sys.exit(1)

    if not skip_passk:
        print("  [L5] pass@k...")
        generate_base = functools.partial(run_inference, tok_b,  mdl_b)
        generate_ft   = functools.partial(run_inference, tok_ft, mdl_ft)
        r.passk_base      = evaluate_passk(tc.input_code, generate_base, tc.smell_type)
        r.passk_finetuned = evaluate_passk(tc.input_code, generate_ft,   tc.smell_type)

    _print_case_summary(r)
    return r

def _print_case_summary(r: CaseResult) -> None:
    def s(lr):
        if lr is None:
            return "N/A"
        return "N/A" if lr.score < 0 else f"{lr.score:.4f}"

    def pk(pkr, attr):
        if pkr is None:
            return "N/A"
        v = getattr(pkr, attr)
        return f"{v:.4f}" if v is not None else "N/A"

    print(
        f"  → L1 bleu  base={s(r.bleu_base)} ft={s(r.bleu_finetuned)} | "
        f"L2 compilation base={s(r.compile_base)} ft={s(r.compile_finetuned)} | "
        f"L3 prr base={s(r.prr_base)} ft={s(r.prr_finetuned)} | "
        f"L4 srr base={s(r.srr_base)} ft={s(r.srr_finetuned)}"
    )
    if r.passk_base or r.passk_finetuned:
        print(
            f"     L5 pass@1 base={pk(r.passk_base,'pass_at_1')} "
            f"ft={pk(r.passk_finetuned,'pass_at_1')} | "
            f"pass@5 base={pk(r.passk_base,'pass_at_5')} "
            f"ft={pk(r.passk_finetuned,'pass_at_5')}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Avalia LLMs na tarefa de refatoração de code smells Java"
    )
    parser.add_argument("--yaml",       help="YAML de casos de teste (formato InstructLab)")
    parser.add_argument("--skip-passk", action="store_true",
                        help="Pula L5 pass@k (execução mais rápida)")
    args = parser.parse_args()

    if args.yaml:
        CONFIG["test_yaml_path"] = args.yaml

    cases = load_test_cases(CONFIG.get("test_yaml_path"))
    cases.sort(key=lambda tc: tc.smell_type != "God Class")

    check_all(cases)

    mem_base = {0: "10GiB", 1: "10GiB", 2: "0GiB", 3: "0GiB"}
    mem_ft   = {0: "0GiB", 1: "0GiB", 2: "10GiB", 3: "10GiB"}

    tok_b,  mdl_b  = load_model(CONFIG["base_model_path"],      "base",       max_memory=mem_base)
    tok_ft, mdl_ft = load_model(CONFIG["finetuned_model_path"], "fine-tuned", max_memory=mem_ft)

    if not models_available(mdl_b, mdl_ft):
        print("\n[ERROR] Models not found. Set paths in smell_eval/config.py")
        sys.exit(1)

    results = []
    for i, tc in enumerate(cases):
        print(f"\n{'─'*65}")
        print(f"[case {i+1}/{len(cases)}] {tc.smell_type}: {tc.description}")
        print(f"  source: {tc.source}")

        print("  Running base model...")
        output_base = run_inference(tok_b,  mdl_b,  tc.input_code, tc.smell_type,
                                    temperature=CONFIG["temperature"])
        print("  Running fine-tuned model...")
        output_ft   = run_inference(tok_ft, mdl_ft, tc.input_code, tc.smell_type,
                                    temperature=CONFIG["temperature"])

        r = _run_layers(tc, output_base, output_ft,
                        tok_b, mdl_b, tok_ft, mdl_ft,
                        skip_passk=args.skip_passk,
                        results=results)
        r.case_index = i
        results.append(r)

    report = build(results)
    print_report(report)
    save(report, CONFIG["output_json"])


if __name__ == "__main__":
    main()
