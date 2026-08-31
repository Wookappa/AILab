# Lezione passo-passo: capire e usare un modello linguistico

## Cosa saprai fare alla fine

Alla fine saprai:

1. spiegare con parole semplici che cosa sono intelligenza artificiale, modello e
   modello linguistico di grandi dimensioni;
2. distinguere input, output, token, prompt e contesto;
3. descrivere come nasce una risposta, un token alla volta;
4. scegliere una temperatura sensata e riconoscere un'allucinazione;
5. separare istruzioni di sistema e richiesta dell'utente;
6. ottenere e validare un risultato JSON con Pydantic;
7. confrontare zero-shot e few-shot;
8. decidere quando esplorare RAG, tool calling o fine-tuning;
9. testare codice LangChain senza usare una chiave o chiamare un servizio esterno.

## Cosa devi sapere prima

Devi saper eseguire un file Python, definire una funzione e leggere una classe. Se
questi concetti sono nuovi, completa [Python passo-passo](../01-python-production/LEZIONE.md).

È utile, ma non obbligatorio, aver letto
[il primo sistema di machine learning](../02-ml-production/LEZIONE.md). Da quella
lezione riprenderemo l'idea di **modello** come funzione che riceve dati e produce una
previsione.

Per gli esempi servono Python 3.12 e le dipendenze del progetto. Dalla cartella
`AI-Mastery-Accelerator`:

```powershell
pip install -e ".[ai]"
```

## 1. Il problema concreto

Un gruppo di assistenza riceve ticket come questo:

```text
Da ieri non riesco a scaricare la busta paga. È urgente.
```

Vorremmo ottenere automaticamente:

```json
{
  "categoria": "payroll",
  "priorita": "alta",
  "sintesi": "Impossibile scaricare la busta paga"
}
```

Scrivere tutte le regole a mano è difficile. Le persone usano sinonimi, fanno errori
e raccontano lo stesso problema in molti modi. Un modello linguistico può leggere il
testo e produrre una classificazione. Prima di affidargli un processo, però, dobbiamo
capire che cosa fa davvero e che cosa non garantisce.

## 2. Dall'intelligenza artificiale al modello linguistico

**Intelligenza artificiale**, abbreviata **AI** dall'inglese *Artificial
Intelligence*, è il nome generale per software che svolge compiti come riconoscere
immagini, comprendere testo o pianificare passi.

Un **modello** è una funzione con molti valori interni, chiamati parametri, appresi da
esempi. È simile a una ricetta regolabile: l'input entra, i parametri trasformano i
dati e otteniamo un output.

```text
input -> modello -> output
```

Un **modello linguistico** lavora con sequenze di testo. Un **LLM**, dall'inglese
*Large Language Model*, è un modello linguistico di grandi dimensioni: contiene molti
parametri ed è stato addestrato su grandi quantità di testo.

La parola “grande” non significa “sempre corretto”. Significa soltanto che capacità,
costi e quantità di parametri sono elevati rispetto a modelli più piccoli.

## 3. Input, output e prompt

L'**input** è ciò che inviamo al modello. L'**output** è ciò che il modello genera.

Il **prompt** è l'insieme di istruzioni e dati forniti in input. Per esempio:

```text
Classifica il ticket come payroll, ferie oppure altro.
Ticket: Non vedo il cedolino di agosto.
```

Un prompt non è una domanda magica. È un contratto imperfetto: descrive il compito,
ma il modello può interpretarlo male. Un buon prompt rende espliciti:

- obiettivo;
- valori consentiti;
- dati da analizzare;
- comportamento quando mancano informazioni;
- formato dell'output.

Esempio più robusto:

```text
Obiettivo: classifica un ticket.
Categorie consentite: payroll, ferie, altro.
Regola: se il testo non basta, scegli altro.
Dati non fidati:
<ticket>Non vedo il cedolino di agosto.</ticket>
Output: restituisci categoria e breve sintesi.
```

