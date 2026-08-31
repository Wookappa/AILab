# Lezione passo-passo: da una funzione a un agente controllato

## Cosa saprai fare alla fine

Alla fine saprai:

1. distinguere funzione, workflow, tool calling e agente;
2. costruire prima un workflow Python deterministico;
3. definire un tool con input validato da Pydantic;
4. spiegare stato, grafo, nodo e arco;
5. creare ed eseguire un grafo con LangGraph 1.x;
6. aggiungere checkpoint e approvazione umana tramite interrupt;
7. evitare ticket duplicati con l'idempotenza;
8. applicare autorizzazione, limiti, timeout e gestione degli errori;
9. decidere quando non usare un agente o un sistema multi-agent.

## Cosa devi sapere prima

Completa [la lezione su LLM e output strutturato](../03-llm-foundations/LEZIONE.md).
Devi sapere che un modello genera output probabilistico e che Pydantic valida la
forma dei dati.

È utile completare anche [la lezione su RAG](../04-rag/LEZIONE.md), perché la ricerca
di documenti è un tipico strumento di sola lettura per un agente.

Devi saper leggere funzioni, condizioni `if`, dizionari e classi Python. Per eseguire
gli esempi, dalla cartella `AI-Mastery-Accelerator`:

```powershell
pip install -e ".[ai]"
```

## 1. Lo scenario concreto

Un assistente di supporto riceve:

```text
Non riesco a scaricare il cedolino. Se non trovi una soluzione, apri un ticket.
```

Il sistema potrebbe:

1. cercare una procedura;
2. decidere se la procedura risponde;
3. chiedere conferma prima di creare un ticket;
4. creare il ticket una sola volta;
5. restituire il risultato.

È allettante chiamare tutto questo “agente”. Ma spesso i passi sono già noti. Se
confondiamo concetti diversi, aggiungiamo variabilità e rischi senza ottenere valore.
Partiamo quindi dalla soluzione più semplice.

## 2. Funzione, workflow, tool calling e agente

### Funzione

Una **funzione** riceve argomenti e restituisce un risultato. Il programma decide
quando chiamarla.

```python
def calcola_iva(importo: float) -> float:
    return importo * 0.22
```

Serve quando il compito è preciso e locale. Non sceglie autonomamente altri passi.

### Workflow

Un **workflow**, cioè flusso di lavoro, è una sequenza o diramazione definita dal
programmatore.

```text
ricevi richiesta -> cerca soluzione -> se assente crea ticket -> rispondi
```

È deterministico quando lo stesso stato segue le stesse regole. Il modello può essere
usato dentro un passo, ma non decide necessariamente l'intero percorso.

Analogia: una lista di controllo in aeroporto. Le condizioni cambiano il percorso,
ma i percorsi ammessi sono stati progettati prima.

### Tool calling

Un **tool** è una funzione resa disponibile al modello con nome, descrizione e schema
degli argomenti. **Tool calling**, cioè chiamata di strumenti, significa che il
modello propone qualcosa come:

```json
{
  "tool": "cerca_procedura",
  "arguments": {"query": "scaricare cedolino", "limit": 3}
}
```

Il modello non deve eseguire direttamente la funzione. Il programma valida argomenti,
permessi e policy, poi decide se eseguirla.

Analogia: il modello compila un modulo di richiesta; il server è l'ufficio che
controlla il modulo e compie l'azione.

### Agente

Un **agente** è un sistema in cui il modello sceglie dinamicamente passi o tool per
raggiungere un obiettivo. Di solito ripete un ciclo:

```text
osserva stato -> sceglie azione -> esegue tool -> osserva risultato -> continua o termina
```

L'agente è utile quando non possiamo elencare facilmente tutte le sequenze. Introduce
però costo, variabilità, loop, nuovi errori e difficoltà di test.

La regola pratica è:

```text
funzione -> workflow -> tool calling -> agente
```

Passa al livello successivo soltanto quando quello precedente non risolve il problema.

## 3. Prima soluzione: workflow Python deterministico

Il seguente programma non usa un modello. Cerca parole note e apre un ticket solo se
non trova una procedura. Copialo in `workflow_supporto.py`:

