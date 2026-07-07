"""
Model loading and inference.
"""

from pathlib import Path
from typing import Optional

from smell_eval.config import CONFIG


# Single generic prompt — does NOT mention the smell type or suggest a refactoring strategy.
_GENERIC_PROMPT = (
    "Refactor the following Java code. "
    "Return only the refactored Java code, no explanations."
)


def _build_prompt(code: str, smell_type: str) -> str:
    return f"{_GENERIC_PROMPT}\n\n{code.strip()}"


def load_model(model_path: str, label: str, max_memory: dict = None):
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
    except ImportError:
        print("ERROR: install transformers and torch")
        return None, None

    if not Path(model_path).exists():
        return None, None

    print(f"[model] Loading {label}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, dtype=torch.bfloat16, local_files_only=True,
        device_map="auto", max_memory=max_memory,
    )
    model.eval()
    params = sum(p.numel() for p in model.parameters())
    print(f"  OK — {params:,} parameters")
    return tokenizer, model


def run_inference(tokenizer, model, code_input: str,
                  smell_type: str = "Long Parameter List",
                  temperature: float | None = None) -> str:
    import torch

    prompt = _build_prompt(code_input, smell_type)

    try:
        input_text = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False, add_generation_prompt=True,
        )
    except Exception:
        input_text = prompt

    temp = temperature if temperature is not None else CONFIG["temperature"]

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=CONFIG["max_new_tokens"],
            temperature=temp,
            do_sample=CONFIG["do_sample"],
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def models_available(base, finetuned) -> bool:
    return base is not None and finetuned is not None
