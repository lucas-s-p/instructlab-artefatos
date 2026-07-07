"""
Verifica todas as dependências antes de iniciar a avaliação.

Verificações realizadas:
  1. transformers + torch instalados
  2. javac disponível no PATH (Camada 2)
  3. PMD disponível no PATH ou CONFIG['pmd_path'] (Camada 4)
  4. Modelos base e fine-tuned encontrados em disco
  5. PMD sanity check: cada caso do dataset dispara before > 0 (Camada 4)
"""

import os
import shutil
import sys
from smell_eval.config import CONFIG


def check_all(test_cases: list) -> None:
    """
    Executa todas as verificações.
    Recebe test_cases para poder rodar o sanity check do PMD.
    """
    errors = []
    errors += _check_transformers()
    errors += _check_javac()
    errors += _check_pmd()
    errors += _check_models()

    if errors:
        _print_errors(errors)
        sys.exit(1)

    # PMD sanity check
    try:
        from smell_eval.layers.layer4_pmd import validate_all, PmdValidationError
        validate_all(test_cases)
    except PmdValidationError as e:
        print("\n" + "═" * 62)
        print("  PMD SANITY CHECK FAILED")
        print("  Fix the issues below before running evaluation:")
        print("═" * 62)
        print(str(e))
        print("═" * 62)
        sys.exit(1)

    print("[ok] All dependencies verified.\n")


def _print_errors(errors: list) -> None:
    print("\n" + "═" * 62)
    print("  ERROR — fix before continuing:")
    print("═" * 62)
    for e in errors:
        print(f"\n  ✗ {e['tool']}")
        for line in e["fix"].splitlines():
            print(f"    {line}")
    print("\n" + "═" * 62)


def _check_transformers() -> list:
    try:
        import transformers, torch  
        return []
    except ImportError as e:
        return [{"tool": f"transformers/torch ({e})",
                 "fix":  "pip install transformers torch"}]


def _check_javac() -> list:
    if _find_javac():
        return []
    return [{"tool": "javac — JDK not found in PATH",
             "fix":  ("Ubuntu/Debian : sudo apt install default-jdk\n"
                      "Fedora        : sudo dnf install java-21-openjdk-devel\n"
                      "macOS         : brew install openjdk")}]


def _check_pmd() -> list:
    if _find_pmd():
        return []
    return [{"tool": "PMD — binary not found",
             "fix":  ("1. Download from: https://github.com/pmd/pmd/releases\n"
                      "2. Extract and set in smell_eval/config.py:\n"
                      '   "pmd_path": "/path/to/pmd/bin/pmd"')}]


def _check_models() -> list:
    errors = []
    for key, label in [("base_model_path", "base"),
                        ("finetuned_model_path", "fine-tuned")]:
        path = CONFIG[key]
        if not os.path.exists(path):
            errors.append({
                "tool": f"Model '{label}' not found: {path}",
                "fix":  f'Set "{key}" in smell_eval/config.py',
            })
    return errors


def _find_javac() -> str | None:
    if shutil.which("javac"):
        return "javac"
    for p in ["/usr/bin/javac", "/usr/local/bin/javac",
              os.path.expanduser("~/.sdkman/candidates/java/current/bin/javac")]:
        if os.path.exists(p):
            return p
    return None


def _find_pmd() -> str | None:
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