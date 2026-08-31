# 09 - Colloquio, system design e piano di mastery

## Risposte che devi saper dare

### Python

- differenza fra processi, thread e asyncio;
- Protocol vs inheritance;
- iteratori e generatori per dataset grandi;
- timeout, retry, cancellation e context manager;
- progettazione testabile senza mockare tutto;
- profiling CPU, memoria e I/O.

### ML

- scegliere split e metriche;
- diagnosticare leakage, overfitting e drift;
- calibrare probabilità e threshold;
- riproducibilità del training;
- differenze batch, online e streaming inference;
- rollout, monitoring e rollback di un modello.

### LLM/RAG

- RAG vs fine-tuning vs tool calling;
- chunking e retrieval ibrido;
- golden set e metriche per retrieval/generation;
- hallucination, injection e data leakage;
- caching, latenza, token e costi;
- valutare un cambio di modello.

### Agenti

- workflow deterministico vs agente;
- stato, checkpoint e idempotenza;
- tool authorization e human-in-the-loop;
- stop condition e budget;
- test di traiettorie;
- ragioni per evitare multi-agent.

### Data platform e MCP

- idempotenza, backfill, schema evolution e data contracts;
- dbt model/test/lineage e incremental model;
- dlt per ingestion e Airflow per orchestrazione;
- micro-partitioning, warehouse e access control in Snowflake;
- host/client/server, resource e tool MCP;
- propagazione identità, autorizzazione e audit;
- Docker, IAM, ECS/Fargate, secrets e observability su AWS.

## Traccia di system design: support assistant

In 45 minuti:

1. chiarisci utenti, volume, dati, SLO e rischio;
2. definisci baseline e non-obiettivi;
3. disegna ingestion, retrieval, orchestration e serving;
4. approfondisci due componenti critici;
5. tratta eval, sicurezza, observability e costo;
6. descrivi failure mode, degradation e rollback;
7. spiega evoluzione da MVP a 100x traffico.

Evita di iniziare con il nome di un framework. Parti dai requisiti e giustifica ogni
componente.

## Domande pratiche

1. Recall@5 sale ma la qualità finale scende: quali ipotesi verifichi?
2. Il p95 raddoppia senza aumento del traffico: come isoli la causa?
3. Un agente crea due ticket dopo un retry: qual è il difetto progettuale?
4. Le metriche offline migliorano ma gli utenti no: cosa manca?
5. Come impedisci a un documento indicizzato di comandare l'agente?
6. Come migri embedding senza downtime?
7. Quando useresti un modello locale?
8. Come stabilisci se il fine-tuning vale il costo?

Per ogni risposta usa: **ipotesi, misura, decisione, trade-off**.

## Mock interview

Registra tre sessioni:

- 45 minuti coding Python;
- 45 minuti ML/LLM system design;
- 30 minuti deep dive sul capstone.

Riascolta e assegna 0-2 a chiarezza, correttezza, metriche, failure mode e trade-off.
Target: almeno 8/10 per tre simulazioni consecutive.

## Piano dopo il bootcamp

Per trasformare conoscenza in seniority:

- mesi 1-3: porta il capstone a utenti reali e gestisci incidenti;
- mesi 4-6: contribuisci a una libreria AI o pubblica benchmark riproducibili;
- mesi 7-12: guida una decisione architetturale, misura impatto e mantieni il servizio;
- continuo: leggi paper selezionati, ma implementa e valuta prima di aggiungere tool.

## Scorecard finale

| Competenza | Prova richiesta |
|---|---|
| Python | package strict-typed, async, test e profiling |
| ML | training riproducibile, metriche e drift |
| RAG | golden set, retrieval eval e citazioni |
| Agenti | graph, policy, approval e recovery |
| Data platform | dlt, dbt, Snowflake, Airflow e data-quality gate |
| MCP | server con resource/tool, auth, audit e idempotenza |
| Produzione | Docker/AWS, API, tracing, load test e rollback |
| Comunicazione | ADR, diagramma e demo basata su metriche |

Se manca una prova, non scrivere solo "conosco X": costruisci l'artefatto che la
dimostra.
