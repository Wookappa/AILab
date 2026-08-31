# Guida completa: agenti affidabili con LangChain e LangGraph

## 1. Definizioni

- **LLM application:** software che usa uno o più modelli linguistici.
- **Workflow:** sequenza e diramazioni definite dal programmatore.
- **Tool calling:** il modello produce nome e argomenti di una funzione; il codice la
  valida ed esegue.
- **Agente:** sistema in cui il modello sceglie dinamicamente passi o tool per
  raggiungere un obiettivo.
- **Orchestrazione:** coordinamento di stato, passi, dipendenze, retry e stop.
- **Traiettoria:** sequenza di decisioni, tool call e risultati di una richiesta.

Un agente non è il solo prompt. È modello + stato + tool + policy + loop + runtime.

## 2. Quando non serve un agente

Usa un workflow deterministico quando:

- i passi sono noti;
- le regole sono stabili;
- gli errori hanno costo alto;
- audit e latenza devono essere prevedibili;
- una state machine esprime facilmente il processo.

Usa decisione agentica quando input e strumenti rendono impossibile enumerare tutte le
sequenze utili e il valore della flessibilità supera costo e rischio.

Spesso la soluzione migliore è ibrida: grafo deterministico con uno o due nodi in cui
il modello sceglie.

## 3. LangChain e LangGraph

**LangChain** offre interfacce per modelli, prompt, documenti, retriever, tool e
structured output. **LangGraph** costruisce workflow con stato usando un grafo.

Nel grafo:

- **node:** funzione che legge stato e restituisce un aggiornamento;
- **edge:** transizione fra nodi;
- **conditional edge:** sceglie il prossimo nodo da un risultato;
- **state:** dati persistenti della richiesta;
- **reducer:** regola per combinare aggiornamenti, per esempio appendere messaggi;
- **checkpoint:** snapshot persistito per riprendere.

Il framework coordina l'esecuzione; policy, dominio e autorizzazione restano codice
tuo e testabile.

## 4. Stato ben progettato

Non usare una lista di messaggi come unico stato:

```python
from typing import Literal, TypedDict

class AgentState(TypedDict):
    request_id: str
    user_id: str
    question: str
    status: Literal["planning", "executing", "waiting_approval", "done", "failed"]
    step_count: int
    cost_cents: float
    evidence_ids: list[str]
    pending_action_id: str | None
    final_answer: str | None
    error_code: str | None
```

Identità e autorizzazioni sensibili possono stare in un execution context non
modificabile dal modello. Lo stato deve essere serializzabile se usi checkpoint.

## 5. Tool design

Un tool efficace è piccolo e specifico:

```python
from pydantic import BaseModel, Field

class SearchPolicyInput(BaseModel):
    query: str = Field(min_length=3, max_length=300)
    limit: int = Field(default=5, ge=1, le=10)

class CreateIncidentInput(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    summary: str = Field(min_length=10, max_length=2_000)
    severity: str
```

Il modello può proporre il payload, ma il runtime:

1. valida schema;
2. deriva tenant e user dall'identità autenticata;
3. verifica permessi e policy;
4. richiede approval se necessario;
5. applica idempotency key;
6. imposta timeout;
7. registra audit;
8. restituisce risultato strutturato.

Evita `execute_sql`, `run_shell` o `http_request` generici. Espongono capacità molto
più ampie dell'obiettivo.

## 6. Loop agentico

Un pattern simile a **ReAct** alterna decisione e azione osservabile:

```text
state
-> modello propone tool call o risposta
-> validazione/policy
-> esecuzione tool
-> risultato aggiunto allo stato
-> nuova decisione
-> stop
```

Non è necessario né consigliabile salvare o mostrare ragionamenti interni estesi.
Conserva decisioni, input/output dei tool, evidenze, errori e transizioni.

## 7. Routing e condizioni di stop

```python
def route(state: AgentState) -> str:
    if state["step_count"] >= 6:
        return "fail_budget"
    if state["cost_cents"] >= 5:
        return "fail_budget"
    if state["status"] == "waiting_approval":
        return "human_review"
    if state["final_answer"] is not None:
        return "end"
    return "agent"
```

Limiti:

