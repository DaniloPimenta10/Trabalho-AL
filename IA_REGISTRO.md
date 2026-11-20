# Registro de Uso de Inteligência Artificial (`IA_REGISTRO.md`)

Este documento registra o histórico de interações e o suporte de ferramentas de Inteligência Artificial utilizadas no desenvolvimento das etapas do trabalho, conforme as diretrizes da disciplina.

---

## Etapa 1: Aquisição e Congelamento de Dados

### 1. Script de Download Automatizado (`src/download.py`)
* **Ferramenta / Modelo:** Gemini (Google)
* **Data:** 2026-11-18
* **Descrição do Uso:** Assistência na estruturação do código em Python utilizando `requests` e `pandas` para consultar a API do IBGE (municípios do Espírito Santo), iterar sobre os geocodes para buscar as séries históricas de dengue no InfoDengue (2015–2025), salvar os arquivos brutos em `data/raw/` e calcular os hashes SHA-256 para a geração automática do manifesto (`data/MANIFEST.txt`).
* **Trechos afetados:** Estrutura completa do script `src/download.py`.

### 2. Script de Auditoria — Etapa 1 (`src/etapa01.py`)
- **Ferramenta / Modelo:** Gemini (Google)
- **Data:** 2026-11-20
- **Descrição do Uso:** Apoio na organização dos caminhos relativos via `pathlib`, leitura iterativa do `data/MANIFEST.txt` e dos CSVs em `data/raw/` com `pandas`, diagnóstico de ambiente no Windows (PEP 668 no `uv` e bloqueio de DLL do `pandas` no Python 3.15 até a adoção do `.venv-312`), discussão da lógica para semanas observadas (`set` em `SE`), duplicatas, semanas esperadas (`data_iniSE` em intervalos de 7 dias), transições válidas em ordem cronológica e estruturação da saída em lista de dicionários para `results/e1_auditoria.csv`.
- **Trechos afetados:** Função `criar_tabela()`, leitura do manifesto/CSV e lógica de cálculo/consolidação das métricas em `src/etapa01.py`.