“Dati non fidati” significa che il ticket può contenere errori o perfino istruzioni
malevole. Il programma deve trattarlo come contenuto da analizzare, non come una nuova
regola.

## 4. Token e contesto

Il modello non legge direttamente parole come una persona. Un componente chiamato
**tokenizer**, cioè segmentatore, divide il testo in **token**. Un token può essere una
parola, una parte di parola, uno spazio o un segno di punteggiatura.

Esempio illustrativo:

```text
"pagamento urgente!" -> ["pagamento", " urgente", "!"]
```

La divisione reale cambia da modello a modello. Non assumere che un token equivalga a
una parola.

Il **contesto** è tutto ciò che il modello può considerare nella richiesta corrente:
istruzioni, domanda, esempi, cronologia e documenti allegati. La **finestra di
contesto** è il numero massimo di token accettati fra input e output.

Analogia quotidiana: il contesto è il contenuto disponibile sulla scrivania mentre
risolvi un esercizio. Se un foglio importante non è sulla scrivania, non puoi usarlo.
Se la scrivania è piena di fogli inutili, trovare il dettaglio giusto diventa più
difficile.

Più token comportano in genere più costo e più tempo. Inoltre, quando il limite è
raggiunto, bisogna accorciare o selezionare il materiale.

## 5. Come nasce una risposta: il token successivo

Un LLM generativo stima quale token potrebbe venire dopo quelli già presenti.

Consideriamo:

```text
Il cielo sereno è
```

Il modello potrebbe assegnare queste probabilità semplificate:

```text
blu       0,70
luminoso  0,15
grigio    0,05
altro     0,10
```

Sceglie un token secondo la configurazione, lo aggiunge e ripete:

```text
Il cielo sereno è blu
```

Ora calcola il token successivo usando anche `blu`. Il ciclo continua fino a un
segnale di fine o al limite di output.

Questa spiegazione chiarisce un punto essenziale: il modello genera una continuazione
plausibile. Non apre automaticamente un archivio di fatti e non verifica ogni frase.
Può produrre una risposta fluida ma falsa.

## 6. Temperatura, limiti e allucinazioni

La **temperatura** regola quanto la scelta privilegia i token più probabili.

- temperatura bassa: output più stabile e concentrato;
- temperatura alta: più varietà e più rischio di deviazioni;
- temperatura zero: spesso più ripetibile, ma non garantisce identicità assoluta fra
  servizi o versioni.

Per classificare ticket conviene una temperatura bassa. Per proporre dieci slogan si
può accettare più varietà.

Un'**allucinazione** è un'informazione generata senza supporto affidabile. Per esempio,
il modello inventa un numero di procedura che non compare in alcuna fonte.

Cause comuni:

- la domanda richiede informazioni assenti;
- il prompt forza comunque una risposta;
- il contesto contiene fonti contraddittorie;
- il modello completa un modello linguistico plausibile, ma sbagliato.

Riduzioni pratiche del rischio:

1. permettere la risposta “informazioni insufficienti”;
2. validare il formato;
3. recuperare fonti attendibili quando servono fatti;
4. verificare nel codice numeri, permessi e regole;
5. misurare gli errori su esempi realistici.

Un LLM ha anche limiti di costo, latenza, contesto, conoscenza aggiornata e
prevedibilità. Non usarlo come unica barriera di sicurezza.

## 7. Messaggi system e user

Le interfacce conversazionali distinguono ruoli. Il messaggio **system**, cioè di
sistema, contiene istruzioni generali dell'applicazione. Il messaggio **user**, cioè
dell'utente, contiene la richiesta corrente.

```python
messages = [
    (
        "system",
        "Classifica ticket. Usa solo payroll, ferie o altro. "
        "Se mancano dati, usa altro.",
    ),
    ("user", "Non riesco a vedere il cedolino."),
]
```