- numero passi;
- wall-clock timeout;
- token e costo;
- chiamate per tool;
- ripetizione della stessa azione;
- dimensione dello stato.

Uno stop "quando il modello pensa di aver finito" non è sufficiente.

### Esempio LangGraph eseguibile

Il corso usa LangGraph `1.x`. Questo esempio mostra state reducer, conditional edge,
checkpoint e interrupt umano:

```python
from operator import add
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt

class SupportState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    audit_events: Annotated[list[str], add]
    pending_action: dict[str, str] | None
    approved: bool | None
    result: str | None

def propose_incident(state: SupportState) -> dict:
    # In un sistema reale il modello produce un oggetto Pydantic validato.
    action = {
        "idempotency_key": "conversation-42:create-incident:v1",
        "title": "Payroll export unavailable",
    }
    return {
        "pending_action": action,
        "audit_events": ["incident_proposed"],
    }

def ask_approval(state: SupportState) -> dict:
    decision = interrupt({
        "kind": "approve_incident",
        "action": state["pending_action"],
    })
    return {
        "approved": bool(decision["approved"]),
        "audit_events": ["approval_received"],
    }

def route_approval(state: SupportState) -> Literal["execute", "cancel"]:
    return "execute" if state["approved"] else "cancel"

def execute(state: SupportState) -> dict:
    action = state["pending_action"]
    assert action is not None
    # create_once salva chiave ed effetto atomicamente.
    incident_id = incident_store.create_once(
        key=action["idempotency_key"],
        payload=action,
    )
    return {"result": incident_id, "audit_events": ["incident_created"]}

def cancel(state: SupportState) -> dict:
    return {"result": "cancelled", "audit_events": ["incident_cancelled"]}

builder = StateGraph(SupportState)
builder.add_node("propose", propose_incident)
builder.add_node("approval", ask_approval)
builder.add_node("execute", execute)
builder.add_node("cancel", cancel)
builder.add_edge(START, "propose")
builder.add_edge("propose", "approval")
builder.add_conditional_edges(
    "approval",
    route_approval,
    {"execute": "execute", "cancel": "cancel"},
)
builder.add_edge("execute", END)
builder.add_edge("cancel", END)

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "conversation-42"}}

paused = graph.invoke(
    {
        "messages": [HumanMessage(content="Apri un incidente")],
        "audit_events": [],
        "pending_action": None,
        "approved": None,
        "result": None,
    },
    config=config,
)
completed = graph.invoke(
    Command(resume={"approved": True}),
    config=config,
)
```

`add_messages` e `operator.add` sono reducer: combinano aggiornamenti invece di
sovrascrivere liste. La `path_map` nelle conditional edge rende esplicite le
destinazioni ammesse.

`InMemorySaver` serve solo a test e demo. In produzione usa un checkpointer persistente,
per esempio Postgres, e conserva lo stesso `thread_id` al resume.

**Semantica critica:** quando riprendi dopo `interrupt`, LangGraph riesegue il nodo
interrotto dall'inizio. Non mettere side effect prima di `interrupt`; ogni effetto
dopo il resume deve comunque essere idempotente perché un crash può avvenire dopo la
scrittura ma prima del checkpoint.

## 8. Error taxonomy

Classifica gli errori perché la recovery dipende dalla causa:

| Errore | Esempio | Azione |
|---|---|---|
| input | schema tool invalido | feedback strutturato, massimo un repair |
| transient | 429 o timeout breve | retry limitato |
| permanent | 401 o permesso negato | stop esplicito |
| domain | saldo non disponibile | percorso alternativo/astensione |
| policy | scrittura non approvata | human gate |
| budget | troppi passi/token | stop controllato |
| invariant | stato impossibile | fail e alert |

Non trasformare tutti gli errori in testo per il modello: alcuni devono interrompere
il workflow.

## 9. Checkpoint e idempotenza

Un checkpoint salva stato e posizione nel grafo. Serve a:

- riprendere dopo crash;
- attendere una decisione umana;
- audit e debugging;
- evitare di ripetere passi costosi.

Non garantisce da solo **exactly once**. I sistemi distribuiti normalmente offrono
almeno una consegna; un tool di scrittura deve essere idempotente.

```text
idempotency_key =
  conversation_id + logical_action + normalized_payload_hash
```

