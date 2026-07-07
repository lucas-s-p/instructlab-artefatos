"""
Camada 5 — pass@k (k=1, 3, 5).

Gera k saídas para cada caso e verifica se pelo menos uma atende ao critério
de corretude.

pass@k = 1 − C(n−c, k) / C(n, k)

onde n = número total de tentativas, c = tentativas corretas.

Interpretação:
  pass@1 : reprodutibilidade (uma tentativa)
  pass@3 : confiabilidade prática
  pass@5 : capacidade máxima do modelo

Gap entre pass@1 e pass@5:
  Um modelo com pass@5=70% e pass@1=20% consegue refatorar, mas é inconsistente.

Critério de corretude (em cascata):
  1. Compilação (L2) — obrigatório. Falha.
  2. SRR via PMD (L4) — se suportado para o smell E before > 0.
     SRR > 0 : passed=True. SRR = 0 : passed=False.
  3. PRR (L3) — fallback para smells de assinatura (LPL, PO, DC)
     quando PMD não detectou o smell no original.
  4. Somente compilação — para smells sem métrica automática disponível.

Temperatura de geração:
  Inferência principal: temperature=0.1 (determinística)
  pass@k:              temperature_passk=0.7 (diversidade entre amostras)
"""

import math
from typing import Callable

from smell_eval.config import CONFIG, PassKResult
from smell_eval.layers import layer2_compilation, layer3_prr, layer4_pmd
from smell_eval.code_extractor import extract_java_code


# Smells para os quais PRR é fallback válido quando PMD não detecta o smell
_SIGNATURE_SMELLS = {"Long Parameter List", "Primitive Obsession", "Data Clumps"}


def evaluate_passk(
    input_code: str,
    generate_fn: Callable[[str, str, float], str],
    smell_type: str = "Long Parameter List",
    k_values: list[int] | None = None,
) -> PassKResult:
    """
    Gera max(k_values) saídas e calcula pass@k para cada k.

    Argumentos:
        input_code:   código smelly (entrada para o modelo)
        generate_fn:  callable(code, smell_type, temperature)
        smell_type:   tipo do smell sendo avaliado
        k_values:     lista de k a calcular

    Retorna:
        PassKResult com pass@1, pass@3, pass@5 e detalhes por geração.
    """
    if k_values is None:
        k_values = CONFIG.get("pass_k_values", [1, 3, 5])

    n = max(k_values)
    attempts = []
    temp_passk = CONFIG.get("temperature_passk", 0.7)

    print(f"    [pass@k] Generating {n} outputs...")
    for i in range(n):
        output = generate_fn(input_code, smell_type, temp_passk)
        passed, failures = _evaluate_correctness(input_code, output, smell_type)
        entry = {
            "attempt":          i + 1,
            "passed":           passed,
            "raw_output":       output,
            "extracted_output": extract_java_code(output),
        }
        if not passed and failures:
            entry["failures"] = failures
        attempts.append(entry)
        status = "✓" if passed else f"✗ ({', '.join(failures)})"
        print(f"      attempt {i+1}/{n}: {status}")

    correct = sum(1 for a in attempts if a["passed"])

    result = PassKResult(details={"n": n, "correct": correct, "attempts": attempts})
    for k in k_values:
        score = _passk_formula(n, correct, k)
        if k == 1:   result.pass_at_1 = round(score, 4)
        elif k == 3: result.pass_at_3 = round(score, 4)
        elif k == 5: result.pass_at_5 = round(score, 4)

    return result


def _evaluate_correctness(original: str, output: str,
                           smell_type: str) -> tuple[bool, list[str]]:
    """
    Retorna (passed, failures) onde failures é lista de camadas que causaram a
    falha: ["compilation"], ["srr"], ["prr"]. Lista vazia = passed=True.
    """
    # Compilação
    r_compile = layer2_compilation.evaluate(output)
    if not r_compile.passed:
        return False, ["compilation"]

    # SRR via PMD (se suportado)
    r_srr = layer4_pmd.evaluate(original, output, smell_type)
    if r_srr.score >= 0:  # PMD rodou com sucesso (não pulado/erro)
        before = r_srr.details.get("smells_before", 0)
        if before > 0:
            if r_srr.score == 0.0:
                failures = ["srr"]
                # Registra PRR como informação secundária quando SRR falha
                if smell_type in _SIGNATURE_SMELLS:
                    r_prr = layer3_prr.evaluate(original, output, smell_type)
                    if not r_prr.passed:
                        failures.append("prr")
                return False, failures
            # SRR > 0 : smell parcial ou totalmente removido
            return True, []

    # PRR para smells de assinatura (fallback quando PMD não detectou)
    if smell_type in _SIGNATURE_SMELLS:
        r_prr = layer3_prr.evaluate(original, output, smell_type)
        if not r_prr.passed:
            return False, ["prr"]
        return True, []

    # Sem métrica automática disponível - compilação é critério único
    return True, []


def _passk_formula(n: int, c: int, k: int) -> float:
    """
    Usa log-gamma para evitar overflow em combinatórias grandes.
    """
    if n - c < k:
        return 1.0
    if c == 0:
        return 0.0
    return 1.0 - math.exp(_log_comb(n - c, k) - _log_comb(n, k))


def _log_comb(n: int, k: int) -> float:
    if k > n:
        return float("-inf")
    return (math.lgamma(n + 1)
            - math.lgamma(k + 1)
            - math.lgamma(n - k + 1))