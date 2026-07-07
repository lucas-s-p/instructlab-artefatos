"""
Dataset de casos de teste — smells com suporte PMD confiável.

Critério de inclusão: a regra PMD deve produzir sinal limpo antes→depois.
"Sinal limpo" = viola no código smelly, não viola (ou viola menos) após boa refatoração.

Fontes:
  Refactoring-master — repositório real smelly→refactored
  DACOS — Sharma et al. (2023) arXiv:2303.08729 [ADAPTED]
  MLCQ  — Madeyski & Lewowski (2020) EASE'20 [ADAPTED]
"""

import yaml
from pathlib import Path
from smell_eval.config import TestCase

BASE_DIR = Path(__file__).parent.resolve()


def carregar_casos_smell(nome_pasta: str) -> list[tuple[str, str]]:
    """
    Busca pares before*/after*.
    Cada subpasta (01/, 02/, ...) vira um TestCase separado.
    """
    pasta_smell = BASE_DIR / nome_pasta
    if not pasta_smell.exists():
        print(f"⚠️  [Aviso] Pasta não encontrada: {pasta_smell}")
        return []

    subpastas = sorted({arq.parent for arq in pasta_smell.rglob("before*.java")})
    if not subpastas:
        print(f"⚠️  [Aviso] Nenhum arquivo 'before*.java' encontrado em: {pasta_smell}")
        return []

    casos = []
    for subpasta in subpastas:
        befores = sorted(subpasta.glob("before*.java"))
        afters  = sorted(subpasta.glob("after*.java"))
        if befores and afters:
            inp = befores[0].read_text(encoding="utf-8")
            exp = afters[0].read_text(encoding="utf-8")
            casos.append((inp, exp))
        else:
            print(f"⚠️  [Aviso] Par incompleto em: {subpasta} — before={len(befores)} after={len(afters)}")

    return casos


# Mapeamento smell_type 
MAPEAMENTO_PASTAS: dict[str, str] = {
    "Long Parameter List": "long_parameter_list",
    "Long Method":         "long_method",
    "Magic Number":        "magic_numer",
    "Dead Code":           "dead_code",
    "Switch Statement":    "switch_statement",
    "Complex Method":      "complex_method",
    "Improper Naming":     "improper_naming",
    "Large Class":         "large_class",
    "God Class":           "god_class",
}

# smell_types 
SMELLS: list[str] = [
    "Long Parameter List",
    "Long Method",
    "Magic Number",
    "Dead Code",
    "Switch Statement",
    "Complex Method",
    "Improper Naming",
    "Large Class",
    "God Class",
]


def _montar_dataset() -> list[dict]:
    dataset = []
    for smell in SMELLS:
        nome_pasta = MAPEAMENTO_PASTAS.get(smell, "")
        casos = carregar_casos_smell(nome_pasta) if nome_pasta else []

        if not casos:
            print(f"⚠️  Nenhum caso encontrado para smell: '{smell}'")
            continue

        total = len(casos)
        for i, (inp, exp) in enumerate(casos, start=1):
            dataset.append({
                "source":      f"{smell} — example {i} of {total}",
                "smell_type":  smell,
                "description": f"{smell} (case {i} of {total})",
                "input":       inp,
                "expected":    exp,
            })

    return dataset


DATASET: list[dict] = _montar_dataset()


def load_test_cases(yaml_path: str | None) -> list[TestCase]:
    if yaml_path and Path(yaml_path).exists():
        return _from_yaml(yaml_path)

    smell_types = sorted({tc["smell_type"] for tc in DATASET})
    print(
        f"[dados] Dataset dinâmico carregado — "
        f"{len(DATASET)} casos, {len(smell_types)} smells: {', '.join(smell_types)}"
    )
    return [
        TestCase(
            smell_type=tc["smell_type"],
            description=tc["description"],
            input_code=tc["input"],
            expected_output=tc["expected"],
            source=tc.get("source", ""),
        )
        for tc in DATASET
    ]


def _from_yaml(path: str) -> list[TestCase]:
    print(f"[dados] Carregando: {path}")
    with open(path) as f:
        data = yaml.safe_load(f)

    items = data if isinstance(data, list) else data.get("seed_examples", [])
    cases = [
        TestCase(
            smell_type=item.get("smell_type", "Long Parameter List"),
            description=f"Case {i + 1}",
            input_code=item.get("question", item.get("input", "")),
            expected_output=item.get("answer", item.get("output", "")),
            source="User-provided YAML",
        )
        for i, item in enumerate(items)
        if item.get("question") or item.get("input")
    ]
    print(f"  {len(cases)} cases loaded")
    return cases