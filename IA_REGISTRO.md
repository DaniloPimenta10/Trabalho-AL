# Registro de Uso de Inteligência Artificial (`IA_REGISTRO.md`)

Este documento registra o histórico de interações e o suporte de ferramentas de Inteligência Artificial utilizadas no desenvolvimento das etapas do trabalho, conforme as diretrizes da disciplina.

---

## Etapa 1: Aquisição e Congelamento de Dados

### 1. Script de Download Automatizado (`src/download.py`)
* **Ferramenta / Modelo:** Gemini (Google)
* **Data:** 2026-11-18
* **Descrição do Uso:** Assistência na estruturação do código em Python utilizando `requests` e `pandas` para consultar a API do IBGE (municípios do Espírito Santo), iterar sobre os geocodes para buscar as séries históricas de dengue no InfoDengue (2015–2025), salvar os arquivos brutos em `data/raw/` e calcular os hashes SHA-256 para a geração automática do manifesto (`data/MANIFEST.txt`).
* **Trechos afetados:** Estrutura completa do script `src/download.py`.