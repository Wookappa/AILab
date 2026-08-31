# AILab

## AI Mastery Accelerator

[![Publish course](https://github.com/wookappa/AILab/actions/workflows/docs.yml/badge.svg)](https://github.com/wookappa/AILab/actions/workflows/docs.yml)

Corso intensivo e pratico per AI/ML Engineer: Python production-grade, ML, computer
vision, LLM, RAG, agenti, MCP, data platform e LLMOps.

**Sito del corso:** <https://wookappa.github.io/AILab/>

## Visualizzazione locale

```powershell
py -3.12 -m venv .venv-docs
.\.venv-docs\Scripts\Activate.ps1
pip install -r requirements-docs.txt
mkdocs serve
```

Apri `http://127.0.0.1:8000`. Il server aggiorna il sito quando modifichi i file.

## Pubblicazione su GitHub Pages

1. Crea un repository GitHub e carica l'intera cartella.
2. Assicurati che il branch principale si chiami `main`.
3. In **Settings > Pages > Build and deployment**, seleziona **GitHub Actions**.
4. Esegui un push su `main`.

Il workflow `.github/workflows/docs.yml` costruisce e pubblica automaticamente il
sito. I contenuti del corso sono in [`AI-Mastery-Accelerator`](AI-Mastery-Accelerator/README.md).