Salva chiave ed effetto atomicamente. Al resume, controlla il registro prima di
rieseguire.

## 10. Human-in-the-loop

Il controllo umano deve mostrare:

- azione proposta;
- parametri;
- evidenze;
- impatto;
- scadenza;
- chi può approvare.

L'approvazione è legata all'hash del payload. Se il modello modifica il payload,
serve una nuova approvazione. Un semplice booleano `approved=true` riutilizzabile è
insicuro.

## 11. Memoria

- **working memory:** stato della richiesta corrente;
- **conversation memory:** cronologia utile della conversazione;
- **long-term memory:** fatti persistiti fra sessioni;
- **semantic memory:** elementi recuperati per somiglianza;
- **episodic memory:** eventi o interazioni precedenti.

Memoria non significa salvare tutto. Definisci consenso, retention, cancellazione,
provenienza e confidenza. Le istruzioni storiche non devono superare policy attuali.

## 12. Autorizzazione

**Autenticazione** verifica chi è l'utente. **Autorizzazione** verifica cosa può fare.

```text
authenticated identity
-> server policy
-> allowed tool
-> resource-level filter
-> execution
-> audit
```

Il modello non decide ruoli, tenant o permessi e non può elevarli tramite prompt. Un
tool deve applicare la stessa autorizzazione anche se invocato fuori dall'agente.

## 13. Planning

Piani espliciti aiutano task lunghi, ma possono diventare obsoleti. Pattern:

- **plan-and-execute:** piano iniziale, poi esecuzione;
- **replanning:** aggiorna piano dopo risultati;
- **router:** sceglie un workflow specializzato;
- **supervisor:** coordina worker con responsabilità limitate.

Preferisci il pattern più semplice. Chiedi al modello output strutturato come lista di
step e valida tool consentiti e dipendenze.

## 14. Multi-agent

Un sistema multi-agent usa più ruoli/modelli che comunicano. È giustificato quando:

- domini e tool hanno confini reali;
- contesti separati riducono rumore;
- parti indipendenti possono procedere in parallelo;
- responsabilità e metriche sono separabili.

Costi:

- più token e latenza;
- protocolli di handoff;
- errori emergenti;
- tracing e test più difficili;
- loop fra agenti.

Prima confronta con un singolo grafo e nodi specializzati.

## 15. Testing

Quattro livelli:

1. **unit:** routing, policy, budget, reducer;
2. **tool contract:** schema, auth, timeout, idempotenza;
3. **trajectory:** sequenze ammesse con modello fake;
4. **eval probabilistica:** successo su scenari ripetuti.

Testa invarianti, non stringhe esatte:

```text
nessuna scrittura senza approval
nessun risultato cross-tenant
massimo sei passi
ogni risposta fattuale cita evidence_id
stessa idempotency key produce un effetto
```

Con un fake model preprogrammi tool call e errori. Con modello reale esegui più run,
misura success rate, costo, p95 e distribuzione delle traiettorie.

## 16. Osservabilità

Ogni trace include:

- request/conversation ID;
- versione graph, prompt e modello;
- nodo e transizione;
- tool name, durata e status;
- token/costo;
- retry e approval;
- evidence IDs;
- risultato finale.

Redigi PII e segreti. Una trace deve ricostruire il comportamento senza registrare
necessariamente contenuto sensibile.

## 17. Laboratorio

Costruisci un support agent:

1. workflow deterministico baseline;
2. state e nodi LangGraph;
3. tool read-only `search_policies` e `get_status`;
4. tool `create_ticket` con policy, approval e idempotenza;
5. checkpoint persistente;
6. limiti di passi, tempo e costo;
7. error taxonomy e recovery;
8. 40 scenari, inclusi injection, crash e resume;
9. confronto baseline/agente.

## 18. Soluzione di riferimento

La soluzione è pronta quando:

- una state machine spiega ogni transizione;
- il modello può proporre ma non autorizzare;
- tool input/output sono tipizzati;
- retry non duplica effetti;
- resume riparte dal checkpoint corretto;
- loop e budget hanno uscita esplicita;
- failure permanente non viene ripetuto;
- metriche confrontano valore dell'agente con workflow semplice;
- sai motivare perché ogni nodo è deterministico o agentico.