```python
PROCEDURE = {
    "cedolino": "Apri Portale Payroll > Documenti > Cedolini.",
    "password": "Apri Recupera accesso e segui il collegamento ricevuto.",
}


def cerca_procedura(richiesta: str) -> str | None:
    testo = richiesta.lower()
    for parola, procedura in PROCEDURE.items():
        if parola in testo:
            return procedura
    return None


def crea_ticket(richiesta: str) -> str:
    return "TICKET-001"


def gestisci_richiesta(richiesta: str) -> dict[str, str]:
    procedura = cerca_procedura(richiesta)
    if procedura is not None:
        return {"stato": "risolto", "risposta": procedura}

    ticket_id = crea_ticket(richiesta)
    return {
        "stato": "ticket_creato",
        "risposta": f"Ho creato {ticket_id}.",
    }


if __name__ == "__main__":
    print(gestisci_richiesta("Non riesco a vedere il cedolino"))
    print(gestisci_richiesta("Il computer si spegne"))
```

Esegui:

```powershell
python workflow_supporto.py
```

Output atteso:

```text
{'stato': 'risolto', 'risposta': 'Apri Portale Payroll > Documenti > Cedolini.'}
{'stato': 'ticket_creato', 'risposta': 'Ho creato TICKET-001.'}
```

`gestisci_richiesta` definisce l'ordine. La condizione `if` controlla la diramazione.
Questa soluzione è facile da capire e testare. Il limite è la ricerca per parole
esatte; potremmo sostituirla con RAG o con una classificazione LLM senza trasformare
subito tutto in un agente.

## 4. Poi un tool tipizzato con Pydantic

Un tool affidabile ha uno scopo piccolo e argomenti stretti. **Tipizzato** significa
che dichiara tipi e vincoli invece di accettare qualunque dizionario.

LangChain offre il decoratore `@tool`, che pubblica una funzione come strumento.
Pydantic valida l'input:

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CercaProceduraInput(BaseModel):
    query: str = Field(min_length=3, max_length=200)
    limit: int = Field(default=3, ge=1, le=5)


@tool(args_schema=CercaProceduraInput)
def cerca_procedura_tool(query: str, limit: int = 3) -> list[str]:
    """Cerca procedure di supporto di sola lettura."""
    procedure = [
        "Cedolino: apri Portale Payroll > Documenti.",
        "Password: usa Recupera accesso.",
        "Ferie: invia la richiesta al manager.",
    ]
    parole = query.lower().split()
    risultati = [
        procedura
        for procedura in procedure
        if any(parola in procedura.lower() for parola in parole)
    ]
    return risultati[:limit]


if __name__ == "__main__":
    risultato = cerca_procedura_tool.invoke(
        {"query": "portale cedolino", "limit": 2}
    )
    print(risultato)
```

Output atteso:

```text
['Cedolino: apri Portale Payroll > Documenti.']
```

`min_length`, `max_length`, `ge` e `le` bloccano input troppo corti, lunghi o fuori
intervallo. La descrizione spiega al modello quando usare il tool. Il tool è di sola
lettura: non modifica sistemi esterni.

Un tool di scrittura, come `crea_ticket`, richiede controlli aggiuntivi:
autorizzazione, approvazione, idempotenza, timeout e audit.

## 5. Stato, grafo, nodo e arco

Quando un workflow cresce, possiamo rappresentarlo come un **grafo**.

- Lo **stato** contiene i dati correnti della richiesta.
- Un **nodo** è una funzione che legge lo stato e restituisce aggiornamenti.
- Un **arco** collega due nodi e indica una transizione.
- Un **arco condizionale** sceglie la destinazione in base a una regola.

Disegno del primo grafo:

```text
                    ┌─────────────┐
INIZIO -> classifica┤             ├-> rispondi -> FINE
                    └──────┬──────┘
                           └--------> crea_ticket -> FINE
