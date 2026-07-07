"""
Geração, exibição e persistência do relatório de avaliação.

Médias do sumário:
  Apenas scores >= 0 entram no cálculo.
  Casos com score=-1 (não avaliados, sem suporte PMD, before=0) são excluídos.
"""

import json
from smell_eval.config import CaseResult, PassKResult
from smell_eval.code_extractor import extract_java_code


def build(results: list[CaseResult]) -> dict:
    return {
        "total_cases": len(results),
        "summary":     _summary(results),
        "cases":       [_case_to_dict(r) for r in results],
    }


def print_report(report: dict) -> None:
    SEP = "═" * 70
    sep = "─" * 70

    def fmt(v):
        if v is None or (isinstance(v, float) and v < 0):
            return "N/A"
        return f"{v:.4f}"

    base = report["summary"]["base_model"]
    ft   = report["summary"]["finetuned_model"]

    print(f"\n{SEP}")
    print("  EVALUATION REPORT — CODE SMELL REFACTORING")
    print(f"  Total cases: {report['total_cases']}")
    print(SEP)
    print(f"\n  {'Metric':<32} {'Base Model':>12} {'Fine-Tuned':>12} {'Delta':>10}")
    print(f"  {sep}")

    metrics = [
        ("BLEU-4 (L1)",            base["avg_bleu"],        ft["avg_bleu"]),
        ("Compilation (L2)",        base["avg_compilation"], ft["avg_compilation"]),
        ("Param. Reduction (L3)",   base["avg_prr"],         ft["avg_prr"]),
        ("SRR — PMD (L4)",          base["avg_srr"],         ft["avg_srr"]),
        ("pass@1 (L5)",             base["avg_pass_at_1"],   ft["avg_pass_at_1"]),
        ("pass@3 (L5)",             base["avg_pass_at_3"],   ft["avg_pass_at_3"]),
        ("pass@5 (L5)",             base["avg_pass_at_5"],   ft["avg_pass_at_5"]),
    ]

    for name, bv, fv in metrics:
        delta = ""
        if (bv is not None and fv is not None
                and isinstance(bv, float) and isinstance(fv, float)
                and bv >= 0 and fv >= 0):
            d = fv - bv
            delta = f"{'+' if d >= 0 else ''}{d:.4f}"
        print(f"  {name:<32} {fmt(bv):>12} {fmt(fv):>12} {delta:>10}")

    print(f"\n{SEP}")


def save(report: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"[saved] {path}")

def _avg(values: list) -> float | None:
    """Média excluindo None e valores < 0 (não avaliados)."""
    valid = [v for v in values if v is not None and isinstance(v, float) and v >= 0]
    return round(sum(valid) / len(valid), 4) if valid else None


def _collect_score(results: list[CaseResult], attr: str) -> list:
    return [
        getattr(r, attr).score
        for r in results
        if getattr(r, attr) is not None
    ]


def _collect_passk(results: list[CaseResult], model: str, k: str) -> list:
    values = []
    for r in results:
        pk = r.passk_base if model == "base" else r.passk_finetuned
        if pk is not None:
            v = getattr(pk, k)
            if v is not None:
                values.append(v)
    return values


def _summary(results: list[CaseResult]) -> dict:
    def model_summary(prefix: str) -> dict:
        return {
            "avg_bleu":        _avg(_collect_score(results, f"bleu_{prefix}")),
            "avg_compilation": _avg(_collect_score(results, f"compile_{prefix}")),
            "avg_prr":         _avg(_collect_score(results, f"prr_{prefix}")),
            "avg_srr":         _avg(_collect_score(results, f"srr_{prefix}")),
            "avg_pass_at_1":   _avg(_collect_passk(results, prefix, "pass_at_1")),
            "avg_pass_at_3":   _avg(_collect_passk(results, prefix, "pass_at_3")),
            "avg_pass_at_5":   _avg(_collect_passk(results, prefix, "pass_at_5")),
        }
    return {
        "base_model":      model_summary("base"),
        "finetuned_model": model_summary("finetuned"),
    }


def _serialize_layer(result) -> dict | None:
    """
    Serializa LayerResult para dict.
    """
    if result is None:
        return None

    d = {
        "score":     result.score,
        "evaluated": result.score >= 0,
        "details":   result.details,
    }

    if result.passed is not None:
        d["passed"] = result.passed

    return d


def _serialize_passk(result: PassKResult | None) -> dict | None:
    return vars(result) if result else None


def _case_to_dict(r: CaseResult) -> dict:
    return {
        "index":           r.case_index,
        "smell_type":      r.smell_type,
        "description":     r.description,
        "source":          r.source,
        "input_code":      r.input_code,
        "expected_output": r.expected_output,
        "base": {
            "bleu":             _serialize_layer(r.bleu_base),
            "compilation":      _serialize_layer(r.compile_base),
            "prr":              _serialize_layer(r.prr_base),
            "srr":              _serialize_layer(r.srr_base),
            "passk":            _serialize_passk(r.passk_base),
            "output_raw":       r.base_output or "",
            "output_extracted": extract_java_code(r.base_output or ""),
        },
        "finetuned": {
            "bleu":             _serialize_layer(r.bleu_finetuned),
            "compilation":      _serialize_layer(r.compile_finetuned),
            "prr":              _serialize_layer(r.prr_finetuned),
            "srr":              _serialize_layer(r.srr_finetuned),
            "passk":            _serialize_passk(r.passk_finetuned),
            "output_raw":       r.finetuned_output or "",
            "output_extracted": extract_java_code(r.finetuned_output or ""),
        },
    }