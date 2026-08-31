# Guida completa: Python per servizi AI affidabili

## 1. Confini validati, core tipizzato

I dati sono non fidati quando arrivano da HTTP, file, code, database o output LLM.
Validali una volta al confine e usa tipi interni più forti.

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field

TenantId = Annotated[str, Field(pattern=r"^[a-z0-9-]{3,40}$")]

class AnswerRequest(BaseModel):
    tenant_id: TenantId
    question: str = Field(min_length=3, max_length=2_000)
    mode: Literal["fast", "accurate"] = "accurate"
```

Pydantic controlla dati runtime. Il type checker controlla il codice senza eseguirlo.
Servono entrambi: un'annotazione `str` non valida un payload JSON.

### `dataclass` o Pydantic?

| Usa | Quando |
|---|---|
| `dataclass(frozen=True)` | oggetto interno già validato, value object |
| `BaseModel` | input/output esterni, parsing e schema JSON |
| `TypedDict` | forma di dizionario richiesta da un framework |
| `Protocol` | contratto strutturale tra core e adapter |

## 2. Dipendenze tramite Protocol

Il dominio dipende da capacità, non da SDK concreti:

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    text: str
    score: float

class Retriever(Protocol):
    async def search(
        self, query: str, *, tenant_id: str, limit: int
    ) -> list[RetrievedChunk]: ...

class AnswerService:
    def __init__(self, retriever: Retriever) -> None:
        self._retriever = retriever
```

Un adapter per Snowflake, un fake e un adapter per vector DB soddisfano lo stesso
contratto senza ereditare da una classe base.

## 3. Errori come parte del contratto

Definisci eccezioni specifiche e conserva la causa:

```python
class ProviderError(RuntimeError):
    pass

class TransientProviderError(ProviderError):
    pass

class InvalidProviderResponse(ProviderError):
    pass
```

- errore transitorio: rate limit, rete temporanea, 5xx selezionati;
- errore permanente: credenziale invalida, input rifiutato, schema incompatibile;
- errore di dominio: operazione non consentita, evidenza insufficiente.

Non fare retry su ogni eccezione. Non trasformare un fallimento in una risposta vuota.

## 4. Asyncio correttamente

`asyncio` migliora throughput quando molte operazioni attendono I/O. Per calcolo CPU
pesante usa processi, codice nativo o un worker separato.

```python
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

async def with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    deadline: float,
    attempts: int = 3,
    base_delay: float = 0.2,
) -> T:
    loop = asyncio.get_running_loop()
    last_error: BaseException | None = None
    for attempt in range(attempts):
        remaining = deadline - loop.time()
        if remaining <= 0:
            raise TimeoutError("request deadline exceeded") from last_error
        try:
            async with asyncio.timeout(min(3.0, remaining)):
                return await operation()
        except (TimeoutError, TransientProviderError) as error:
            last_error = error
            if attempt == attempts - 1:
                raise
            retry_after = getattr(error, "retry_after", None)
            delay = (
                float(retry_after)
                if retry_after is not None
                else base_delay * (2**attempt) + random.uniform(0, 0.1)
            )
            if delay >= deadline - loop.time():
                raise TimeoutError("insufficient budget for retry") from error
            await asyncio.sleep(delay)
    raise AssertionError("unreachable")
```

`deadline` usa il clock monotono dell'event loop:
`loop.time() + total_budget_seconds`. L'adapter converte i timeout specifici dell'SDK
in `TransientProviderError`, mentre il timeout imposto dall'applicazione viene gestito
esplicitamente. Per un rate limit rispetta `Retry-After` quando presente.

La cancellazione deve propagarsi: non catturare `BaseException` e non sopprimere
`CancelledError`. La deadline rappresenta il budget totale; i retry non possono
moltiplicarlo.

### Concorrenza limitata

```python
class LimitedGenerator:
    def __init__(self, limit: int = 5) -> None:
        self._semaphore = asyncio.Semaphore(limit)

    async def generate(self, prompt: str) -> str:
        async with self._semaphore:
            return await call_provider(prompt)
```

Una semaphore protegge il processo, ma in più repliche serve un rate limiter condiviso
o una quota lato provider.

### Task concorrenti

Con `TaskGroup`, se un task fallisce gli altri vengono cancellati:

```python
async with asyncio.TaskGroup() as group:
    policy_task = group.create_task(load_policy())
    profile_task = group.create_task(load_profile())

policy = policy_task.result()
profile = profile_task.result()
```

Usalo quando i risultati sono entrambi necessari. Se uno è opzionale, gestisci quel
fallimento esplicitamente invece di applicare un comportamento globale.

## 5. Idempotenza

Per una scrittura, il client invia una chiave stabile:

```text
POST /incidents
Idempotency-Key: request-123:create-incident
```

Il server salva chiave, hash della richiesta e risultato nella stessa transazione
dell'effetto. Una ripetizione con stesso hash restituisce il risultato; stessa chiave
con payload diverso è un errore. Un semplice controllo "esiste?" seguito da "crea"
non è atomico e soffre race condition.

## 6. Configurazione e segreti

Carica configurazione all'avvio e fallisci subito se manca un valore obbligatorio.
Non leggere `os.environ` in ogni funzione e non impostare fallback silenziosi per
credenziali o ambienti.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    model_name: str
    provider_timeout_seconds: float = 3.0
    max_concurrency: int = 5
```

In produzione usa un secret manager; `.env` serve allo sviluppo e non va committato.

## 7. Logging e correlation

Logga eventi, non frasi da interpretare:

```json
{
  "event": "provider_call_completed",
  "request_id": "r-123",
  "provider": "example",
  "duration_ms": 842,
  "input_tokens": 390,
  "output_tokens": 87,
  "status": "success"
}
```

Evita prompt, documenti e output completi salvo policy esplicita. Propaga `request_id`
con `contextvars` o contesto della request. Metriche aggregate e trace non sostituiscono
i log: rispondono a domande diverse.

## 8. Test efficaci

Piramide:

1. molti unit test per dominio, parsing e policy;
2. integration test per adapter reali o container locali;
3. pochi end-to-end per flusso completo;
4. eval dataset per comportamento probabilistico.

```python
import pytest

class FakeRetriever:
    async def search(
        self, query: str, *, tenant_id: str, limit: int
    ) -> list[RetrievedChunk]:
        return [RetrievedChunk("c1", "policy text", 0.9)]

@pytest.mark.asyncio
async def test_answer_uses_authorized_retrieval() -> None:
    service = AnswerService(FakeRetriever())
    # Asserisci risultato e parametri di sicurezza osservabili.
```

Mocka rete, clock e UUID ai confini; non mockare ogni funzione interna. Un test che
riproduce l'implementazione riga per riga impedisce refactoring senza aumentare fiducia.

Testa almeno:

- limite minimo/massimo degli input;
- timeout e cancellazione;
- retry solo su errore transitorio;
- categorie o campi sconosciuti;
- concorrenza e doppia richiesta idempotente;
- redazione dati sensibili;
- error mapping HTTP.

## 9. Profiling

Misura prima di ottimizzare:

- `cProfile`/`py-spy`: dove passa il tempo CPU;
- `tracemalloc`: allocazioni Python;
- metriche per step: attese di rete e pool;
- event-loop lag: operazioni bloccanti in async;
- load test: throughput, p50/p95/p99 ed errori.

Un p95 alto con CPU bassa suggerisce I/O, code o rate limit; una media non mostra la
coda lunga.

## 10. Laboratorio

Costruisci un package `answer_service`:

1. modelli Pydantic per request/response;
2. `Retriever` e `Generator` come Protocol;
3. servizio async con budget totale, timeout per adapter e semaphore;
4. retry selettivo con backoff e jitter;
5. endpoint FastAPI e CLI JSONL;
6. log strutturati con `request_id`;
7. fake deterministici e test dei failure mode.

## 11. Soluzione e autovalutazione

La soluzione è corretta se:

- il core non importa FastAPI, LangChain o SDK provider;
- input invalido produce errore strutturato;
- `CancelledError` interrompe il lavoro;
- errore permanente causa un solo tentativo;
- la concorrenza osservata non supera il limite;
- due richieste con stessa idempotency key producono un solo effetto;
- test unitari non usano rete;
- log e trace non contengono testo sensibile.

**Esercizio orale:** spiega cosa accade quando il provider risponde dopo il timeout,
durante lo shutdown e quando tutte le richieste consumano la semaphore.