```

Lo stato potrebbe essere:

```text
richiesta = "Il computer si spegne"
categoria = "sconosciuta"
risultato = null
```

Ogni nodo dovrebbe fare una cosa comprensibile. Il grafo non rende automaticamente
il sistema agentico: può rappresentare anche un workflow interamente deterministico.

## 6. Esempio completo LangGraph 1.x senza approval

LangGraph è una libreria per costruire workflow con stato come grafi. Questo primo
esempio non ha approvazione umana: serve a imparare le parti fondamentali.

Copia in `grafo_supporto.py`:

```python
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class SupportState(TypedDict):
    richiesta: str
    categoria: Literal["cedolino", "password", "sconosciuta"] | None
    risultato: str | None


def classifica(state: SupportState) -> dict:
    testo = state["richiesta"].lower()
    if "cedolino" in testo:
        categoria = "cedolino"
    elif "password" in testo:
        categoria = "password"
    else:
        categoria = "sconosciuta"
    return {"categoria": categoria}


def scegli_percorso(
    state: SupportState,
) -> Literal["rispondi", "crea_ticket"]:
    if state["categoria"] == "sconosciuta":
        return "crea_ticket"
    return "rispondi"


def rispondi(state: SupportState) -> dict:
    procedure = {
        "cedolino": "Apri Portale Payroll > Documenti.",
        "password": "Usa il collegamento Recupera accesso.",
    }
    categoria = state["categoria"]
    assert categoria in procedure
    return {"risultato": procedure[categoria]}


def crea_ticket(state: SupportState) -> dict:
    return {"risultato": "Creato TICKET-001"}


builder = StateGraph(SupportState)
builder.add_node("classifica", classifica)
builder.add_node("rispondi", rispondi)
builder.add_node("crea_ticket", crea_ticket)
builder.add_edge(START, "classifica")
builder.add_conditional_edges(
    "classifica",
    scegli_percorso,
    {
        "rispondi": "rispondi",
        "crea_ticket": "crea_ticket",
    },
)
builder.add_edge("rispondi", END)
builder.add_edge("crea_ticket", END)
graph = builder.compile()


if __name__ == "__main__":
    finale = graph.invoke(
        {
            "richiesta": "Non vedo il cedolino",
            "categoria": None,
            "risultato": None,
        }
    )
    print(finale)
```

Esegui:

```powershell
python grafo_supporto.py
```

Output atteso:

```text
{'richiesta': 'Non vedo il cedolino', 'categoria': 'cedolino', 'risultato': 'Apri Portale Payroll > Documenti.'}
```

`StateGraph` riceve il tipo dello stato. `add_node` registra funzioni. `START` ed
`END` rappresentano inizio e fine. `add_conditional_edges` rende esplicite tutte le
destinazioni ammesse. In produzione, la classificazione potrebbe usare un modello
con output Pydantic, mantenendo però il routing e i limiti nel codice.

## 7. Dal grafo all'agente

Per trasformare una parte del sistema in agente, un nodo può chiedere a un LLM di
scegliere il prossimo tool. Il runtime deve comunque:

1. accettare soltanto tool in una lista consentita;
2. validare gli argomenti;
3. controllare identità e permessi;
4. contare passi, tempo e costo;
5. interrompere loop;
6. registrare decisioni e risultati.

Il modello propone; il programma autorizza. Questa separazione è essenziale.

## 8. Idempotenza: evitare ticket duplicati

Un'operazione è **idempotente** quando ripeterla con la stessa chiave logica produce
lo stesso effetto, non un nuovo effetto.

Analogia: premi due volte il pulsante dell'ascensore. La richiesta resta una; non
arrivano due ascensori.

Caso reale:

1. il sistema crea `TICKET-123`;
2. la rete cade prima di salvare il risultato;
3. il workflow riparte;
4. senza protezione crea anche `TICKET-124`.

Usiamo una **idempotency key**, cioè chiave di idempotenza:

```text
conversazione-42:create-ticket:v1
```

Il database salva atomicamente chiave e risultato. Se la stessa chiave ricompare,
restituisce `TICKET-123`.

```python
class TicketStore:
    def __init__(self) -> None:
        self._creati: dict[str, str] = {}

    def create_once(self, key: str) -> str:
        if key not in self._creati:
            self._creati[key] = f"TICKET-{len(self._creati) + 1:03d}"
        return self._creati[key]
