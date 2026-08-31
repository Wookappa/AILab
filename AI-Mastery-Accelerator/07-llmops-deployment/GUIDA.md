# Guida completa: LLMOps, evaluation e deploy

## 1. Che cosa significa LLMOps

**LLMOps** applica pratiche di engineering e operations al ciclo di vita di sistemi
con Large Language Model:

```text
dataset -> esperimento -> eval -> release -> monitor -> feedback -> dataset
```

Rispetto al software deterministico, output e qualità dipendono da modello, prompt,
contesto, retrieval, tool e variabilità. Rispetto a MLOps classico, provider e modelli
possono cambiare senza retraining locale e il costo è spesso per token.

## 2. Unità di versione

Una release AI include:

```text
application commit
model provider + model version
prompt/template version
generation parameters
tool schemas
graph version
retrieval configuration
knowledge index version
eval dataset version
evaluator version
```

Dire "modello X ha ottenuto 85%" non è riproducibile senza il resto.

## 3. Piramide di verifica

1. **unit test:** funzioni deterministiche, parser, policy, routing;
2. **contract test:** provider, tool, schema e adapter;
3. **component eval:** retrieval, classificazione, structured output;
4. **end-to-end eval:** task completo;
5. **safety eval:** injection, leakage, abuso e permessi;
6. **load/resilience test:** carico e dipendenze degradate;
7. **online measurement:** comportamento reale e outcome prodotto.

I livelli bassi sono rapidi e localizzano errori. Gli end-to-end danno fiducia
complessiva ma spiegano meno la causa.

## 4. Dataset di evaluation

Ogni caso contiene:

- input e contesto;
- segmento;
- output/rubrica attesi;
- evidenze richieste;
- elementi vietati;
- answerable/unanswerable;
- severità del fallimento;
- provenienza e reviewer.

Costruisci il dataset da requisiti, log redatti, incidenti e casi sintetici revisionati.
Separa:

- **development set:** usato durante iterazione;
- **test set bloccato:** usato per release;
- **challenge set:** avversariale;
- **canary set:** pochi casi eseguiti continuamente.

Evitare la **contaminazione** significa non ottimizzare direttamente sul test fino a
memorizzarne i casi.

## 5. Evaluator

Tipi:

- match esatto o schema validity;
- regole deterministiche;
- confronto con reference;
- retrieval metrics;
- modello giudice con rubrica;
- review umana;
- outcome reale.

Una rubrica utile definisce livelli osservabili:

```text
2 = risposta corretta, completa e supportata dalle fonti
1 = parzialmente corretta, nessuna affermazione pericolosa
0 = errata, non supportata o viola un vincolo
```

Per LLM-as-judge:

- nascondi quale output è candidato/baseline;
- randomizza ordine nel pairwise comparison;
- richiedi evidenze;
- misura accordo con revisori umani;
- versiona prompt e modello giudice.

## 6. Variabilità e significatività

Non concludere da due punti percentuali su dieci esempi. Riporta:

- numero casi;
- differenza assoluta;
- risultati per segmento;
- più run se il comportamento varia;
- intervallo di confidenza o bootstrap;
- regressioni critiche anche se la media sale.

Il **bootstrap** ricampiona con sostituzione i casi per stimare la variabilità della
metrica. Non corregge un dataset non rappresentativo.

## 7. Quality gate

Esempio logico:

```python
def release_allowed(candidate: Metrics, baseline: Metrics) -> bool:
    return (
        candidate.task_success >= baseline.task_success - 0.01
        and candidate.critical_violations == 0
        and candidate.p95_ms <= baseline.p95_ms * 1.10
        and candidate.cost_per_request <= MAX_COST
    )
```

Le soglie dipendono dal rischio. Un guardrail sicurezza può essere zero-tolerance;
una metrica rumorosa richiede margine statistico e review.

## 8. API serving

Contratto esempio:

```json
POST /v1/answers
{
  "question": "...",
  "conversation_id": "...",
  "mode": "accurate"
}
```

Risposta:

```json
{
  "request_id": "...",
  "answer": "...",
  "citations": [{"source_id": "...", "uri": "..."}],
  "status": "answered",
  "model_version": "...",
  "index_version": "..."
}
```

Versiona l'API indipendentemente dal modello. Limita input, valida schema, autentica
utente e deriva tenant dal token.

## 9. Timeout e budget

Se l'SLO totale è 5 secondi, non assegnare 5 secondi a ogni dipendenza sequenziale.
Definisci budget:

```text
auth          100 ms
query/embed   400 ms
retrieval     500 ms
rerank        700 ms
generation  2800 ms
overhead      500 ms
```

I numeri sono esempio, non standard. Propaga deadline per evitare lavoro inutile dopo
che il client ha rinunciato.

## 10. Resilienza

- **retry:** ripete errore transitorio con limite/backoff/jitter;
- **circuit breaker:** interrompe chiamate a dipendenza che fallisce ripetutamente;
- **bulkhead:** separa risorse per evitare che un workload saturi tutto;
- **backpressure:** rallenta/rifiuta nuovo lavoro quando la capacità è piena;
- **rate limit:** quota per intervallo;
- **fallback:** comportamento alternativo esplicito e semanticamente valido;
- **dead-letter queue:** conserva job asincroni falliti per analisi/replay.

Un fallback non deve fingere successo. Se il RAG è indisponibile, una risposta del
solo LLM può essere pericolosa; spesso è meglio dichiarare indisponibilità.

## 11. Caching

Livelli:

- embedding cache per testo invariato;
- retrieval cache per query+tenant+index version;
- prompt prefix cache del provider;
- response cache per richieste deterministiche;
- tool cache per dati con TTL.

