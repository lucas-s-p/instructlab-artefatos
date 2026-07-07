import json
import csv
import re
import time
import urllib.request
from collections import Counter


# Config
JSONL_FILE  = "../../2026-05-26_134109/messages_2026-05-26T13_41_15.jsonl"
OUTPUT_CSV  = "classified.csv"
STATS_FILE  = "classified_stats.txt"

OPENROUTER_API_KEY = "API_KEY"
MODEL              = "google/gemini-2.5-flash"

NOT_FOUND_LABEL = "NOT FOUND"

# True: 1 instância, False: 1440 (dataset completo)
DRY_RUN_ONE = False

SYSTEM_PROMPT = "You are a code smell classifier. Reply only with a JSON object."

USER_PROMPT_TEMPLATE = """\
Below is a question-and-answer exchange about refactoring a Java code snippet.

--- CONVERSATION ---
{conversation}
--- END CONVERSATION ---

Your task is to identify the code smell(s) explicitly mentioned in the explanation provided in the conversation.

Important rules:
- Use only the explanation text as evidence.
- Do NOT infer smells from the source code.
- Do NOT infer smells from the refactored code.
- Only return smells that are explicitly stated or directly described in the explanation.
- If a smell is not mentioned in the explanation, do not include it.
- If no identifiable smell is mentioned in the explanation, return ["{not_found}"].

Return a JSON object with a single key "smells", whose value is a list of smell names in UPPERCASE.

Example:
{{"smells": ["LONG METHOD", "DUPLICATE CODE"]}}
"""

# Texto para processamento
def build_conversation_text(record: dict) -> str:
    parts = []
    for m in record.get("messages", []):
        role = m.get("role", "?").upper()
        content = m.get("content", "")
        parts.append(f"[{role}]\n{content}")
    return "\n\n".join(parts)

# Leitura das instâncias
instances = []
with open(JSONL_FILE, encoding="utf-8") as f:
    for idx, line in enumerate(f, start=1):
        try:
            record = json.loads(line)
        except Exception:
            continue
        conversation = build_conversation_text(record)
        instances.append({"line": idx, "conversation": conversation})

print(f"Total de instâncias: {len(instances)}")

if DRY_RUN_ONE:
    instances = instances[:1]
    print(f"DRY RUN: processando só 1 instância (linha {instances[0]['line']})")
else:
    print(f"Processando {len(instances)} instâncias...")

# Chamada à API
def call_openrouter(conversation: str) -> list[str]:
    prompt = USER_PROMPT_TEMPLATE.format(
        conversation=conversation[:4000],  # trunca para não estourar contexto
        not_found=NOT_FOUND_LABEL,
    )
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0,
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type":  "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    content = data["choices"][0]["message"]["content"].strip()

    # Limpa possíveis ```json ... ``` ao redor
    content = re.sub(r"^```(?:json)?", "", content).strip()
    content = re.sub(r"```$", "", content).strip()

    parsed = json.loads(content)
    smells = parsed.get("smells", [NOT_FOUND_LABEL])

    # normaliza para uppercase/strip
    return [s.strip().upper() for s in smells if s.strip()]

# Processa e salva
results = []
for i, inst in enumerate(instances, start=1):
    conv = inst["conversation"]
    try:
        smells = call_openrouter(conv)
    except Exception as e:
        smells = [f"[ERRO: {e}]"]
    time.sleep(0.5)  # evita rate limit

    results.append({
        "linha": inst["line"],
        "smell": "; ".join(smells),
    })

    print(f"[{i}/{len(instances)}] linha {inst['line']} → {smells}")

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["linha", "smell"])
    writer.writeheader()
    writer.writerows(results)

print(f"\nSalvo em {OUTPUT_CSV}")

# Estatísticas
def analyze_classified_csv(csv_path: str, stats_path: str | None = None) -> Counter:
    counter = Counter()
    total_instances = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total_instances += 1
            smells = [s.strip() for s in row["smell"].split(";") if s.strip()]
            for s in smells:
                counter[s] += 1

    # Monta a tabela como texto
    lines = []
    lines.append(f"Total de instâncias: {total_instances}")
    lines.append(f"Total de smells distintos: {len(counter)}")
    lines.append("")
    lines.append(f"{'SMELL':<30} {'COUNT':>6}")
    lines.append("-" * 38)
    for smell, count in counter.most_common():
        lines.append(f"{smell:<30} {count:>6}")

    table_text = "\n".join(lines)
    print("\n" + table_text)

    if stats_path:
        with open(stats_path, "w", encoding="utf-8") as f:
            f.write(table_text + "\n")
        print(f"\nEstatísticas salvas em {stats_path}")

    return counter


analyze_classified_csv(OUTPUT_CSV, STATS_FILE)