```

Un checkpoint da solo non garantisce l'assenza di duplicati: un crash può avvenire
dopo l'effetto esterno e prima del checkpoint.

## 9. Interrupt, checkpoint e controllo umano

Un **checkpoint** è una fotografia persistita dello stato e della posizione nel
grafo. Serve a riprendere dopo un arresto o ad attendere una decisione.

Un **interrupt** è una pausa esplicita. Il grafo restituisce la richiesta di
approvazione e riparte quando riceve la risposta.

**Human-in-the-loop**, cioè persona nel ciclo, significa che un essere umano controlla
un'azione sensibile. Non vuol dire approvare ogni lettura: concentra il controllo su
scritture, pagamenti, cancellazioni o comunicazioni esterne.

Programma completo `grafo_approval.py`:

```python
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field


class TicketProposto(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=100)
    titolo: str = Field(min_length=5, max_length=80)
    descrizione: str = Field(min_length=10, max_length=500)
    priorita: Literal["bassa", "media", "alta"]


class ApprovalState(TypedDict):
    richiesta: str
    proposta: dict | None
    approvato: bool | None
    risultato: str | None


class TicketStore:
    def __init__(self) -> None:
        self._creati: dict[str, str] = {}

    def create_once(self, key: str) -> str:
        if key not in self._creati:
            self._creati[key] = f"TICKET-{len(self._creati) + 1:03d}"
        return self._creati[key]


store = TicketStore()


def proponi(state: ApprovalState) -> dict:
    proposta = TicketProposto(
        idempotency_key="conversation-42:create-ticket:v1",
        titolo="Problema non risolto",
        descrizione=state["richiesta"],
        priorita="media",
    )
    return {"proposta": proposta.model_dump()}


def chiedi_approvazione(state: ApprovalState) -> dict:
    decisione = interrupt(
        {
            "tipo": "approva_ticket",
            "proposta": state["proposta"],
        }
    )
    return {"approvato": bool(decisione["approvato"])}


def instrada(state: ApprovalState) -> Literal["esegui", "annulla"]:
    return "esegui" if state["approvato"] else "annulla"


def esegui(state: ApprovalState) -> dict:
    proposta = TicketProposto.model_validate(state["proposta"])
    ticket_id = store.create_once(proposta.idempotency_key)
    return {"risultato": f"Creato {ticket_id}"}


def annulla(state: ApprovalState) -> dict:
    return {"risultato": "Operazione annullata"}


builder = StateGraph(ApprovalState)
builder.add_node("proponi", proponi)
builder.add_node("approval", chiedi_approvazione)
builder.add_node("esegui", esegui)
builder.add_node("annulla", annulla)
builder.add_edge(START, "proponi")
builder.add_edge("proponi", "approval")
builder.add_conditional_edges(
    "approval",
    instrada,
    {"esegui": "esegui", "annulla": "annulla"},
)
builder.add_edge("esegui", END)
builder.add_edge("annulla", END)

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "conversation-42"}}


if __name__ == "__main__":
    pausa = graph.invoke(
        {
            "richiesta": "Il computer si spegne continuamente.",
            "proposta": None,
            "approvato": None,
            "risultato": None,
        },
        config=config,
    )
    print("Richiesta umana:", pausa["__interrupt__"][0].value)

    finale = graph.invoke(
        Command(resume={"approvato": True}),
        config=config,
    )
    print("Risultato:", finale["risultato"])

    stesso_ticket = store.create_once(
        "conversation-42:create-ticket:v1"
    )
    print("Ripetizione sicura:", stesso_ticket)
