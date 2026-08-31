# AI Mastery Accelerator

Percorso intensivo per acquisire competenze operative da **AI/ML Engineer**: Python
solido, ML fuori dal notebook, RAG, agenti, valutazione e deploy.

> Il corso costruisce competenze e portfolio, ma non sostituisce i "3+ anni" richiesti
> da alcune posizioni. Per rendere credibile il profilo, completa i progetti, pubblicali
> e raccogli metriche, decisioni tecniche e feedback di utenti reali.

## Percorso

| Settimana | Modulo | Risultato |
|---|---|---|
| 0 | [Setup e metodo](00-setup/README.md) | Ambiente riproducibile e baseline |
| 1 | [Python production-grade](01-python-production/README.md) | Package tipizzato, testato e osservabile |
| 2 | [ML end-to-end](02-ml-production/README.md) | Modello con pipeline, metriche e API |
| 3 | [LLM e Transformer](03-llm-foundations/README.md) | Scelte motivate su prompt, modelli e tuning |
| 4 | [RAG](04-rag/README.md) | Retrieval misurabile con citazioni |
| 5 | [Agenti e LangGraph](05-agents/README.md) | Workflow con tool, stato e guardrail |
| 6 | [Data platform e MCP](06-data-platform-mcp/README.md) | Pipeline knowledge-base automatizzata |
| 7 | [LLMOps e deploy](07-llmops-deployment/README.md) | Servizio valutato, monitorato e resiliente |
| 8-9 | [Capstone](08-capstone/README.md) | Progetto da portfolio production-ready |
| Continuo | [Colloquio e mastery](09-interview/README.md) | System design, domande e piano di crescita |

La [matrice di copertura della posizione](JOB-MATCH.md) collega ogni requisito a un
modulo e a una prova concreta da mostrare.

## Ritmo consigliato

Durata: **9 settimane, 8-10 ore/settimana**. Se conosci già data engineering, comprimi
i moduli 2 e 6 in una sola settimana.

1. Leggi teoria e schema: 60-90 minuti.
2. Riscrivi gli esempi senza copiare: 2 ore.
3. Completa gli esercizi: 3-4 ore.
4. Integra il risultato nel capstone: 2 ore.
5. Scrivi un breve ADR: problema, alternative, scelta, metriche.

## Regola di completamento

Un modulo è concluso solo quando:

- il codice parte da zero seguendo il README;
- test, lint e type-check passano;
- hai almeno una metrica e un test per un caso negativo;
- sai spiegare trade-off, failure mode e costo;
- il risultato non dipende da una cella eseguita manualmente.

## Portfolio minimo

Alla fine mostra tre repository o tre componenti ben separati:

1. **ML service**: training riproducibile, tracking, API, drift.
2. **RAG service**: ingestion, retrieval ibrido, eval e citazioni.
3. **Agent workflow**: MCP, tool tipizzati, stato persistente, human approval e tracing.

Ogni progetto deve avere diagramma, quickstart, test, metriche, costi stimati,
limitazioni note e una demo di 3-5 minuti.

## Dipendenze

Gli esempi sono volutamente piccoli. Installa soltanto le dipendenze del laboratorio
che stai eseguendo:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev,ai]"
```

Non inserire chiavi API nel repository: usa variabili d'ambiente o un secret manager.
