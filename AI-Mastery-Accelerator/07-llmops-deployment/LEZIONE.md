# Lezione passo-passo: portare un sistema AI in produzione

## Cosa saprai fare alla fine

Saprai:

1. spiegare che cosa cambia fra demo e produzione;
2. esporre un servizio con FastAPI;
3. distinguere log, metriche e trace;
4. capire latenza, percentili, timeout e limiti;
5. definire SLI, SLO ed error budget;
6. spiegare test, CI/CD, canary e rollback;
7. capire il ruolo di Docker, ECS, Fargate e IAM.

## Cosa devi sapere prima

Completa le lezioni Python, RAG, agenti e data platform. Non serve aver già usato AWS:
partiremo dal servizio locale.

## 1. Demo e produzione

Una demo dimostra che un'idea può funzionare in un caso scelto. Un sistema in
produzione deve funzionare:

- con utenti diversi;
- con input errati;
- quando una dipendenza è lenta;
- sotto richieste concorrenti;
- dopo un riavvio;
- con versioni e costi controllati;
- rispettando permessi e privacy.

```text
demo: funziona una volta sul mio computer
produzione: comportamento misurabile e gestibile nel tempo
```

## 2. Processo, server e API

Un **processo** è un programma in esecuzione.

Un **server** è un processo che resta in ascolto e risponde a richieste.

Una **API**, Application Programming Interface, è il contratto delle richieste e delle
risposte.

Esempio HTTP:

```text
POST /v1/answers
Content-Type: application/json

{"question": "Come richiedo le ferie?"}
```

Risposta:

```json
{
  "answer": "Apri la sezione Ferie.",
  "status": "answered"
}
```

**HTTP** è il protocollo usato da browser e servizi web. `POST` indica una richiesta
che invia dati. `/v1/answers` è il percorso dell'operazione.

## 3. FastAPI

FastAPI è un framework Python per creare API.

Il corso include `src\ai_mastery\production_app.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AI Mastery Example")

class AnswerRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)

class AnswerResponse(BaseModel):
    answer: str
    status: str

@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/v1/answers")
async def answer(request: AnswerRequest) -> AnswerResponse:
    return AnswerResponse(
        answer=f"Ricevuto: {request.question}",
        status="answered",
    )
```

Avvia:

```powershell
uvicorn ai_mastery.production_app:app --reload
```

- `uvicorn` è il server;
- `ai_mastery.production_app` è il modulo;
- `app` è l'oggetto FastAPI;
- `--reload` riavvia durante lo sviluppo, non va usato in produzione.

Apri:

```text
http://127.0.0.1:8000/docs
```

FastAPI mostra una pagina per provare l'API.

## 4. Validazione e codici HTTP

Pydantic rifiuta domande troppo corte. FastAPI restituisce un errore `422`.

Codici comuni:

| Codice | Significato |
|---|---|
| 200 | richiesta riuscita |
| 400 | input semanticamente invalido |
| 401 | identità non verificata |
| 403 | identità valida ma azione vietata |
| 404 | risorsa non trovata |
| 409 | conflitto con stato/idempotenza |
| 429 | troppe richieste |
| 500 | errore interno inatteso |
| 503 | servizio temporaneamente non disponibile |

Non restituire `200` con una stringa vuota quando il provider fallisce: nasconde il
problema al client.

## 5. Richieste concorrenti

Due utenti possono chiamare il servizio nello stesso momento. La **concorrenza** è la
gestione di più lavori che si sovrappongono nel tempo.

Un provider può consentire solo un certo numero di richieste. Una semaphore limita:

```python
import asyncio

provider_slots = asyncio.Semaphore(5)

async def call_provider(prompt: str) -> str:
    async with provider_slots:
        return await provider.generate(prompt)
```

Quando i cinque posti sono occupati, le richieste successive attendono. Serve anche
un limite alla coda: attendere senza limite sposta soltanto il problema sulla latenza.

## 6. Timeout, retry e deadline

Un **timeout** limita quanto attendere una singola operazione.

Un **retry** ripete un errore transitorio, come un breve problema di rete.

Una **deadline** è il limite dell'intera richiesta.

Esempio:

```text
budget totale: 5 secondi
retrieval: massimo 0,8 s
reranking: massimo 0,7 s
LLM: tempo residuo
```

