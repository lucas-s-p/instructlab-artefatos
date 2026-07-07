"""
Configuração central e estruturas de dados compartilhadas.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

_HERE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RULES_DIR = os.path.join(_HERE, "pmd_rules")

CONFIG = {
    # Modelos
    "base_model_path":"/home/multiarq/.cache/huggingface/hub/models--ibm-granite--granite-3.3-8b-instruct/snapshots/51dd4bc2ade4059a6bd87649d68aa11e4fb2529b",

    "finetuned_model_path":"/home/multiarq/lucas/MODELOS_ARTIGO_FINETUNING/granite-3.3-8b/hf_format/samples_16",

    # Dataset
    "test_yaml_path": None,  # None → usa dataset embutido

    # PMD
    "pmd_path": "../pmd-bin-7.25.0/bin/pmd",

    # Rulesets por smell
    "pmd_ruleset_lpl":    os.path.join(_RULES_DIR, "long-parameter-list.xml"),
    "pmd_ruleset_method": os.path.join(_RULES_DIR, "long-method.xml"),
    "pmd_ruleset_switch": os.path.join(_RULES_DIR, "switch-complexity.xml"),
    "pmd_ruleset_god":    os.path.join(_RULES_DIR, "god-class.xml"),
    "pmd_ruleset_naming": os.path.join(_RULES_DIR, "improper-naming.xml"),
    "pmd_ruleset_large":  os.path.join(_RULES_DIR, "large-class.xml"),
    "pmd_ruleset_magic": os.path.join(_RULES_DIR, "magic-number.xml"),

    # pass@k
    "pass_k_values": [1, 3, 5],

    # Geração
    "max_new_tokens":     5000,
    "temperature":        0.1,   # inferência principal
    "temperature_passk":  0.7,   # pass@k 
    "do_sample":          True,
    "lang":               "java",

    # Saída
    "output_json": "relatorio_avaliacao.json",
}

# Data Classes
@dataclass
class TestCase:
    smell_type:      str
    description:     str
    input_code:      str
    expected_output: str
    source:          str = ""


@dataclass
class LayerResult:
    """
    Resultado de uma camada de avaliação.
    """
    score:   float
    details: dict           = field(default_factory=dict)
    passed:  Optional[bool] = None


@dataclass
class PassKResult:
    pass_at_1: Optional[float] = None
    pass_at_3: Optional[float] = None
    pass_at_5: Optional[float] = None
    details:   dict            = field(default_factory=dict)


@dataclass
class CaseResult:
    case_index:       int
    smell_type:       str
    description:      str
    source:           str
    input_code:       str   
    expected_output:  str  
    base_output:      str
    finetuned_output: str

    # L1 — BLEU-4
    bleu_base:         Optional[LayerResult] = None
    bleu_finetuned:    Optional[LayerResult] = None

    # L2 — Compilação
    compile_base:      Optional[LayerResult] = None
    compile_finetuned: Optional[LayerResult] = None

    # L3 — PRR (Parameter Reduction Rate)
    prr_base:          Optional[LayerResult] = None
    prr_finetuned:     Optional[LayerResult] = None

    # L4 — SRR via PMD
    srr_base:          Optional[LayerResult] = None
    srr_finetuned:     Optional[LayerResult] = None

    # L5 — pass@k
    passk_base:        Optional[PassKResult] = None
    passk_finetuned:   Optional[PassKResult] = None