```

Output atteso:

```text
Richiesta umana: {'tipo': 'approva_ticket', 'proposta': {...}}
Risultato: Creato TICKET-001
Ripetizione sicura: TICKET-001
```

`InMemorySaver` conserva checkpoint solo nella memoria del processo ed è adatto a una
demo. In produzione serve un archivio persistente. Al resume LangGraph può rieseguire
il nodo interrotto dall'inizio: non mettere effetti esterni prima di `interrupt`, e
rendi idempotenti quelli successivi.

## 10. Autorizzazione, limiti ed errori

**Autenticazione** verifica chi è l'utente. **Autorizzazione** verifica che cosa può
fare. Il modello non deve inventare ruolo, tenant o permessi.

```text
identità autenticata -> policy server -> tool consentito -> risorsa consentita -> azione
```

Per ogni esecuzione definisci:

- numero massimo di passi, per esempio 6;
- timeout totale, per esempio 20 secondi;
- massimo numero di chiamate allo stesso tool;
- budget di token e costo;
- dimensione massima dello stato;
- condizione di fine e risposta in caso di limite.

Non tutti gli errori si trattano allo stesso modo:

- errore di input: restituisci dettagli di validazione;
- errore temporaneo, come un timeout breve: retry limitato;
- permesso negato: termina, non riprovare;
- dato non disponibile: usa percorso alternativo o astensione;
- limite superato: termina in modo controllato;
- stato impossibile: interrompi e genera un avviso.

Un **retry**, cioè nuovo tentativo, deve avere un limite e non deve duplicare effetti.

## 11. Quando non usare un agente

Non usare un agente quando:

- i passi sono noti e stabili;
- una funzione o macchina a stati descrive bene il processo;
- l'errore ha costo alto e non serve flessibilità;
- latenza e costo devono essere prevedibili;
- non hai un insieme di test realistico;
- il modello non aggiunge una decisione utile.

Per il calcolo dell'IVA, la validazione di un codice fiscale o una procedura di
pagamento fissa, il codice deterministico è normalmente migliore.

## 12. Quando non usare multi-agent

**Multi-agent** significa usare più agenti con ruoli e comunicazioni separate. Non è
sinonimo di qualità maggiore.

Evitalo se un singolo workflow con nodi specializzati basta. Più agenti comportano:

- più token e latenza;
- passaggi di consegna che possono perdere informazioni;
- loop fra agenti;
- autorizzazioni più complesse;
- test e osservabilità più difficili.

Valutalo solo quando esistono confini reali fra domini o strumenti, contesti separati
sono utili e lavori indipendenti possono procedere in parallelo.

## 13. Laboratorio guidato

1. **Esegui il workflow semplice.**
   Verifica: cedolino segue il ramo `risolto`; altro problema crea il ticket.
2. **Esegui il tool tipizzato.**
   Verifica: `limit=8` produce un errore Pydantic.
3. **Esegui `grafo_supporto.py`.**
   Verifica: lo stato finale contiene categoria e risultato.
4. **Cambia la richiesta in un problema sconosciuto.**
   Verifica: il grafo raggiunge `crea_ticket`.
5. **Esegui `grafo_approval.py`.**
   Verifica: compare una pausa prima della creazione.
6. **Riprendi con `approvato=False`.**
   Nel file cambia temporaneamente il valore passato a `Command(resume=...)` da
   `True` a `False`, poi rieseguilo.
   Verifica: il risultato è `Operazione annullata` e lo store resta vuoto.
7. **Riprendi con approvazione.**
   Ripristina `approvato=True` e riesegui.
   Verifica: il ticket viene creato.
8. **Ripeti la stessa chiave.**
   Verifica: ottieni lo stesso identificatore, non un nuovo ticket.
9. **Disegna i limiti.**
   Scrivi massimo passi, timeout, retry e azioni che richiedono approvazione.
   Verifica: ogni limite ha un comportamento di uscita esplicito.

## 14. Esercizi graduati

### Base

1. Aggiungi la categoria `ferie` al grafo senza approval.
2. Aggiungi `audit_events: list[str]` allo stato e registra ogni nodo visitato.
3. Imposta priorità `alta` se la richiesta contiene `urgente`.

### Intermedio

1. Aggiungi allo store il contenuto del ticket, non solo l'identificatore.
2. Lega l'approvazione a una copia esatta della proposta.
3. Simula un timeout temporaneo e consenti al massimo due tentativi senza creare
   duplicati.

### Avanzato

Sostituisci il nodo `classifica` con un modello fake a output Pydantic. Permetti al
modello di proporre soltanto `cerca_procedura_tool`; mantieni creazione ticket,
autorizzazione, approval e limiti nel codice deterministico. Confronta successo,
tempo e numero di passi con il workflow originale.

## 15. Soluzioni ragionate

Per la categoria ferie:

```python
class SupportState(TypedDict):
    richiesta: str
    categoria: Literal["cedolino", "password", "ferie", "sconosciuta"] | None
    risultato: str | None