Il messaggio di sistema serve a separare regole stabili e dati variabili. Non rende
però il sistema invulnerabile: autorizzazioni e controlli devono vivere nel codice.

## 8. JSON e Pydantic: trasformare testo in dati

**JSON**, acronimo di *JavaScript Object Notation*, è un formato testuale per
rappresentare oggetti, liste, numeri e stringhe. È utile perché il programma può
leggere campi noti invece di interpretare una frase libera.

**Pydantic** è una libreria Python che descrive e valida la forma dei dati. Questo
schema accetta solo categorie e priorità previste:

```python
from typing import Literal

from pydantic import BaseModel, Field


class TicketClassificato(BaseModel):
    categoria: Literal["payroll", "ferie", "altro"]
    priorita: Literal["bassa", "media", "alta"]
    sintesi: str = Field(min_length=5, max_length=120)
```

Se arriva `priorita="enorme"`, Pydantic genera un errore. La validazione non dimostra
che il contenuto sia vero; dimostra soltanto che rispetta il contratto.

## 9. Zero-shot e few-shot

**Zero-shot**, cioè “zero esempi”, significa descrivere il compito senza mostrare
coppie input-output:

```text
Classifica il ticket in payroll, ferie o altro.
Ticket: Vorrei spostare le ferie.
```

**Few-shot**, cioè “pochi esempi”, aggiunge alcuni casi:

```text
Ticket: Il cedolino non si apre.
Categoria: payroll

Ticket: Posso cambiare le ferie?
Categoria: ferie

Ticket: La tastiera non funziona.
Categoria: altro

Ora classifica:
Ticket: Non vedo la busta paga.
```

Gli esempi aiutano quando le categorie sono ambigue o il formato viene ignorato.
Consumano però contesto e possono trasmettere errori o distorsioni. Il confronto deve
avvenire sullo stesso insieme di test, non su una sola frase scelta a mano.

## 10. Programma completo: structured output senza chiave

**Structured output** significa output strutturato secondo uno schema. LangChain è una
libreria che offre interfacce comuni per modelli, messaggi e catene di operazioni.
Il metodo `with_structured_output` collega un modello a uno schema Pydantic.

Copia questo programma in `llm_strutturato.py`. Il modello è un **fake**, cioè un
sostituto controllato usato nei test. Non chiama internet e non richiede una chiave.

```python
from typing import Literal

from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field


class TicketClassificato(BaseModel):
    categoria: Literal["payroll", "ferie", "altro"]
    priorita: Literal["bassa", "media", "alta"]
    sintesi: str = Field(min_length=5, max_length=120)


class FakeChatModel:
    """Modello prevedibile per provare il contratto dell'applicazione."""

    def with_structured_output(self, schema: type[BaseModel]) -> RunnableLambda:
        def risposta_finta(messages: list[tuple[str, str]]) -> BaseModel:
            testo_utente = messages[-1][1].lower()
            if "cedolino" in testo_utente or "busta paga" in testo_utente:
                dati = {
                    "categoria": "payroll",
                    "priorita": "alta" if "urgente" in testo_utente else "media",
                    "sintesi": "Problema di accesso al cedolino",
                }
            elif "ferie" in testo_utente:
                dati = {
                    "categoria": "ferie",
                    "priorita": "media",
                    "sintesi": "Richiesta relativa alle ferie",
                }
            else:
                dati = {
                    "categoria": "altro",
                    "priorita": "bassa",
                    "sintesi": "Richiesta fuori dalle categorie note",
                }
            return schema.model_validate(dati)

        return RunnableLambda(risposta_finta)


def classifica_ticket(model: object, testo: str) -> TicketClassificato:
    modello_strutturato = model.with_structured_output(TicketClassificato)
    risultato = modello_strutturato.invoke(
        [
            (
                "system",
                "Classifica il ticket. Non inventare categorie o dettagli.",
            ),
            ("user", testo),
        ]
    )
    return TicketClassificato.model_validate(risultato)


if __name__ == "__main__":
    risultato = classifica_ticket(
        FakeChatModel(),
        "È urgente: non riesco a scaricare il cedolino.",
    )
    print(risultato.model_dump_json(indent=2))
```

