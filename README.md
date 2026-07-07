# Artefatos

Este repositório reúne os artefatos produzidos durante os experimentos de especialização de modelos de linguagem para a tarefa de refatoração automática de código Java com *code smells*. Foram especializados dois modelos baseados no **Qwen 2.5 Instruct** e um modelo **Granite 3.3 8B Instruct**.

## Estrutura do repositório

### `dados_sinteticos`

Contém o conjunto de dados sintéticos gerado com o **InstructLab**, utilizando o modelo professor **GPT-4o**. Ao todo, foram geradas **1.440 instâncias**, com o objetivo de ensinar os modelos a identificar e refatorar trechos de código Java contendo *code smells*.

### `evaluate`

Contém a ferramenta de avaliação desenvolvida para os experimentos. A ferramenta é composta por quatro camadas de avaliação principais, que permitem analisar diferentes aspectos da qualidade das refatorações produzidas pelos modelos:

- **Compilação:** verifica se o código refatorado compila corretamente.
- **PRR (Parameter Reduction Rate):** mede a redução de parâmetros após a refatoração.
- **SRR (Smell Removal Rate):** avalia a capacidade do modelo de remover os *code smells* presentes no código.
- **Pass@k:** estima a probabilidade de o modelo gerar pelo menos uma refatoração correta em *k* tentativas.

Em conjunto, essas métricas fornecem uma avaliação consistente do desempenho dos modelos especializados.
