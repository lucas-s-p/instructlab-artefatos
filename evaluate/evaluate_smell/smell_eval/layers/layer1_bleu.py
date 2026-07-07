"""
Camada 1 — BLEU-4 (similaridade lexical no nível de código).

Calcula BLEU-4 entre o código Java extraído da saída do modelo e o
expected_output do dataset. 

Semântica do score
0.0 : tokens completamente diferentes
1.0 : correspondência lexical perfeita 

Implementação: nltk sentence_bleu com smoothing method1.
O smoothing evita score zero quando alguma ordem de n-gram não tem match —
comum em saídas curtas ou com diferenças estruturais.
"""

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import RegexpTokenizer

from smell_eval.config import LayerResult
from smell_eval.code_extractor import extract_java_code

# Java-aware tokenizer: separates identifiers, symbols, and numbers.
_TOKENIZER = RegexpTokenizer(r"[A-Za-z_]\w*|[^\w\s]|\d+")

_SMOOTH = SmoothingFunction().method1


def _tokenize(code: str) -> list[str]:
    return _TOKENIZER.tokenize(code)


def evaluate(output: str, expected: str) -> LayerResult:
    """
    Argumentos:
        output:   saída bruta do modelo (código extraído internamente)
        expected: código refatorado esperado (ground truth do dataset)

    Retorna:
        LayerResult com score em [0, 1].
        score = -1.0 se hipótese ou referência ficar vazia após extração.
    """
    code_hyp = extract_java_code(output)
    code_ref  = expected.strip()

    if not code_hyp or not code_ref:
        return LayerResult(
            score=-1.0,
            details={"error": "hypothesis or reference empty after code extraction"},
        )

    tokens_hyp = _tokenize(code_hyp)
    tokens_ref = _tokenize(code_ref)

    if not tokens_hyp or not tokens_ref:
        return LayerResult(
            score=-1.0,
            details={"error": "tokenization produced empty sequence"},
        )

    score = sentence_bleu(
        [tokens_ref],
        tokens_hyp,
        weights=(0.25, 0.25, 0.25, 0.25),   # BLEU-4
        smoothing_function=_SMOOTH,
    )
    score = round(float(score), 4)

    return LayerResult(
        score=score,
        details={
            "bleu4":             score,
            "hypothesis_tokens": len(tokens_hyp),
            "reference_tokens":  len(tokens_ref),
            "hypothesis_length": len(code_hyp),
            "reference_length":  len(code_ref),
        },
    )