Tre retry da cinque secondi non rispettano un budget di cinque secondi. Ogni retry
deve controllare il tempo residuo.

Non fare retry su:

- credenziale errata;
- permesso negato;
- input invalido;
- errore di dominio permanente.

Una scrittura ritentata deve essere idempotente.

## 7. Log, metriche e trace

### Log

Un **log** è un evento testuale strutturato:

```json
{
  "event": "answer_completed",
  "request_id": "r-123",
  "duration_ms": 820,
  "status": "success"
}
```

Non registrare automaticamente prompt, PII o segreti.

### Metrica

Una **metrica** è un numero aggregabile nel tempo:

```text
requests_total
errors_total
request_duration_seconds
tokens_total
cost_total
```

### Trace

Una **trace** ricostruisce una richiesta attraverso più step:

```text
API 900 ms
  retrieval 120 ms
  reranker 90 ms
  LLM 640 ms
```

Ogni richiesta ha un `request_id` o trace ID per collegare gli eventi.

## 8. Media e percentili

La media può nascondere richieste molto lente.

Il **p95** è il valore sotto cui termina il 95% delle richieste. Se p95 è 4 secondi:

```text
95 richieste su 100 terminano entro 4 secondi
5 possono essere più lente
```

Misura almeno:

- p50: esperienza centrale;
- p95: coda lenta comune;
- p99: casi estremi.

Segmenta per modello, endpoint, tenant e versione senza creare label con valori
illimitati.

## 9. SLI, SLO e SLA

**SLI**, Service Level Indicator, è una misura:

```text
percentuale di richieste valide completate entro 4 secondi
```

**SLO**, Service Level Objective, è l'obiettivo:

```text
99% in una finestra di 30 giorni
```

**SLA**, Service Level Agreement, è un accordo contrattuale con conseguenze.

L'**error budget** è la quota di fallimenti permessa dallo SLO. Se lo consumi troppo
velocemente, rallenti i rilasci e migliori affidabilità.

I valori dipendono dal prodotto: non copiare 99,9% senza calcolare costo e necessità.

## 10. Evaluation prima del deploy

Un sistema AI richiede due famiglie di controllo:

### Test deterministici

```text
parser
validazione
autorizzazione
routing
idempotenza
```

Lo stesso input deve produrre il risultato previsto.

### Eval comportamentali

```text
correttezza
retrieval
citazioni
astensione
tool selection
sicurezza
costo e latenza
```

Il modello può variare, quindi misuriamo distribuzioni e casi, non una stringa identica
per ogni risposta.

## 11. CI/CD

**CI**, Continuous Integration, esegue controlli automatici a ogni modifica:

```text
lint -> type-check -> test -> eval piccola -> build
```

**CD**, Continuous Delivery/Deployment, prepara o pubblica la versione approvata.

Un **quality gate** blocca la release se una metrica critica regredisce.

Esempio:

```text
nessun accesso cross-tenant
task success non peggiore oltre margine concordato
p95 entro budget
costo entro limite
```

## 12. Strategie di rilascio

### Rolling

Sostituisce gradualmente istanze vecchie.

### Blue/green

Mantiene ambiente vecchio e nuovo; il traffico cambia destinazione.

### Canary

Invia una piccola percentuale alla nuova versione. Se metriche peggiorano, interrompe.

### Shadow

Copia richieste alla nuova versione ma non mostra l'output agli utenti. Attenzione:
non deve duplicare azioni di scrittura.

### Rollback

Ritorna a una versione nota. Nei sistemi AI versiona separatamente:

- applicazione;
- modello;
- prompt;
- tool;
- indice.

## 13. Docker

Un'**immagine Docker** contiene applicazione e dipendenze. Un **container** è
un'istanza in esecuzione dell'immagine.

Vantaggi:

- stesso runtime in sviluppo e cloud;
- artifact immutabile;
- dipendenze esplicite;
- avvio ripetibile.

Un container sicuro:

- usa immagine piccola;
- non esegue come root;
- non contiene segreti;
- ha health check;
- gestisce arresto;
- usa versioni fissate.

Docker non risolve automaticamente database, rete, backup o autorizzazione.

## 14. AWS in parole semplici

Per il capstone:

- **ECR:** deposito delle immagini Docker;
- **ECS:** servizio che coordina container;
- **Fargate:** esegue container senza gestire server;
- **ALB:** distribuisce richieste HTTP;
- **S3:** conserva file e artifact;
- **Secrets Manager:** conserva segreti;
- **CloudWatch:** raccoglie log e metriche;
- **IAM:** definisce identità e permessi.

Il task dell'applicazione riceve un ruolo IAM. La policy deve concedere solo le azioni
necessarie, per esempio leggere una cartella S3 precisa.

## 15. Laboratorio guidato

### Passo 1: avvia l'API

```powershell
uvicorn ai_mastery.production_app:app --reload
```

Apri `/docs` e prova una domanda valida.

### Passo 2: prova input invalido

Invia `"x"`. Verifica il codice 422 e leggi il campo segnalato.

### Passo 3: esegui i test

In un altro terminale con `.venv` attivo:

```powershell
python -m pytest tests\test_production_app.py
```

### Passo 4: aggiungi request ID

Genera un identificatore per richiesta, inseriscilo in risposta e log.

### Passo 5: simula lentezza

Aggiungi temporaneamente `await asyncio.sleep(2)` e misura il tempo. Poi applica un
timeout inferiore e restituisci un errore esplicito.

## 16. Esercizi

### Base

Aggiungi `/health/ready` distinto da `/health/live`.

### Intermedio

Aggiungi un limite di cinque chiamate concorrenti al generatore.

### Avanzato

Definisci SLI, SLO, dashboard e rollback per l'API del capstone. Motiva i valori.

## 17. Soluzioni

### Base

`live` dice che il processo gira. `ready` dice che può servire traffico:

```python
from fastapi import HTTPException

def dependencies_are_ready() -> bool:
    # Nel laboratorio non ci sono ancora dipendenze esterne.
    return True

@app.get("/health/ready")
async def ready() -> dict[str, str]:
    if not dependencies_are_ready():
        raise HTTPException(status_code=503, detail="not ready")
    return {"status": "ready"}
```

Non chiamare un provider costoso ad ogni probe: usa uno stato aggiornato in modo
controllato.

### Intermedio

```python
provider_slots = asyncio.Semaphore(5)

async with provider_slots:
    result = await generator.generate(question)
```

Il limite è per processo. Con più repliche serve una quota condivisa o lato provider.

### Avanzato: esempio di risposta

Per il capstone puoi proporre:

| Voce | Esempio iniziale | Azione |
|---|---:|---|
| disponibilità | 99,5% mensile | rollback se il canary peggiora oltre lo 0,5% |
| latenza | p95 sotto 2 s | allarme per 10 minuti consecutivi sopra soglia |
| qualità | almeno 90% citazioni valide | blocco deploy se l'eval regredisce |
| costo | massimo 0,03 euro/richiesta | riduzione contesto o rollback |

I numeri sono ipotesi da concordare con prodotto, non valori universali. La dashboard
segmenta errori e latenza per versione; il rollback riporta immagine e configurazione
all'ultima release valida ed è provato prima del rilascio.

## 18. Errori comuni

- Restituire successo vuoto dopo un errore.
- Aggiungere retry a ogni layer.
- Misurare solo la media.
- Confondere liveness e readiness.
- Inserire segreti nell'immagine.
- Usare un ruolo IAM amministratore.
- Fare canary senza metriche o criterio di stop.
- Avere rollback documentato ma mai provato.
- Registrare testo sensibile per comodità.

## 19. Domande di autoverifica

**Che differenza c'è fra log e metrica?**  
Il log descrive un evento; la metrica è un numero aggregato nel tempo.

**Che cosa significa p95?**  
Il 95% delle osservazioni è minore o uguale a quel valore.

**Perché una deadline è diversa dal timeout?**  
La deadline limita l'intera richiesta; il timeout può limitare un singolo passo.

**Che cosa fa un canary?**  
Espone una piccola quota alla nuova versione e controlla le metriche.

**Che cosa fa IAM?**  
Assegna identità e permessi a persone e workload AWS.

## 20. Prossimo passo

Leggi la [guida avanzata LLMOps](GUIDA.md) e poi il [laboratorio
infrastruttura](INFRA.md) quando il servizio locale è chiaro.
