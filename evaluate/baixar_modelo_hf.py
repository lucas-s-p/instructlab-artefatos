from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # ou "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Salva no disco
tokenizer.save_pretrained("./modelos/tinyllama")
model.save_pretrained("./modelos/tinyllama")