Esegui:

```powershell
python llm_strutturato.py
```

Output atteso:

```json
{
  "categoria": "payroll",
  "priorita": "alta",
  "sintesi": "Problema di accesso al cedolino"
}
```

Il blocco `TicketClassificato` definisce il contratto. `FakeChatModel` restituisce dati
prevedibili. `classifica_ticket` usa `with_structured_output`, invia messaggi di
sistema e utente, poi valida di nuovo il risultato al confine dell'applicazione.

Quando vorrai eseguire una valutazione con un servizio reale, potrai sostituire il
fake senza cambiare `classifica_ticket`:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="NOME_MODELLO", temperature=0)
risultato = classifica_ticket(model, "Non vedo il cedolino.")
```

Questa seconda variante richiede configurazione e credenziali del fornitore. Non è
necessaria per completare il laboratorio.

## 11. Prima mappa delle tecniche successive

Non devi conoscerle già. Ti basta capire quale problema affrontano.

- **RAG**, da *Retrieval-Augmented Generation*, prima cerca documenti rilevanti e poi
  li inserisce nel contesto. Serve per conoscenza privata, aggiornata o citabile.
- **Tool calling**, cioè chiamata di strumenti, permette al modello di proporre una
  funzione e i suoi argomenti. Il codice valida ed esegue. Serve per leggere dati
  correnti o compiere azioni.
- **Fine-tuning**, cioè ulteriore addestramento, modifica il comportamento del modello
  usando molti esempi. Serve quando prompt ed esempi non bastano per un comportamento
  ripetuto. Non è la prima scelta per documenti che cambiano spesso.

Ordine prudente: prompt e schema; poi RAG o tool se mancano dati; fine-tuning solo
dopo misure ed analisi degli errori.

## 12. Laboratorio guidato

1. **Installa le dipendenze.** Esegui `pip install -e ".[ai]"`.
   Verifica: `python -c "import langchain_core, pydantic; print('ok')"` stampa `ok`.
2. **Crea il programma.** Copia il codice in `llm_strutturato.py`.
   Verifica: il file contiene una sola definizione di `TicketClassificato`.
3. **Esegui il caso payroll.**
   Verifica: categoria `payroll` e priorità `alta`.
4. **Cambia il testo in `Vorrei spostare le ferie`.**
   Verifica: categoria `ferie`.
5. **Prova `Il mouse è rotto`.**
   Verifica: categoria `altro`, senza eccezioni.
6. **Forza un errore nel fake.** Cambia temporaneamente la priorità in `urgente`.
   Verifica: Pydantic blocca il dato con un errore di validazione. Ripristina poi
   `alta`.
7. **Annota cinque ticket realistici e il risultato atteso.**
   Verifica: ogni ticket ha categoria, priorità e sintesi attese prima dell'esecuzione.

## 13. Esercizi graduati

### Base

1. Aggiungi la categoria `accessi`.
2. Classifica come `accessi` un testo che contiene “password”.
3. Aggiungi un campo booleano `richiede_risposta`.

### Intermedio

1. Rifiuta ticket più corti di 5 caratteri prima di chiamare il modello.
2. Crea cinque casi di test con `assert`.
3. Confronta una versione zero-shot e una few-shot del messaggio di sistema,
   conservando gli stessi casi attesi.

### Avanzato

Progetta una valutazione con almeno 30 ticket, casi ambigui e fuori dominio. Misura
accuratezza per categoria, percentuale di output validi, tempo e costo. Non usare la
confidenza dichiarata dal modello come prova di correttezza.

## 14. Soluzioni ragionate

Soluzione base:

```python
class TicketClassificato(BaseModel):
    categoria: Literal["payroll", "ferie", "accessi", "altro"]
    priorita: Literal["bassa", "media", "alta"]
    sintesi: str = Field(min_length=5, max_length=120)
    richiede_risposta: bool
