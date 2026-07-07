#!/usr/bin/env python3
"""
parse_eval_log.py
Lê o arquivo de log de avaliação (copia_eval.log ou evaluate.log) e calcula:
  - Médias por smell (L1-BLEU, L2-Compilation, L3-PRR, L4-SRR, L5-pass@1, L5-pass@5)
  - Média geral de todos os casos

Estrutura do dicionário de saída:
  results[smell_name] = {
      "base": {"L1": [...], "L2": [...], "L3": [...], "L4": [...], "pass@1": [...], "pass@5": [...]},
      "ft":   {"L1": [...], "L2": [...], "L3": [...], "L4": [...], "pass@1": [...], "pass@5": [...]},
  }
"""

import re
import sys
import json
from collections import defaultdict

# ─── Config ──────────────────────────────────────────────────────────────────

SMELLS = [
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

LOG_FILE = sys.argv[1] if len(sys.argv) > 1 else "evaluate.log"

# ─── Regex patterns ───────────────────────────────────────────────────────────

# Linha com métricas L1-L4:
# → L1 bleu  base=0.5379 ft=0.5880 | L2 compilation base=1.0000 ft=1.0000 | ...
RE_L1_L4 = re.compile(
    r"L1 bleu\s+base=([\d.]+|N/A)\s+ft=([\d.]+|N/A)"
    r".*?L2 compilation\s+base=([\d.]+|N/A)\s+ft=([\d.]+|N/A)"
    r".*?L3 prr\s+base=([\d.]+|N/A)\s+ft=([\d.]+|N/A)"
    r".*?L4 srr\s+base=([\d.]+|N/A)\s+ft=([\d.]+|N/A)",
    re.IGNORECASE,
)

# Linha com métricas L5:
# L5 pass@1 base=0.2000 ft=1.0000 | pass@5 base=1.0000 ft=1.0000
RE_L5 = re.compile(
    r"L5 pass@1\s+base=([\d.]+|N/A)\s+ft=([\d.]+|N/A)"
    r".*?pass@5\s+base=([\d.]+|N/A)\s+ft=([\d.]+|N/A)",
    re.IGNORECASE,
)

# Cabeçalho de caso:
# [case 1/36] Long Parameter List: Long Parameter List (case 1 of 2)
RE_CASE = re.compile(r"\[case\s+\d+/\d+\]\s+(.+?):", re.IGNORECASE)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def to_float(s):
    """Converte string para float, retorna None se 'N/A'."""
    return None if s.upper() == "N/A" else float(s)


def avg(lst):
    """Média ignorando valores None."""
    vals = [v for v in lst if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


# ─── Parse ───────────────────────────────────────────────────────────────────

def parse_log(path):
    """
    Retorna:
      results[smell] = {
          "base": {"L1":[], "L2":[], "L3":[], "L4":[], "pass@1":[], "pass@5":[]},
          "ft":   {"L1":[], "L2":[], "L3":[], "L4":[], "pass@1":[], "pass@5":[]},
          "cases": int
      }
    """
    results = {}
    for smell in SMELLS:
        results[smell] = {
            "base": defaultdict(list),
            "ft":   defaultdict(list),
            "cases": 0,
        }

    current_smell = None

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {path}")
        sys.exit(1)

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detecta novo caso e smell
        m_case = RE_CASE.search(line)
        if m_case:
            detected = m_case.group(1).strip()
            # Mapeia para smell canonical
            current_smell = None
            for smell in SMELLS:
                if smell.lower() in detected.lower():
                    current_smell = smell
                    break
            if current_smell is None:
                print(f"[WARN] Smell não reconhecido: '{detected}' — ignorando caso")
            i += 1
            continue

        # Detecta linha de métricas L1-L4
        m_l1l4 = RE_L1_L4.search(line)
        if m_l1l4 and current_smell:
            b_l1, f_l1, b_l2, f_l2, b_l3, f_l3, b_l4, f_l4 = m_l1l4.groups()

            results[current_smell]["base"]["L1"].append(to_float(b_l1))
            results[current_smell]["ft"]["L1"].append(to_float(f_l1))
            results[current_smell]["base"]["L2"].append(to_float(b_l2))
            results[current_smell]["ft"]["L2"].append(to_float(f_l2))
            results[current_smell]["base"]["L3"].append(to_float(b_l3))
            results[current_smell]["ft"]["L3"].append(to_float(f_l3))
            results[current_smell]["base"]["L4"].append(to_float(b_l4))
            results[current_smell]["ft"]["L4"].append(to_float(f_l4))

            # Linha L5 vem logo abaixo (próxima linha não vazia)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                m_l5 = RE_L5.search(lines[j].strip())
                if m_l5:
                    b_p1, f_p1, b_p5, f_p5 = m_l5.groups()
                    results[current_smell]["base"]["pass@1"].append(to_float(b_p1))
                    results[current_smell]["ft"]["pass@1"].append(to_float(f_p1))
                    results[current_smell]["base"]["pass@5"].append(to_float(b_p5))
                    results[current_smell]["ft"]["pass@5"].append(to_float(f_p5))
                    results[current_smell]["cases"] += 1
                    i = j + 1
                    continue

            i += 1
            continue

        i += 1

    return results


# ─── Aggregation ─────────────────────────────────────────────────────────────

METRICS = ["L1", "L2", "L3", "L4", "pass@1", "pass@5"]


def aggregate(results):
    """Calcula médias por smell e geral."""
    summary = {}

    all_base = defaultdict(list)
    all_ft   = defaultdict(list)

    for smell, data in results.items():
        n = data["cases"]
        if n == 0:
            continue

        smell_summary = {"cases": n, "base": {}, "ft": {}}
        for m in METRICS:
            b_vals = data["base"][m]
            f_vals = data["ft"][m]
            smell_summary["base"][m] = {
                "values": b_vals,
                "mean":   avg(b_vals),
            }
            smell_summary["ft"][m] = {
                "values": f_vals,
                "mean":   avg(f_vals),
            }
            all_base[m].extend(b_vals)
            all_ft[m].extend(f_vals)

        summary[smell] = smell_summary

    # Média geral
    total_cases = sum(d["cases"] for d in summary.values())
    overall = {"cases": total_cases, "base": {}, "ft": {}}
    for m in METRICS:
        overall["base"][m] = avg(all_base[m])
        overall["ft"][m]   = avg(all_ft[m])
    summary["__OVERALL__"] = overall

    return summary


# ─── Display ─────────────────────────────────────────────────────────────────

def print_table(summary):
    header = f"{'Smell':<22} {'N':>3}  " + "  ".join(
        f"{'B-' + m:>10} {'FT-' + m:>10}" for m in METRICS
    )
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))

    for smell in SMELLS + ["__OVERALL__"]:
        if smell not in summary:
            continue
        d = summary[smell]
        label = "OVERALL" if smell == "__OVERALL__" else smell
        row = f"{label:<22} {d['cases']:>3}  "
        for m in METRICS:
            if smell == "__OVERALL__":
                b = d["base"][m]
                ft = d["ft"][m]
            else:
                b  = d["base"][m]["mean"]
                ft = d["ft"][m]["mean"]
            b_str  = f"{b:.4f}"  if b  is not None else "  N/A  "
            ft_str = f"{ft:.4f}" if ft is not None else "  N/A  "
            row += f"  {b_str:>10} {ft_str:>10}"
        if smell == "__OVERALL__":
            print("-" * len(header))
        print(row)
    print("=" * len(header))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"[parse_eval_log] Lendo: {LOG_FILE}")
    raw = parse_log(LOG_FILE)
    summary = aggregate(raw)

    # Exibe tabela
    print_table(summary)

    # Salva JSON compacto (sem os arrays de valores individuais — só médias)
    out_compact = {}
    for smell, d in summary.items():
        if smell == "__OVERALL__":
            out_compact[smell] = d
        else:
            out_compact[smell] = {
                "cases": d["cases"],
                "base":  {m: d["base"][m]["mean"] for m in METRICS},
                "ft":    {m: d["ft"][m]["mean"]   for m in METRICS},
            }

    json_path = LOG_FILE.replace(".log", "_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out_compact, f, indent=2, ensure_ascii=False)
    print(f"\n[parse_eval_log] JSON salvo em: {json_path}")

    # Salva JSON completo (com arrays de valores por caso)
    json_full_path = LOG_FILE.replace(".log", "_full.json")
    # Converte defaultdict para dict normal para serializar
    raw_serializable = {}
    for smell, data in raw.items():
        if data["cases"] == 0:
            continue
        raw_serializable[smell] = {
            "cases": data["cases"],
            "base":  {m: data["base"][m] for m in METRICS},
            "ft":    {m: data["ft"][m]   for m in METRICS},
        }
    with open(json_full_path, "w", encoding="utf-8") as f:
        json.dump(raw_serializable, f, indent=2, ensure_ascii=False)
    print(f"[parse_eval_log] JSON completo (valores por caso) salvo em: {json_full_path}")


if __name__ == "__main__":
    main()