**TTL (Time To Live)** è la durata di validità. La cache key deve includere ogni
variabile che cambia il risultato: tenant, permessi, modello, prompt e indice.
Non condividere cache fra utenti se l'output contiene dati autorizzati diversamente.

## 12. Streaming

Lo streaming riduce **TTFT (Time To First Token)** percepito, non necessariamente la
durata totale. Problemi:

- errore dopo aver inviato parte della risposta;
- citazioni disponibili solo alla fine;
- moderazione e validazione incomplete;
- client disconnesso ma backend continua.

Progetta protocollo eventi (`start`, `token`, `citation`, `error`, `done`) e
cancellazione.

## 13. Osservabilità

Tre segnali:

- **log:** eventi discreti con contesto;
- **metric:** serie numerica aggregabile;
- **trace:** percorso di una richiesta fra componenti.

Usa OpenTelemetry per correlation fra API, graph, retrieval e tool.
Per eseguire l'esempio installa `pip install -e ".[ops]"`.

```python
from opentelemetry import trace

tracer = trace.get_tracer("ai_ops.answer_service")

async def traced_generation(model, messages, *, prompt_version: str):
    with tracer.start_as_current_span("llm.generate") as span:
        span.set_attribute("gen_ai.system", "configured-provider")
        span.set_attribute("gen_ai.request.model", model.model_name)
        span.set_attribute("app.prompt.version", prompt_version)
        result = await model.ainvoke(messages)
        span.set_attribute("gen_ai.usage.input_tokens", result.usage_metadata["input_tokens"])
        span.set_attribute("gen_ai.usage.output_tokens", result.usage_metadata["output_tokens"])
        return result
```

Non inserire prompt/output negli attributi per default. LangSmith e Langfuse offrono
tracing specializzato LLM; OpenTelemetry resta utile per collegarlo a API, database e
infrastruttura. Valuta privacy, self-hosting, costo e lock-in.

Attributi:

```text
request_id, tenant_bucket, release_version
model, prompt_version, index_version
node/tool, status, duration
input/output tokens, estimated cost
retrieved chunk IDs, citation IDs
error_code, retry_count
```

Non usare testo del prompt come label di metrica: crea cardinalità enorme e leakage.

## 14. SLI, SLO e error budget

- **SLI (Service Level Indicator):** misura, per esempio percentuale risposte valide;
- **SLO (Objective):** target, per esempio 99,5% in 30 giorni;
- **SLA:** accordo contrattuale con conseguenze;
- **error budget:** quota di fallimenti ammessa dallo SLO.

Se il budget viene consumato troppo velocemente, sospendi release rischiose e investi
in affidabilità. Qualità semantica e disponibilità tecnica richiedono SLI distinti.

## 15. Deployment

- **rolling:** sostituisce gradualmente istanze;
- **blue/green:** due ambienti, switch del traffico;
- **canary:** nuova release a piccola percentuale;
- **shadow:** copia traffico alla candidata senza usare la risposta;
- **A/B test:** confronta impatto prodotto su gruppi randomizzati.

Canary protegge metriche operative; per qualità rara servono anche eval offline e
review. Modello, prompt e indice devono poter essere rollbackati indipendentemente.

## 16. Docker e supply chain

- immagini minime e non-root;
- dipendenze bloccate e SBOM;
- scan CVE;
- artifact firmati;
- secret solo runtime;
- health check;
- graceful shutdown;
- digest immutabile in deploy.

**SBOM (Software Bill of Materials)** elenca componenti e versioni. **CVE** identifica
vulnerabilità pubbliche note.

## 17. AWS serving

ECS/Fargate è sufficiente per molti servizi:

```text
ALB -> ECS service -> provider/vector DB
             |
             +-> CloudWatch / OpenTelemetry
             +-> Secrets Manager
             +-> SQS worker per job async
```

- **ALB:** load balancer HTTP;
- **SQS:** coda gestita;
- autoscaling su CPU, memoria, richieste o queue depth;
- task role IAM con permessi minimi;
- availability zone multiple se richiesto dallo SLO.

## 18. Capacity e costo

Approssima:

```text
concurrency ≈ requests_per_second * average_duration_seconds
```

Se 10 richieste/s durano mediamente 3 s, circa 30 sono contemporanee, prima di
considerare burst. Dimensiona semaphore, connection pool e quote provider.

Costo mensile:

```text
richieste * costo medio modello
+ compute
+ storage/index
+ observability
+ traffico
+ costo umano di review/incidenti
```

Misura per feature o tenant per evitare che la media nasconda outlier.

## 19. Incident response

Runbook:

1. rileva e assegna severity;
2. limita impatto: disabilita tool, rollback prompt/modello/indice;
3. conserva trace e versioni;
4. comunica stato;
5. correggi;
6. verifica recovery;
7. postmortem senza colpe con action owner.

Esempi: leakage fra tenant, hallucination pericolosa, costo anomalo, provider down,
indice stale, loop agente.

## 20. Laboratorio e soluzione

Porta RAG/agente dietro FastAPI:

1. endpoint versionato e auth fake;
2. deadline, semaphore e rate limit;
3. trace per ogni step;
4. eval CLI con baseline/candidate;
5. load test e fault injection;
6. Docker non-root;
7. canary simulato;
8. dashboard SLI/SLO/costo;
9. rollback separato di app, modello e indice.

La soluzione è pronta se:

- CI blocca regressioni definite;
- errori hanno codici e non risposte vuote;
- richiesta cancellata interrompe lavoro;
- cache rispetta tenant e versione;
- overload produce 429/503 controllato;
- trace ricostruisce la latenza;
- alert ha owner e runbook;
- rollback è stato eseguito, non solo descritto.

Continua con il [laboratorio Infrastructure as Code](INFRA.md) per container, IAM ed
ECS/Fargate.