```

Nel fake, il controllo `if "password" in testo_utente` deve venire prima del caso
generico `else`. Ogni dizionario deve includere `richiede_risposta`, per esempio
`True`. Pydantic segnala subito un ramo dimenticato.

Soluzione intermedia per validazione e test:

```python
def classifica_ticket(model: object, testo: str) -> TicketClassificato:
    if len(testo.strip()) < 5:
        raise ValueError("Il ticket deve contenere almeno 5 caratteri")
    modello_strutturato = model.with_structured_output(TicketClassificato)
    risultato = modello_strutturato.invoke(
        [("system", "Classifica senza inventare dati."), ("user", testo)]
    )
    return TicketClassificato.model_validate(risultato)


fake = FakeChatModel()
assert classifica_ticket(fake, "Problema cedolino").categoria == "payroll"
assert classifica_ticket(fake, "Vorrei ferie").categoria == "ferie"
assert classifica_ticket(fake, "Mouse rotto").categoria == "altro"
```

La validazione avviene prima della chiamata perché un input chiaramente invalido non
deve consumare tempo o denaro.

### Soluzione avanzata: criteri di verifica

Dividi almeno 30 ticket in categorie e casi fuori dominio prima di provare varianti.
Per ogni variante conserva lo stesso insieme di test e registra: accuratezza totale
e per categoria, percentuale di output Pydantic validi, latenza p50/p95 e costo
medio. Gli esempi few-shot si scelgono dai dati di sviluppo, non dai casi usati per
la misura finale. Analizza poi gli errori uno per uno e documenta quale modifica
intendi verificare nel prossimo esperimento.

## 15. Errori comuni

- **Pensare che il modello cerchi fatti automaticamente.** Genera token; per dati
  aggiornati serve una fonte o uno strumento.
- **Confondere formato valido e risposta corretta.** JSON valido può contenere una
  categoria sbagliata.
- **Mettere tutto nel prompt.** Contesto lungo significa costo e rumore; seleziona ciò
  che serve.
- **Alzare la temperatura per migliorare la qualità.** Aumenta varietà, non conoscenza.
- **Fidarsi di una singola prova.** Valuta molti casi normali, limite e ambigui.
- **Inserire segreti nei messaggi.** Prompt e trace possono essere registrati.
- **Lasciare categorie aperte.** Uno schema con valori consentiti riduce output
  inattesi.
- **Considerare il fake una prova del modello reale.** Il fake testa il codice; le
  capacità del modello richiedono una valutazione separata.

## 16. Domande di autoverifica

**Che cos'è un token?**  
Un'unità prodotta dal tokenizer: può essere parola, parte di parola o punteggiatura.

**Che cosa contiene il contesto?**  
Tutto ciò che il modello può considerare nella richiesta corrente.

**Perché una risposta fluida può essere falsa?**  
Perché il modello ottimizza una continuazione plausibile, non una verifica automatica
dei fatti.

**A che cosa serve Pydantic?**  
A validare forma, tipi e vincoli dei dati prodotti o ricevuti.

**Qual è la differenza fra zero-shot e few-shot?**  
Zero-shot non include esempi; few-shot include poche coppie input-output.

**Quando serve RAG?**  
Quando la risposta deve usare documenti aggiornati, privati o citabili.

**La temperatura zero garantisce sempre lo stesso risultato?**  
No. Riduce la variabilità, ma servizi, versioni e infrastruttura possono influire.

## Approfondimento tecnico

Solo dopo aver completato questa lezione, passa alla
[GUIDA tecnica su LLM, valutazione e tuning](GUIDA.md).
