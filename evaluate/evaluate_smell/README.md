# Avaliação de Refatoração de Code Smell

Pipeline de avaliação em 5 camadas para comparar **modelo base vs. fine-tuned**
na tarefa de refatoração de code smells Java.

---

## Instalação

```bash
# 1. Dependências Python
pip install -r requirements.txt

# 2. Baixar dados NLTK 
python3 -c "import nltk; nltk.download('punkt')"

# 3. JDK 
sudo apt install default-jdk        # Ubuntu/Debian
sudo dnf install java-21-openjdk-devel  # Fedora
brew install openjdk                # macOS

# 4. PMD (Camada 4 — remoção do smell)
# Baixe em https://github.com/pmd/pmd/releases
# Descompacte e configure em smell_eval/config.py:
#   "pmd_path": "/caminho/para/pmd/bin/pmd"
```

---

## Configuração dos modelos

Edite `smell_eval/config.py`:
```python
"base_model_path":      "~/.local/share/instructlab/checkpoints/hf_format/samples_0",
"finetuned_model_path": "~/.local/share/instructlab/checkpoints/hf_format/samples_last",
```

---

## Uso

```bash
python evaluate.py

# Mais rápido: pula pass@k (L5)
python evaluate.py --skip-passk
```

---

## Estrutura

```
evaluate.py                      
requirements.txt
README.md
pmd_rules/
  long-parameter-list.xml         
  long-method.xml                 
  switch-complexity.xml          
  god-class.xml                  
  improper-naming.xml                 
  large-class.xml                 
smell_eval/
  config.py                       
  code_extractor.py               
  preflight.py                
  data/
    dataset.py                   
  layers/
    layer1_bleu.py                 
    layer2_compilation.py          
    layer3_prr.py               
    layer4_pmd.py             
    layer5_passk.py                
  models/
    inference.py                   
  report/
    builder.py                    
```

---

## Camadas de avaliação

| Camada | Métrica | O que mede |
|--------|---------|-----------|
| L1 | BLEU-4 | Similaridade lexical código gerado vs ground truth | 
| L2 | Compilation Rate | Código gerado sintaticamente válido |
| L3 | Parameter Reduction Rate | Redução de parâmetros — apenas LPL/PO/DC | 
| L4 | SRR via PMD | Smell removido segundo regra PMD calibrada | 
| L5 | pass@k (k=1,3,5) | Corretude com múltiplas tentativas | 


## Dataset embutido


---