def classifica(state: SupportState) -> dict:
    testo = state["richiesta"].lower()
    if "cedolino" in testo:
        return {"categoria": "cedolino"}
    if "password" in testo:
        return {"categoria": "password"}
    if "ferie" in testo:
        return {"categoria": "ferie"}
    return {"categoria": "sconosciuta"}
```

Aggiungi poi `"ferie": "Apri il portale HR e invia la richiesta al manager."` al
dizionario delle procedure. Lo stato e il dizionario devono evolvere insieme.

Per registrare audit senza perdere eventi, ogni nodo può copiare e ampliare la lista:

```python
def aggiungi_evento(state: dict, evento: str) -> list[str]:
    return [*state.get("audit_events", []), evento]


def crea_ticket(state: SupportState) -> dict:
    return {
        "risultato": "Creato TICKET-001",
        "audit_events": aggiungi_evento(state, "ticket_creato"),
    }
```

In un grafo più avanzato puoi usare un reducer, cioè una regola che combina
automaticamente aggiornamenti concorrenti. Per il primo esercizio, la copia esplicita
è più facile da osservare.

Per legare l'approvazione al contenuto, calcola un hash della proposta normalizzata e
salva quell'hash nella richiesta di approval. Se titolo, descrizione o priorità
cambiano, l'hash cambia e serve una nuova approvazione.

## 16. Errori comuni

- **Chiamare agente qualsiasi automazione.** Un workflow con passi fissi non diventa
  agente solo perché usa un LLM.
- **Far eseguire al modello direttamente un tool.** Il server deve validare e
  autorizzare.
- **Esporre tool generici.** `esegui_sql` o `chiama_qualsiasi_url` concedono capacità
  troppo ampie.
- **Usare solo la cronologia come stato.** Servono campi espliciti per passi, stato,
  costi, azioni pendenti ed errori.
- **Confondere checkpoint e idempotenza.** Il checkpoint aiuta a riprendere; la chiave
  evita effetti duplicati.
- **Mettere una scrittura prima dell'interrupt.** Al resume il nodo può ripartire.
- **Riprovare ogni errore.** Un permesso negato non è un errore temporaneo.
- **Lasciare il loop senza limiti.** Il modello può ripetere la stessa azione.
- **Usare multi-agent per moda.** Aumenta coordinamento e punti di guasto.

## 17. Domande di autoverifica

**Qual è la differenza fra funzione e workflow?**  
La funzione svolge un compito; il workflow coordina più passi e diramazioni.

**Che cosa fa il modello nel tool calling?**  
Propone nome del tool e argomenti. Il runtime valida e decide l'esecuzione.

**Che cosa rende un sistema un agente?**  
Il modello sceglie dinamicamente passi o strumenti in un ciclo orientato a un
obiettivo.

**Che cos'è lo stato?**  
L'insieme dei dati correnti necessari per decidere e proseguire.

**A che cosa serve un arco condizionale?**  
A scegliere il prossimo nodo secondo una regola esplicita.

**Perché il checkpoint non basta contro i duplicati?**  
Un crash può avvenire dopo l'effetto esterno ma prima del salvataggio del checkpoint.

**Che cos'è l'idempotenza?**  
La proprietà per cui ripetere la stessa azione logica non crea un secondo effetto.

**Chi decide i permessi?**  
Il codice del server usando identità e policy, non il modello.

**Quando è preferibile non usare un agente?**  
Quando passi e regole sono noti e un workflow deterministico risolve il problema.

## Approfondimento tecnico

Solo dopo aver eseguito i due grafi, passa alla
[GUIDA tecnica su agenti affidabili e LangGraph](GUIDA.md).
