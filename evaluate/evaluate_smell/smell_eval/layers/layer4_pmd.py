"""
Camada 4 — Smell Removal Rate (SRR) via PMD.

Executa PMD com a regra mapeada ao smell_type antes e depois da refatoração.
Calcula SRR = (violations_before - violations_after) / violations_before.

PMD output:
  returncode=0 : OK, zero violations found   (stdout = "{}")
  returncode=4 : OK, violations found        (stdout = JSON with violations)
  other        : PMD execution error

SRR behavior when before=0:
  Se PMD não detecta o smell no código original, não há baseline para medir.
  Retorna score=-1, evaluated=False.
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
from typing import Optional

from smell_eval.config import CONFIG, LayerResult
from smell_eval.code_extractor import extract_java_code


# Mapeamento Smell
def _r(key: str) -> str:
    return CONFIG[key]


_SMELL_TO_RULESET: dict[str, str | None] = {
    "Long Parameter List":              _r("pmd_ruleset_lpl"),
    "Long Method":                      _r("pmd_ruleset_method"),
    "Long Method / Duplicate Code":     _r("pmd_ruleset_method"),
    "Switch Statement":                 _r("pmd_ruleset_switch"),
    "Complex Method":                   _r("pmd_ruleset_switch"),
    "God Class":                        _r("pmd_ruleset_god"),
    "Magic Number":                     _r("pmd_ruleset_magic"),
    "Dead Code":                        "category/java/bestpractices.xml/UnusedPrivateMethod",
    "Improper Naming":                  _r("pmd_ruleset_naming"),
    "Large Class":                      _r("pmd_ruleset_large"),
    "Duplicate Code":                   None,
    "Duplicate Code Across Classes":    None,
    "Feature Envy":                     None,
    "Lazy Class":                       None,
    "Indecent Exposure":                None,
    "Comments":                         None,
}


# Validação
class PmdValidationError(RuntimeError):
    """Levantado quando validate_all() encontra problema que impediria execução."""
    pass


def validate_all(test_cases: list) -> None:
    """
    Valida todas as condições necessárias para a camada 4 ANTES de iniciar.
    Levanta PmdValidationError com lista completa de problemas encontrados.
    """
    errors = []

    # PMD disponível
    pmd = _find_pmd()
    if not pmd:
        raise PmdValidationError(
            "PMD not found. Download from https://github.com/pmd/pmd/releases "
            "and set CONFIG['pmd_path']."
        )

    # Rulesets existem
    smells_in_dataset = {tc.smell_type for tc in test_cases}
    for smell in sorted(smells_in_dataset):
        ruleset = _SMELL_TO_RULESET.get(smell)
        if ruleset is None:
            continue 
        if not _ruleset_exists(ruleset):
            errors.append(f"[ruleset not found] smell='{smell}' → {ruleset}")

    if errors:
        raise PmdValidationError(
            "PMD ruleset validation failed:\n" + "\n".join(f"  ✗ {e}" for e in errors)
        )

    # Sanity check: cada caso deve disparar before > 0
    print("[L4 preflight] Validating PMD detects smell in each input case...")
    sanity_failures = []
    for tc in test_cases:
        ruleset = _SMELL_TO_RULESET.get(tc.smell_type)
        if ruleset is None:
            continue
        count, err = _count_violations(pmd, ruleset, tc.input_code)
        status = "✓" if (count or 0) > 0 else "✗"
        print(f"  {status} [{tc.smell_type}] before={count}  err={err}")
        if err:
            sanity_failures.append(
                f"[PMD error] smell='{tc.smell_type}': {err}"
            )
        elif (count or 0) == 0:
            sanity_failures.append(
                f"[before=0] smell='{tc.smell_type}': PMD detects 0 violations in input. "
                f"Ruleset: {os.path.basename(ruleset)}. "
                f"Either the threshold is too high or the code does not match the rule."
            )

    if sanity_failures:
        raise PmdValidationError(
            "PMD sanity check failed — fix these cases before running evaluation:\n"
            + "\n".join(f"  ✗ {e}" for e in sanity_failures)
        )

    print("[L4 preflight] All cases passed PMD sanity check.\n")


# Avaliação
def evaluate(original: str, refactored: str, smell_type: str) -> LayerResult:
    """
    Calcula SRR para o smell_type dado.

    Returns:
      score ∈ [0.0, 1.0]   : SRR calculado (before > 0)
      score = -1.0         : smell sem suporte, PMD indisponível, before=0, ou erro
      evaluated = True     : PMD rodou e before > 0
      evaluated = False    : PMD não rodou ou before == 0 (sem baseline)
      passed = True        : smell completamente removido (after == 0)
      passed = False       : smell ainda presente ou piorou
    """
    ruleset = _SMELL_TO_RULESET.get(smell_type)

    if ruleset is None:
        return LayerResult(
            score=-1.0,
            details={
                "skipped": True,
                "reason":  f"'{smell_type}' has no reliable PMD support — SRR not calculated.",
            },
        )

    pmd = _find_pmd()
    if not pmd:
        return LayerResult(
            score=-1.0,
            details={"error": "PMD not found. Set CONFIG['pmd_path']."},
        )

    if not _ruleset_exists(ruleset):
        return LayerResult(
            score=-1.0,
            details={"error": f"Ruleset not found: {ruleset}"},
        )

    clean_refactored = extract_java_code(refactored)

    before, before_err = _count_violations(pmd, ruleset, original)
    after,  after_err  = _count_violations(pmd, ruleset, clean_refactored)

    # before com erro 
    if before_err:
        raise RuntimeError(
            f"PMD execution failed for smell='{smell_type}': "
            f"before_err={before_err}\nRuleset: {ruleset}\n"
            "Fix PMD setup before continuing — aborting to avoid wasting time."
        )

    # after com erro
    if after_err:
        print(
            f"\n  [L4 warning] PMD error on model output for smell='{smell_type}':\n"
            f"  {after_err}\n"
            f"  (case not aborted — score=-1, passed=None)"
        )
        return LayerResult(
            score=-1.0,
            details={
                "error":         f"PMD error on model output: {after_err}",
                "smells_before": before,
                "smells_after":  -1,
                "ruleset":       os.path.basename(ruleset),
            },
            passed=None,
        )

    if before == 0:
        return LayerResult(
            score=-1.0,
            details={
                "smells_before":  0,
                "smells_after":   after,
                "no_baseline":    True,
                "reason":         (
                    "PMD detected 0 violations in the original code. "
                    "No baseline to measure removal. "
                    "Run validate_all() before evaluation to catch this early."
                ),
                "ruleset":        os.path.basename(ruleset),
                "threshold_note": _threshold_note(smell_type),
            },
        )

    srr = _calc_srr(before, after)
    return LayerResult(
        score=round(srr, 4),
        details={
            "smells_before":  before,
            "smells_after":   after,
            "srr":            round(srr, 4),
            "smell_removed":  (after == 0),
            "ruleset":        os.path.basename(ruleset),
            "threshold_note": _threshold_note(smell_type),
        },
        passed=(after == 0),
    )


# Execução
def _count_violations(pmd: str, ruleset: str, code: str) -> tuple[int, str | None]:
    """
    Runs PMD and returns (n_violations, error_msg).
    error_msg is None if OK, descriptive string on real error.
    """
    wrapped = code if _has_class_declaration(code) else f"public class Check {{\n{code}\n}}"

    with tempfile.TemporaryDirectory() as tmpdir:
        java_file = os.path.join(tmpdir, "Check.java")
        with open(java_file, "w") as f:
            f.write(wrapped)
        try:
            result = subprocess.run(
                [
                    pmd, "check",
                    "-d", java_file,
                    "-R", ruleset,
                    "-f", "json",
                    "--no-cache",
                    "--no-progress",
                ],
                capture_output=True, text=True, timeout=60,
            )
        except Exception as e:
            return -1, str(e)

    # returncode=0 : OK, no violations; returncode=4 : OK, violations found
    if result.returncode not in (0, 4):
        stderr_msg = (result.stderr or "").strip()
        stdout_msg = (result.stdout or "").strip()
        detail = stderr_msg or stdout_msg or "(no output)"
        return -1, f"PMD returncode={result.returncode}:\n{detail}"

    if result.returncode == 0:
        return 0, None

    try:
        data = json.loads(result.stdout)
        violations = sum(len(f.get("violations", [])) for f in data.get("files", []))
        return violations, None
    except (json.JSONDecodeError, KeyError):
        pass

    # Fallback: contar linhas com .java: (formato texto)
    count = sum(1 for line in result.stdout.splitlines() if ".java:" in line)
    return count, None


def _has_class_declaration(code: str) -> bool:
    return bool(re.search(r"\b(class|interface|enum)\s+\w+", code))


# Helpers
def _calc_srr(before: int, after: int) -> float:
    return max(0.0, (before - after) / before)


def _ruleset_exists(ruleset: str) -> bool:
    if ruleset.startswith("category/") or ruleset.startswith("rulesets/"):
        return True
    return os.path.exists(ruleset)


def _threshold_note(smell_type: str) -> str:
    notes = {
        "Long Parameter List":          "threshold=4 params",
        "Long Method":                  "threshold=12 NCSS statements",
        "Long Method / Duplicate Code": "threshold=12 NCSS statements",
        "Switch Statement":             "threshold=CC 4 (switch with 3+ cases)",
        "Complex Method":               "threshold=CC 4",
        "God Class":                    "proxy: CyclomaticComplexity classReportLevel=40",
        "Magic Number":                 "XPath: NumericLiteral inside IfStatement (excludes 0, 1, -1, 2)",
        "Dead Code":                    "unused private methods only (UnusedPrivateMethod)",
        "Improper Naming":              "ClassNamingConventions + MethodNamingConventions + FieldNamingConventions",
        "Large Class":                  "NcssCount classReportLevel=40",
    }
    return notes.get(smell_type, "")


def _find_pmd() -> Optional[str]:
    configured = CONFIG.get("pmd_path")
    if configured and os.path.exists(configured):
        return configured
    for name in ["pmd", "pmd.sh"]:
        if shutil.which(name):
            return name
    for p in ["/opt/pmd/bin/pmd", os.path.expanduser("~/pmd/bin/pmd")]:
        if os.path.exists(p):
            return p
    return None