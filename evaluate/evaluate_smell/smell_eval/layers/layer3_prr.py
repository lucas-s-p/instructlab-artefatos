"""
Camada 3 — Parameter Reduction Rate (PRR).

Aplicável para: Long Parameter List, Primitive Obsession, Data Clumps.

Para qualquer outro smell, retorna score=-1 (N/A) 

Conta parâmetros na assinatura do método antes e depois da refatoração
usando regex sobre a declaração.

  PRR = 1 − (params_after / params_before)

PRR = 1.0 : todos os parâmetros encapsulados (0 parâmetros restantes)
PRR = 0.5 : metade dos parâmetros foi encapsulada
PRR = 0.0 : nenhuma mudança
PRR < 0   : o modelo adicionou parâmetros (regressão)

Referências:
  Palomba et al. (2018) "Detecting Bad Smells in Source Code using Change
  History Information". TOSEM.
  Tsantalis et al. (2022) RefactoringMiner 2.0. IEEE TSE.
"""

import re
from smell_eval.config import LayerResult
from smell_eval.code_extractor import extract_java_code

# Smells para os quais PRR tem suporte
_PRR_APPLICABLE = {"Long Parameter List", "Primitive Obsession", "Data Clumps"}

# Regex para capturar a lista de parâmetros da primeira assinatura de método
_METHOD_SIG = re.compile(
    r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\(([^)]*)\)",
    re.MULTILINE,
)


def evaluate(original: str, refactored: str,
             smell_type: str = "Long Parameter List") -> LayerResult:
    """
    Calcula PRR comparando o número de parâmetros antes e depois.

    Args:
        original:   código smelly original
        refactored: output do modelo
        smell_type: tipo do smell

    Returns:
        LayerResult com score=-1 se smell_type não for aplicável.
    """
    if smell_type not in _PRR_APPLICABLE:
        return LayerResult(
            score=-1.0,
            passed=None,
            details={
                "skipped": True,
                "reason":  (
                    f"PRR not applicable for '{smell_type}'. "
                    f"Applicable only for: {sorted(_PRR_APPLICABLE)}."
                ),
            },
        )

    clean_refactored = extract_java_code(refactored)

    params_before = _count_params(original)
    params_after  = _count_params(clean_refactored)

    if params_before <= 0:
        return LayerResult(
            score=0.0,
            details={"error": "could not detect parameters in original code"},
            passed=None,
        )

    if params_after < 0:
        return LayerResult(
            score=0.0,
            details={"error": "could not detect parameters in model output"},
            passed=False,
        )

    prr = 1.0 - (params_after / params_before)
    improved = params_after < params_before

    return LayerResult(
        score=round(prr, 4),
        details={
            "params_before": params_before,
            "params_after":  params_after,
            "prr":           round(prr, 4),
            "improved":      improved,
        },
        passed=improved,
    )


def _count_params(code: str) -> int:
    """
    Conta parâmetros da primeira assinatura de método encontrada.
    Retorna -1 se não encontrar nenhuma assinatura.
    """
    match = _METHOD_SIG.search(code)
    if not match:
        return -1
    param_str = match.group(1).strip()
    if not param_str:
        return 0
    # Conta vírgulas de primeiro nível (ignora generics aninhados)
    depth  = 0
    commas = 0
    for ch in param_str:
        if ch in "<(":
            depth += 1
        elif ch in ">)":
            depth -= 1
        elif ch == "," and depth == 0:
            commas += 1
    return commas + 1