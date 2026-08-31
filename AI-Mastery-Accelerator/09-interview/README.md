# 09 - Colloquio, system design e piano di mastery

**Inizia da qui:** [preparazione al colloquio passo-passo](LEZIONE.md).

Questa pagina è il manuale avanzato delle risposte modello.

## Risposte che devi saper dare

L'elenco seguente è una mappa degli argomenti. Le parentesi introducono subito
il significato dei termini; le sezioni successive spiegano meccanismo, esempio e
trade-off senza richiedere un glossario esterno.

### Python

- differenza fra processi, thread e `asyncio` (modello di concorrenza
  cooperativa della libreria standard);
- `Protocol` (interfaccia strutturale verificabile dall'analizzatore statico dei
  tipi) vs inheritance (ereditarietà nominale);
- iteratori e generatori (sequenze lazy, prodotte un elemento alla volta) per
  dataset grandi;
- timeout, retry, cancellation e context manager, cioè limite di tempo,
  nuovo tentativo, annullamento e gestione garantita delle risorse;
- progettazione testabile senza mockare tutto;
- profiling, cioè misura dei colli di bottiglia di CPU (*Central Processing
  Unit*), memoria e I/O (*Input/Output*, lettura o scrittura verso sistemi
  esterni).

### ML (Machine Learning)

- scegliere split (partizioni separate di train, validation e test) e metriche;
- diagnosticare leakage (informazione futura o indebita nel training),
  overfitting (adattamento eccessivo ai dati visti) e drift (cambiamento dei dati
  o della relazione da apprendere in produzione);
- calibrare probabilità, cioè allinearle alle frequenze osservate, e scegliere
  threshold, la soglia che trasforma uno score in una decisione;
- riproducibilità del training;
- differenze fra inferenza batch (a gruppi), online (richiesta-risposta) e
  streaming (su flusso continuo di eventi);
- rollout (rilascio graduale), monitoring (misura continua) e rollback (ritorno
  alla versione precedente) di un modello.

### LLM e RAG (*Large Language Model* e *Retrieval-Augmented Generation*)

Un LLM (*Large Language Model*) è un modello linguistico generativo. RAG
(*Retrieval-Augmented Generation*) significa recuperare fonti pertinenti e
fornirle al modello durante la generazione.

- RAG vs fine-tuning (addestramento ulteriore del modello) vs tool calling
  (invocazione strutturata di funzioni esterne);
- chunking (divisione dei documenti in unità recuperabili) e retrieval ibrido
  (ricerca lessicale più ricerca semantica);
- golden set, un dataset di valutazione curato con risultati attesi, e metriche
  per retrieval e generation;
- hallucination (affermazione non supportata), prompt injection (istruzione
  ostile inserita nei dati) e data leakage (esposizione di informazioni non
  autorizzate);
- caching (riuso di risultati memorizzati), latenza (tempo di risposta), token
  (unità di testo elaborata dal modello) e costi;
- valutare un cambio di modello.

### Agenti

- workflow deterministico, con passi stabiliti dal codice, vs agente, in cui il
  modello sceglie dinamicamente le azioni;
- stato, checkpoint (snapshot persistito da cui riprendere) e idempotenza
  (ripetere la stessa operazione senza duplicarne l'effetto logico);
- autorizzazione dei tool e *human-in-the-loop* (approvazione o intervento umano
  dentro il flusso);
- condizione di arresto e budget di passi, tempo, token o costo;
- test di traiettorie, cioè delle sequenze di stati, decisioni e tool;
- ragioni per evitare sistemi multi-agent, composti da più agenti coordinati.

### Data platform e MCP (*Model Context Protocol*)

MCP (*Model Context Protocol*) è un protocollo che standardizza come
un'applicazione scopre e usa contesto e strumenti esposti da server esterni.

- idempotenza, backfill (ricalcolo controllato dello storico), schema evolution
  (cambiamento compatibile della struttura) e data contract (accordo verificabile
  fra producer e consumer);
- modelli, test, lineage (tracciamento delle dipendenze) e caricamenti
  incrementali con dbt, strumento di trasformazione dati nel warehouse;
- dlt, libreria di ingestion, cioè acquisizione dei dati, e Airflow,
  orchestratore di task e dipendenze;
- micro-partitioning (suddivisione fisica automatica dei dati), virtual warehouse
  (cluster di calcolo) e controllo accessi in Snowflake;
- host MCP (applicazione principale), client (connessione al server), server
  (processo che espone capacità), resource (contenuto leggibile) e tool (funzione
  invocabile);
- propagazione dell'identità, autorizzazione e audit, cioè registrazione
  verificabile delle azioni;
- Docker, piattaforma per immagini e container, IAM (*Identity and Access
  Management*), ECS (*Elastic Container Service*) con Fargate, esecuzione gestita
  di container, segreti e osservabilità su AWS (*Amazon Web Services*).

## Risposte modello

Queste non sono formule da recitare. Una buona risposta parte dal requisito, rende
esplicite le assunzioni, propone una misura e discute almeno un trade-off.

### Python

#### Processi, thread e `asyncio`

Un carico **CPU-bound** passa la maggior parte del tempo a calcolare sulla CPU;
un carico **I/O-bound** passa invece il tempo ad attendere rete, disco o altri
sistemi. Il **GIL** (*Global Interpreter Lock*) di CPython è il lock che, nelle
build tradizionali dell'interprete, permette a un solo thread per processo di
eseguire bytecode Python alla volta.

I **processi** hanno memoria separata e ciascuno ha il proprio interprete: sono
quindi adatti a calcolo CPU-bound, isolamento e parallelismo reale, ma hanno
costi maggiori di avvio, memoria e serializzazione. I **thread** condividono
memoria e sono utili per I/O bloccante o librerie native che rilasciano il GIL;
richiedono però sincronizzazione e possono introdurre *race condition*, errori
in cui il risultato dipende dall'ordine imprevedibile delle operazioni.
`asyncio` usa normalmente un solo thread e *cooperative scheduling*: ogni
coroutine cede esplicitamente il controllo durante un'attesa. Scala bene con
molte operazioni I/O concorrenti, purché l'intera catena sia non bloccante.

La scelta deriva dal carico:

| Carico | Scelta iniziale | Motivo |
|---|---|---|
| preprocessing numerico CPU-bound | process pool o libreria vettorizzata | parallelismo CPU |
| chiamate HTTP (*Hypertext Transfer Protocol*) concorrenti | `asyncio` | molte attese, overhead contenuto |
| SDK (*Software Development Kit*) solo sincrono e I/O-bound | thread pool limitato | integra codice bloccante |
| isolamento forte di un worker | processo/container | failure e risorse separate |

Non basta rendere una funzione `async`: una chiamata bloccante dentro l'event
loop ferma tutte le coroutine. Imposterei limiti di concorrenza, timeout e
**backpressure**, cioè rallentamento o rifiuto controllato di nuovo lavoro quando
il sistema è pieno. Misurerei throughput, il lavoro completato per unità di
tempo, p95/p99, i tempi sotto cui termina rispettivamente il 95% e il 99% delle
richieste, CPU, memoria e saturazione delle risorse prima di decidere.

#### `Protocol` vs inheritance

`typing.Protocol` è il costrutto Python per dichiarare un'interfaccia
strutturale: il type checker accetta qualunque oggetto che possieda metodi e
attributi richiesti. L'ereditarietà nominale richiede invece una relazione
esplicita *is-a* con una classe base e può condividere implementazione,
invarianti e ciclo di vita. È appropriata quando la classe base controlla davvero
il contratto; `Protocol` riduce l'accoppiamento ed è utile ai confini
dell'applicazione.

```python
from typing import Protocol

class Retriever(Protocol):
    def search(self, query: str, *, limit: int) -> list[str]: ...

def answer(query: str, retriever: Retriever) -> str:
    docs = retriever.search(query, limit=5)
    return synthesize(query, docs)
```

In questo esempio produzione e test possono fornire implementazioni diverse
senza dipendere da una gerarchia. Non userei però `Protocol` per nascondere
contratti vaghi: semantica degli errori, timeout e invarianti devono comunque
essere documentati e testati.

#### Iteratori e generatori per dataset grandi

Un iteratore espone `__iter__`/`__next__`; un generatore è un modo compatto per
crearlo con `yield`. Entrambi permettono elaborazione lazy e memoria circa
proporzionale al batch, non al dataset. Per un file grande leggerei record a
stream, li trasformerei e produrrei batch senza costruire una lista completa:

```python
from collections.abc import Iterable, Iterator

def batches(rows: Iterable[str], size: int) -> Iterator[list[str]]:
    batch: list[str] = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch
```

I trade-off sono che un generatore è spesso consumabile una sola volta, gli
errori emergono durante l'iterazione e alcune operazioni globali, come shuffle
perfetto o quantili esatti, richiedono stato. Per pipeline lunghe aggiungerei
checkpoint, conteggi e gestione esplicita delle risorse.

#### Timeout, retry, cancellation e context manager

Un timeout limita il tempo concesso a un tentativo; un retry ripete solo errori
transitori. L'**idempotenza** è la proprietà per cui ripetere la stessa
operazione produce un solo effetto logico, per esempio un solo ticket.
Imposterei timeout distinti per connessione e risposta, retry con *exponential
backoff* (attese progressivamente più lunghe) e *jitter* (piccola casualità per
evitare retry simultanei), numero massimo di tentativi e un **deadline
complessivo**. Non ritenterei errori di validazione o autorizzazione. Per
operazioni con effetti esterni userei una chiave di idempotenza, altrimenti il
retry può duplicare l'effetto.

La cancellation deve propagarsi: una coroutine cancellata chiude task figli e
risorse, senza trasformare indiscriminatamente `CancelledError` in successo. Un
context manager garantisce cleanup anche su eccezione:

```python
async with client.stream("GET", url, timeout=timeout) as response:
    async for chunk in response.aiter_bytes():
        consume(chunk)
```

In produzione aggiungerei circuit breaker solo quando evita pressione su una
dipendenza già guasta, metriche per tentativo/esito e un budget di retry
inferiore al budget di latenza end-to-end.

#### Progettazione testabile senza mockare tutto

Separerei logica pura da I/O: il dominio riceve dati e restituisce decisioni,
mentre database, clock, random, modelli e client HTTP stanno dietro interfacce
piccole iniettate dall'esterno. Testerei la logica con valori reali, gli adapter
con integration test contro dipendenze realistiche e pochi end-to-end sui flussi
critici. Preferirei fake in memoria con comportamento credibile ai mock che
verificano ogni chiamata interna.

Un test fragile dice “è stato chiamato il metodo X due volte”; un test utile dice
“a parità di richiesta e chiave idempotente viene creato un solo ticket”. I mock
restano utili per errori difficili da riprodurre, clock o callback, ma non devono
replicare l'intera implementazione.

#### Profiling CPU, memoria e I/O

Prima riproduco il problema con un carico rappresentativo e stabilisco una
**baseline**, la misura di riferimento con cui confrontare ogni modifica. Per
CPU uso profiler statistici o `cProfile` e guardo tempo cumulativo,
non solo il metodo più lento. Per memoria osservo RSS (*Resident Set Size*, la
memoria fisica occupata dal processo) nel tempo, allocazioni e oggetti trattenuti con
`tracemalloc`; distinguo picco, perdita e memoria tenuta da cache. Per I/O misuro
DNS (*Domain Name System*), connessione, TLS (*Transport Layer Security*) e TTFB
(*Time To First Byte*, tempo fino al primo byte), oltre a query lente,
saturazione dei pool e attese dell'event loop.

Profilo in un ambiente vicino alla produzione e ottimizzo il collo di bottiglia
dominante. Dopo la modifica ripeto lo stesso benchmark e verifico anche
correttezza e regressioni: una cache che dimezza la latenza ma usa memoria senza
limite non è un miglioramento completo.

### ML

#### Split e metriche

Uno **split** divide gli esempi in training, validation e test: il primo stima i
parametri, il secondo sceglie configurazione e soglie, il terzo misura una sola
volta la generalizzazione finale. Deve simulare l'uso futuro. Per dati IID
(*independent and identically distributed*, indipendenti e generati dalla stessa
distribuzione) può bastare uno split stratificato; per serie temporali serve uno
split temporale; per più eventi dello stesso utente, paziente o macchinario uso
un *group split* per impedire contaminazione fra train e test. Tengo il test
finale congelato e uso train/validation o *cross-validation*, cioè più rotazioni
degli split, per la selezione.

La metrica deriva dal costo dell'errore e dalla prevalenza. *Precision* è la
quota di predizioni positive corrette; *recall* è la quota di positivi reali
trovati. PR-AUC (*Precision-Recall Area Under the Curve*) è l'area sotto la curva
precision-recall ed è informativa quando la classe positiva è rara. ROC-AUC
(*Receiver Operating Characteristic Area Under the Curve*) è l'area sotto la
curva che confronta tasso di veri e falsi positivi a tutte le soglie; può
apparire ottimistica con forte
sbilanciamento. *Log loss* penalizza probabilità errate e troppo sicure.
L'accuracy può quindi essere fuorviante. Per un sistema decisionale valuto la
metrica alla soglia operativa e, quando possibile, costo o utilità attesa. Non
esiste una soglia universale: va scelta con stakeholder, vincoli e dati
rappresentativi.

#### Leakage, overfitting e drift

Il **leakage** è l'uso nel training di informazioni che non saranno disponibili
al momento della previsione: feature, cioè variabili date in input al modello,
calcolate usando eventi futuri, preprocessing adattato su tutto il
dataset, duplicati o entità condivise tra split. Produce metriche artificialmente
alte. Lo cerco con lineage temporale, *ablation* (rimozione controllata di feature
o componenti), split più realistici e confronto fra disponibilità offline e
online.

L'**overfitting** è l'adattamento eccessivo ai dati visti, osservabile come un
divario fra train e validation; intervengo con più dati, regolarizzazione,
modello più semplice, *early stopping* o una validation migliore. Il **drift** è
un cambiamento in produzione: può variare la distribuzione degli input `P(X)`,
la relazione fra input e target `P(Y|X)` o la prevalenza del target. Per esempio,
una nuova campagna può cambiare il mix di utenti senza rendere il modello meno
accurato. Monitoro feature, predizioni e outcome quando arrivano, per segmento e
con baseline stagionali. Un test statistico da solo non decide il retraining:
serve collegare il drift all'impatto sulle prestazioni.

#### Calibrazione e threshold

La **calibrazione** misura se una probabilità predetta corrisponde alla frequenza
osservata: fra casi stimati intorno a 0,8, circa l'80% dovrebbe essere positivo
nel contesto valutato. Verifico un *reliability diagram*, che confronta
probabilità e frequenze per intervalli, il Brier score, errore quadratico delle
probabilità, e la log loss su un set separato. Se necessario applico Platt
scaling, una regressione logistica sugli score, oppure isotonic regression, una
mappatura monotona più flessibile, senza adattarle sul test.

Il threshold è una decisione di prodotto, non una proprietà intrinseca del
modello. Lo scelgo minimizzando un costo atteso o rispettando vincoli, per
esempio recall minimo o capacità massima della review manuale. Possono servire
threshold diversi per segmenti solo se giustificati, legali e monitorabili.
Ricalibro e rivaluto le soglie quando cambiano prevalenza o costi.

#### Riproducibilità del training

Versiono codice, configurazione, dati o snapshot, schema, feature, split,
dipendenze, immagine, seed e artefatti. Registro hardware, versione delle
librerie, metrica e modello prodotto. I seed non garantiscono sempre
determinismo su GPU (*Graphics Processing Unit*) o algoritmi paralleli; documento
quindi il livello atteso: bitwise, stessa metrica entro tolleranza o stessa
decisione di promozione.

La pipeline deve poter ricostruire un modello da un identificatore di run e
validare data contract e lineage. Un model registry non sostituisce la
riproducibilità se il dataset originale o la trasformazione non sono
ricostruibili.

#### Batch, online e streaming inference

L'**inferenza** è l'uso di un modello addestrato per produrre una previsione.

| Modalità | Uso | Vantaggio | Rischio principale |
|---|---|---|---|
| batch | scoring periodico di molti record | throughput e costo | predizioni non fresche |
| online | richiesta/risposta a bassa latenza | decisione aggiornata | disponibilità e p99 |
| streaming | evento continuo con stato/window | reazione quasi real-time | ordering, replay, stato |

In batch pianifico partizioni, retry e output idempotenti. Online considero
**autoscaling**, aumento o riduzione automatica delle repliche in base al carico,
parità delle feature fra training e serving, timeout e fallback.
Streaming richiede *event time*, l'istante in cui l'evento è avvenuto, e
*watermark*, una stima di quanto il flusso sia avanzato che permette di chiudere
finestre pur accettando eventi in ritardo. Richiede inoltre deduplica e
checkpoint. Con semantica **at least once** un evento può essere consegnato più
volte; **exactly once** significa un solo effetto logico end-to-end ed è una
proprietà da dimostrare, non un'etichetta del broker. Spesso batch o micro-batch
soddisfano il requisito a minor costo.

#### Rollout, monitoring e rollback

Il **rollout** è l'introduzione graduale di una nuova versione; il **monitoring**
è la misura continua del suo comportamento; il **rollback** ripristina una
versione precedente. Prima del deploy confronto il candidato con la baseline su
test congelato, segmenti, robustezza e requisiti operativi. Poi uso **shadow
traffic**, una copia delle richieste elaborata senza influenzare l'utente, oppure
un **canary**, una piccola quota realmente servita dalla nuova versione. Un A/B
test assegna invece utenti comparabili a varianti diverse per misurare un effetto
causale. Applico **guardrail**, limiti che fermano il rollout se peggiorano
qualità, errori, latenza, costo o KPI (*Key Performance Indicator*, indicatore
di risultato aziendale). Versiono insieme modello, feature e configurazione.

Monitoro qualità input, schema, drift, distribuzione delle predizioni, metriche
operative e outcome ritardati. Il rollback, cioè il ritorno alla versione
precedente, deve essere provato e rapido:
riattivare modello/configurazione precedenti, mantenendo compatibilità con
feature e schema. Definisco prima del rollout criteri di stop; i valori dipendono
dal rischio e dallo SLO (*Service Level Objective*, obiettivo misurabile di
affidabilità o prestazione), non da percentuali universali.

### LLM/RAG

#### RAG vs fine-tuning vs tool calling

**RAG** recupera documenti al momento della domanda e li inserisce nel contesto
del modello; lo uso quando la risposta dipende da conoscenza privata, ampia o
aggiornata e voglio citazioni. Il **fine-tuning** aggiorna i pesi del modello con
esempi aggiuntivi; lo uso per cambiare comportamento stabile, formato o stile,
non come memoria affidabile di fatti mutevoli. Il **tool calling** fa produrre al
modello nome e argomenti strutturati di una funzione che l'applicazione valida ed
esegue; serve per leggere stato autorevole in tempo reale o compiere un'azione,
per esempio controllare un ordine o aprire un ticket.

Le tecniche possono coesistere: un modello fine-tuned può scegliere strumenti e
rispondere su contesto recuperato. Partirei dalla baseline più semplice e
confronterei qualità, latenza, rischio e costo. Non userei RAG per dati
transazionali che devono essere letti da un'API (*Application Programming
Interface*, interfaccia software fra sistemi) autorizzata.

#### Chunking e retrieval ibrido

Il **chunking** divide un documento in unità indicizzabili. Deve rispettare la
struttura semantica: titoli, paragrafi, tabelle e codice. Chunk troppo piccoli
perdono contesto; troppo grandi diluiscono il segnale e consumano token. Un
**embedding** è un vettore numerico che rappresenta il significato di testo o
altri dati e permette di cercare elementi semanticamente vicini. Conservo
metadata, gerarchia, versione e ACL (*Access Control List*, regole che indicano
chi può leggere una risorsa); valuto dimensione e sovrapposizione sul golden set,
non solo “a occhio”.

Il **retrieval ibrido** combina ricerca lessicale e semantica. BM25 è un
algoritmo di ranking lessicale che premia termini presenti nella query tenendo
conto di frequenza e lunghezza del documento; è efficace per codici e nomi rari.
Il *dense retrieval* confronta invece embedding per similarità semantica.
Normalizzo e fondo i ranking, applico filtri autorizzativi prima di esporre
risultati e, se il budget lo consente, faccio **reranking**: un secondo modello
riordina un piccolo insieme di candidati con una valutazione più accurata ma più
costosa. Misuro recall a `k`, MRR (*Mean Reciprocal Rank*, quanto in alto compare
il primo risultato utile), nDCG (*normalized Discounted Cumulative Gain*,
qualità dell'intero ordine), precisione del contesto e qualità finale. Aumentare
`k` non garantisce una risposta migliore.

#### Golden set e metriche

Un **golden set** è un dataset di valutazione curato. Contiene query reali o
rappresentative, intento, fonti attese, risposta o criteri di correttezza, casi
senza risposta, segmenti e severità. Versiono dataset e *rubric*, cioè regole
esplicite di valutazione; separo set di sviluppo e set di valutazione per non
ottimizzare continuamente sugli stessi esempi.

Valuto a strati:

- **retrieval:** Recall@k, MRR/nDCG, precisione e copertura per segmento;
- **generation:** correttezza, *groundedness* o *faithfulness*, cioè supporto
  effettivo delle affermazioni nelle fonti, completezza e citazioni;
- **sistema:** task success, tasso di astensione corretto, latenza e costo;
- **produzione:** feedback e outcome, analizzati senza assumere che un click sia
  sempre qualità.

Un **LLM judge** usa un modello linguistico per assegnare un voto secondo una
rubric. Va calibrato con annotazioni umane, ordine randomizzato e controlli di
bias; non è una verità assoluta.

#### Hallucination, prompt injection e data leakage

Una **hallucination** è un'affermazione generata senza supporto sufficiente nelle
fonti o nei dati autorevoli. Per ridurla limito le fonti, richiedo evidenze,
verifico che le citazioni supportino davvero le affermazioni e consento
l'astensione. Una **prompt injection** è testo ostile che tenta di farsi trattare
come istruzione privilegiata; è un problema di *trust boundary*, il confine fra
componenti affidabili e dati non fidati. Documenti e output dei tool sono dati,
non istruzioni. Separo policy di sistema, contenuto recuperato e risultato dei
tool; applico allowlist, validazione degli argomenti e autorizzazione lato server
per ogni azione.

Il **data leakage** è l'esposizione di dati oltre lo scopo autorizzato. Contro
questo rischio filtro retrieval e cache per tenant, organizzazione isolata che
condivide il servizio, e utente; propago ACL,
minimizzo PII (*Personally Identifiable Information*, dati che identificano una
persona), cifro dati e log e definisco conservazione e redazione. Non affido al
prompt il controllo accessi: il modello non deve mai vedere dati che il chiamante
non è autorizzato a leggere.

#### Caching, latenza, token e costi

Una **cache** conserva risultati riutilizzabili per evitare calcolo o chiamate
ripetute. La **latenza** è il tempo percepito dalla richiesta alla risposta; un
**token** è un'unità di testo elaborata dal modello, non necessariamente una
parola. Misuro latenza per fase: coda, retrieval, reranking, tempo fino al primo
token, generazione e tool. Riduzione del prompt, modelli più piccoli,
parallelismo controllato, streaming e retrieval selettivo spesso aiutano più di
una cache indiscriminata. Distinguo cache di embedding, retrieval, prefissi del
prompt e risposta.

La chiave di cache deve includere almeno versione di modello/prompt/indice,
identità o ambito autorizzativo e parametri rilevanti. Definisco TTL (*Time To
Live*, durata massima dell'elemento in cache) e
invalidazione al cambio dei dati; non condivido risposte personalizzate fra
tenant. Ottimizzo costo per task riuscito, non costo per singola chiamata: un
modello economico che richiede più retry o review umana può costare di più.

#### Valutare un cambio di modello

Congelo un set rappresentativo e confronto incumbent e candidato con lo stesso
prompt, strumenti e dati. Misuro qualità per segmento, sicurezza, aderenza al
formato/tool schema, latenza, rate limit, stabilità, token e costo end-to-end.
Eseguo anche test di regressione su casi critici e carico.

Se il candidato supera i criteri minimi, procedo con shadow/canary e osservo
traffico reale. Mantengo adapter e versioni per rollback. Non promuovo un modello
solo perché vince una media: può regredire su lingue, long context o tool calling
essenziali.

### Agenti

#### Workflow deterministico vs agente

Un **workflow deterministico** codifica in anticipo passi e transizioni: a parità
di input e stato segue regole note, quindi è più prevedibile e testabile. Un
**agente** delega invece al modello la scelta dinamica della prossima azione fra
strumenti e percorsi possibili; serve quando i percorsi non sono enumerabili o
la selezione richiede interpretazione. Preferisco un workflow con nodi LLM dove
possibile e introduco autonomia solo nel punto che porta valore.

La domanda chiave non è “posso usare LangGraph?”, ma “quale decisione non riesco
a modellare deterministicamente?”. Paghiamo l'agente con maggiore varianza,
superficie di sicurezza, latenza e difficoltà di debug.

#### Stato, checkpoint e idempotenza

Lo **stato** è l'insieme minimo di informazioni necessarie per decidere il passo
successivo. Un **checkpoint** è una sua copia persistita e versionata da cui un
worker può riprendere dopo un crash. Conservo input validato, passo corrente,
output strutturati, tentativi, budget e riferimenti agli artefatti, e salvo un
checkpoint dopo transizioni significative.

Ogni effetto esterno usa un identificatore di operazione e una chiave di
idempotenza stabili e registra `pending/completed/failed`. Il checkpoint da solo
non evita duplicati: un crash può avvenire dopo l'effetto esterno ma prima del
salvataggio. Servono API idempotenti, pattern **outbox/inbox** — registri
persistenti di messaggi da inviare o già ricevuti — oppure riconciliazione.

#### Authorization e human-in-the-loop

Il modello propone; un **policy enforcement point**, componente deterministico
che applica le regole di accesso, decide se l'identità può usare il tool su quella
risorsa con quegli argomenti. Uso credenziali limitate nello scopo e nella
durata, validazione dello schema e una lista esplicita di strumenti consentiti.
Per azioni irreversibili, ad alto impatto o ambigue inserisco approvazione umana
con anteprima, motivazione, differenza rispetto allo stato corrente e scadenza.

L'approvazione non deve essere un bottone opaco “OK”: l'utente deve sapere cosa
accadrà. Dopo l'approvazione ricontrollo autorizzazione e stato, perché potrebbero
essere cambiati.

#### Stop condition e budget

Definisco limiti duri su passi, tempo, token, costo, retry e chiamate per tool,
oltre a condizioni semantiche di successo, fallimento e impossibilità. Rilevo
loop tramite firme di stato/azione e vieto retry senza nuova informazione.

Al superamento del budget l'agente deve degradare in modo utile: restituire
risultato parziale, chiedere approvazione o passare a operatore, non terminare
silenziosamente. I limiti sono calibrati sui task e sugli SLO.

#### Test di sistemi non deterministici

Un sistema è **non deterministico** quando lo stesso input può produrre
traiettorie o testi diversi. Testo separatamente nodi deterministici, schema e
policy; uso implementazioni finte ma realistiche dei tool per errori ed effetti
esterni; valuto traiettorie su dataset con più esecuzioni quando la varianza
conta. Non asserisco la stringa esatta, ma invarianti: nessun tool non
autorizzato, citazioni valide, budget rispettato, stato terminale corretto e
risultato entro rubric.

Registro trace, prompt, modello, tool input/output e seed quando disponibile.
Confronto distribuzioni e tassi di successo con intervalli di confidenza, poi
mantengo una piccola suite end-to-end contro servizi reali.

#### Perché evitare multi-agent

Un sistema **multi-agent** coordina più agenti, ognuno con contesto, ruolo o
strumenti propri. Può essere utile quando ruoli hanno permessi o obiettivi
realmente distinti e il parallelismo compensa il costo. Spesso però replica
prompt, aumenta token e latenza, crea passaggi di consegne che perdono
informazione, rende difficile attribuire errori e amplia la superficie
autorizzativa.

Prima provo un singolo orchestratore con tool e subworkflow deterministici.
Introduco un altro agente solo con un'ipotesi misurabile, per esempio ridurre il
tempo grazie a ricerche indipendenti, e confronto task success, costo e failure
rate con la baseline.

### Data platform, MCP, Docker e AWS

#### Idempotenza, backfill, schema evolution e data contract

Una pipeline è **idempotente** se rieseguire la stessa partizione produce lo
stesso stato logico. Chiavi naturali o stabili, `MERGE` — istruzione SQL che
aggiorna le chiavi esistenti e inserisce quelle nuove — deduplica e watermark
tracciati evitano duplicati. Un **backfill** ricalcola dati storici per un
intervallo e una versione specifici; lo tratto come una normale esecuzione
parametrizzata, isolata dal flusso corrente, con risorse limitate, validazioni e
possibilità di sostituire atomicamente le partizioni.

La **schema evolution** è il cambiamento nel tempo di colonne, tipi e semantica;
distinguo modifiche additive, compatibili e incompatibili. Un **data contract**
formalizza fra produttore e consumatore schema, nullability, semantica, owner,
freshness e aspettative verificabili. Per una modifica incompatibile uso doppia
scrittura o lettura, oppure una vista compatibile, migro i consumer e rimuovo la
vecchia versione solo dopo verifica.

#### dbt

dbt è uno strumento che applica pratiche di ingegneria del software alle
trasformazioni nel warehouse. Organizzo fonti, staging, livelli intermedi e
mart, mantenendo trasformazioni SQL (*Structured Query Language*) versionate.
Uso test built-in (`not_null`, `unique`, `relationships`,
`accepted_values`) e test custom per invarianti di business; documentazione ed
exposure rendono visibili **lineage**, cioè la catena di dipendenze e
trasformazioni, e consumer.

Un **modello incrementale** elabora solo dati nuovi o cambiati invece di
ricostruire sempre tutta la tabella. Deve dichiarare chiave unica, strategia di merge,
lookback per eventi in ritardo e comportamento su full refresh. Verifico che una
riesecuzione non duplichi dati e che modifiche alla logica storica attivino un
backfill controllato. I test dbt sono gate di qualità, non sostituti del
monitoring di freshness e volume.

#### dlt e Airflow

dlt è una libreria di ingestion che estrae, normalizza e carica dati da API,
file o database, gestendo stato incrementale e schema. Airflow è un orchestratore
che pianifica e osserva dipendenze, retry, SLA (*Service Level Agreement*,
impegno contrattuale sul servizio) e backfill fra task e sistemi. Evito di
incapsulare tutta la logica in un DAG (*Directed Acyclic Graph*, grafo orientato
senza cicli usato per esprimere dipendenze): il codice di ingestion e
trasformazione deve restare eseguibile e testabile fuori dall'orchestratore.

Configuro task idempotenti, pool e concurrency limit, timeout, alert utili e
retry solo su errori transitori. Per un backfill considero pressione su sorgente
e warehouse e separo data interval da ora di esecuzione.

#### Snowflake

In Snowflake una **micro-partition** è un'unità fisica immutabile di storage,
creata automaticamente con metadata sui valori. Il **pruning** evita di leggere
micro-partition incompatibili con i filtri. Osservo profilo delle query e dati
scansionati prima di introdurre una clustering key, che migliora la disposizione
ma ha un costo di mantenimento. Un **virtual warehouse** è il cluster di calcolo
separato dallo storage: separo warehouse per carico quando serve isolamento,
scelgo sospensione automatica e dimensione in base a concorrenza e latenza e
controllo code e scritture temporanee su disco.

Per il controllo accessi preferisco RBAC (*Role-Based Access Control*), nel quale
i permessi sono assegnati a ruoli, con **least privilege**, cioè solo i privilegi
minimi necessari. Uso database role, viste sicure, mascheramento e policy a
livello di riga per dati sensibili. Monitoro storico accessi, query e costi;
resource monitor e budget alert sono limiti di sicurezza, non una strategia
completa di ottimizzazione.

#### Componenti MCP

In MCP, l'**host** è l'applicazione che coordina l'esperienza e crea uno o più
**client**, connettori che mantengono una sessione con un **server**. Il server
espone capability come **tool**, funzioni invocabili per leggere o modificare
stato, e **resource**, contenuti indirizzabili che il client può leggere;
eventuali prompt sono template offerti dal server. Il protocollo standardizza
scoperta e invocazione, non rende automaticamente sicuro il tool.

Il server valida input, autorizza ogni richiesta, applica limiti e restituisce
errori strutturati. L'host deve trattare descrizioni e output come non fidati,
mostrare approval dove necessario e non concedere a tutti i server le stesse
credenziali.

#### Identità, autenticazione, autorizzazione e audit

L'**autenticazione** stabilisce chi chiama; l'**autorizzazione** decide se può
eseguire una determinata azione su una risorsa. Propago identità e contesto del
servizio senza passare token onnipotenti al modello. Preferisco token con scopo,
destinatario e durata limitati e delega esplicita; per job asincroni salvo
riferimenti sicuri, non credenziali nei checkpoint.

L'**audit** è una traccia verificabile di chi ha fatto cosa, quando e con quale
esito. Collega attore, tenant, richiesta, decisione di policy, tool, argomenti
redatti, risultato, timestamp e identificatore di correlazione. I log sono
append-only, cioè aggiungibili ma non modificabili ordinariamente, e protetti,
con conservazione e accesso coerenti alla sensibilità. Audit non significa
registrare prompt completi con segreti o PII.

#### Docker e AWS

Docker impacchetta applicazione e dipendenze in un'immagine eseguita come
container isolato a livello di sistema operativo. Creo immagini multi-stage,
minimali, con versioni fissate e scansionate; eseguo come utente non root, con
filesystem in sola lettura quando possibile, health check e arresto ordinato.
Configurazione e segreti non entrano nell'immagine.

Su AWS, ECS con Fargate esegue container senza gestire direttamente i server
sottostanti ed è adatto a servizi stateless, che non conservano stato locale
necessario fra richieste. Metto un ALB (*Application Load Balancer*) o API
Gateway davanti al servizio, uso autoscaling su segnali coerenti con il collo di
bottiglia e distribuisco task su più Availability Zone, zone fisicamente
separate nella stessa regione. IAM è il sistema AWS che assegna identità,
policy e permessi: ogni task assume un ruolo IAM con privilegi minimi, distinto
dal ruolo usato per scaricare l'immagine e avviare il container. Per esempio, il
servizio può leggere un solo secret e scrivere su una specifica coda, senza
accesso amministrativo. Secrets Manager o Parameter Store forniscono segreti con
rotazione; KMS (*Key Management Service*) gestisce le chiavi usate per cifrare i
dati. Policy più granulari migliorano l'isolamento ma aumentano il lavoro di
gestione e test.

Per produzione aggiungo log strutturati, metriche RED (*Rate, Errors, Duration*:
volume, errori e durata), trace distribuite e identificatori di correlazione,
allarmi sugli SLO e dashboard di dipendenze e costi. Un trace distribuito collega
le fasi della stessa richiesta attraverso più servizi. Deploy
blue-green o canary e una revisione della compatibilità dati rendono il rollback
praticabile. Il numero di task, le soglie di scaling e i timeout dipendono dal
profilo misurato.

## Traccia di system design: support assistant

In 45 minuti:

1. chiarisci utenti, volume, dati, SLO (*Service Level Objective*, obiettivo
   quantitativo del servizio) e rischio;
2. definisci baseline e non-obiettivi;
3. disegna ingestion, retrieval, orchestration e serving;
4. approfondisci due componenti critici;
5. tratta eval, sicurezza, observability e costo;
6. descrivi failure mode, degradation e rollback;
7. spiega evoluzione da MVP (*Minimum Viable Product*, prima versione minima
   utile) a 100x traffico.

Evita di iniziare con il nome di un framework. Parti dai requisiti e giustifica ogni
componente.

### Risposta modello completa

#### 1. Requirements e non-obiettivi

Progetto un assistente per clienti e operatori che risponde su documentazione
approvata, legge dati dell'account tramite API e, con conferma, apre o aggiorna
ticket. Un requirement è un bisogno o vincolo verificabile; un non-obiettivo
delimita esplicitamente ciò che la prima versione non farà. Prima chiarisco:

- canali, lingue, utenti, tenant e accessibilità;
- volume medio/picco, crescita, lunghezza delle conversazioni e concorrenza;
- fonti, frequenza di aggiornamento, ownership e vincoli di residenza;
- azioni consentite e casi che richiedono un operatore;
- SLO di disponibilità e latenza per classe di richiesta;
- costo degli errori: risposta inesatta, esposizione dati, azione errata.

SLO e target numerici vanno definiti dai requisiti, non copiati da altri sistemi.
Misurerei almeno availability, p95/p99, task success, grounded answer rate,
correct escalation rate e costo per conversazione riuscita. Non-obiettivi
iniziali: risolvere ogni richiesta, modificare dati senza conferma, apprendere
automaticamente da chat non revisionate o sostituire il sistema ticketing.

#### 2. Baseline

Parto con ricerca documentale più risposta citata e passaggio a un operatore.
Per FAQ (*Frequently Asked Questions*, domande frequenti) note mantengo anche una
baseline deterministica basata sulla sola ricerca. Questo stabilisce se
l'orchestrazione LLM porta un miglioramento reale rispetto a ricerca e template,
e offre una degradazione sicura.

#### 3. Architettura

```text
Fonti approvate -> ingestion/versioning -> parser/chunker -> indici sparse+dense
                                                       \-> metadata/ACL store

Client -> API/Auth -> conversation service -> policy/orchestrator
                                      |          |-> retrieval + reranker
                                      |          |-> model gateway
                                      |          |-> tool gateway -> sistemi aziendali
                                      |          \-> human approval/escalation
                                      |
                                      \-> state/checkpoint

Tutti i componenti -> trace, metriche, audit, eval store
```

- **API/Auth:** l'interfaccia applicativa e il componente di autenticazione
  verificano utente e tenant, applicano un limite di richieste e creano un
  identificatore di correlazione.
- **Conversation service:** conserva stato minimo, preferenze e riferimenti,
  cifrati e con retention.
- **Orchestrator:** classifica il percorso: FAQ/RAG, lettura via tool, azione con
  approvazione, oppure escalation. LangGraph o un workflow equivalente è
  un'implementazione possibile, non il requisito.
- **Retrieval:** filtri ACL e versione prima del ranking, ricerca ibrida,
  reranking e costruzione di contesto con citazioni.
- **Model gateway:** un punto di accesso uniforme a più modelli, con timeout,
  budget, scelta del modello, osservabilità e rollback di modello o prompt.
- **Tool gateway:** schema validation, policy, idempotency key, credential
  scoping e audit; il modello non chiama direttamente i sistemi core.
- **Human handoff:** il passaggio a un operatore trasferisce sintesi, evidenze,
  azioni tentate e stato, senza obbligarlo a ricominciare.

#### 4. Data flow

**Ingestion:** il sistema produttore pubblica una versione; la pipeline valida
contratto, malware e formati, estrae struttura, rimuove o classifica dati
personali identificativi (PII), crea chunk con
metadata/ACL e scrive un nuovo indice immutabile. Una suite di retrieval eval e
controlli di conteggio/freshness precede lo switch atomico dell'alias. La
versione precedente resta disponibile per rollback.

**Query:** l'API autentica, normalizza l'input e recupera scope e policy. Il
router sceglie il flusso. Per RAG, il retriever applica ACL, recupera candidati
ibridi, reranka e restituisce passaggi con provenance. Il modello produce una
risposta strutturata con citazioni oppure si astiene. Per dati account usa un
tool read-only autorizzato. Per side effect produce una proposta; il gateway
mostra l'anteprima, raccoglie conferma e invoca l'API con chiave idempotente.

#### 5. Approfondimenti critici

**Retrieval e aggiornamento senza downtime.** Versiono parser, chunker, modello
di embedding e indice. Una migrazione crea l'indice `vNext` in parallelo,
esegue backfill e golden-set eval, quindi usa shadow query o dual-read su un
campione. Lo switch avviene tramite alias/configurazione atomica; rollback
riporta a `vCurrent`. Metadata e ACL sono parte dell'indice e del test.

**Effetti esterni affidabili.** Ogni azione ha identificatore di operazione,
attore, dati normalizzati, decisione di policy e stato. Il tool verifica
autorizzazione e chiave di idempotenza nel sistema destinatario o in un ledger,
un registro persistente delle operazioni. Con una outbox, tabella di messaggi da
pubblicare salvata nella stessa transazione dei dati, intenzione e pubblicazione
sono riconciliabili. Dopo un timeout ambiguo non ritento alla cieca: interrogo lo
stato tramite l'identificatore. Approvazione e autorizzazione vengono rivalidate
immediatamente prima dell'effetto.

#### 6. Sicurezza

- contenuti recuperati e tool output sono dati non fidati, mai istruzioni;
- ACL e tenant isolation sono applicati prima che il modello veda il contesto;
- least privilege, token scoped e brevi, secret manager e rotazione;
- allowlist di tool, schema validation, limiti e approval per azioni sensibili;
- cifratura in transito/a riposo, minimizzazione, redazione e retention;
- difese contro prompt injection ed esfiltrazione testate con adversarial set;
- audit correlato end-to-end senza memorizzare segreti inutili;
- threat model per spoofing, confused deputy, poisoning, replay e supply chain.

Il **threat model** identifica asset, attori, confini di fiducia e possibili
abusi. Copre impersonificazione dell'identità, uso indebito dei privilegi di un
servizio (*confused deputy*), contaminazione delle fonti o dei dati
(*poisoning*), riuso di richieste valide (*replay*) e compromissione di
dipendenze o immagini nella catena di fornitura software.

Una regola nel system prompt non è un controllo di sicurezza. L'enforcement
avviene nei componenti deterministici.

#### 7. Evaluation

Costruisco un golden set versionato da ticket reali redatti e casi sintetici
mirati, con intento, fonti, risposta attesa/rubric, autorizzazioni e azione
consentita. Copro FAQ, long tail, “non so”, conflitti fra fonti, injection,
tenant crossing e failure dei tool.

La pipeline valuta retrieval, groundedness, correttezza, citazioni, selezione e
argomenti dei tool, astensione, escalation, latenza e costo. Annotatori umani
calibrano rubric e LLM judge. In produzione collego trace e feedback a outcome
come riapertura o risoluzione, controllando bias di selezione. Ogni modifica a
modello, prompt, indice o tool contract esegue regression test.

#### 8. SLO e osservabilità

Definisco SLI (*Service Level Indicator*, la misura concreta associata a uno
SLO) per disponibilità e latenza end-to-end e per dipendenza, separando richieste
informative da azioni. Traccio tempo in coda, retrieval, TTFT (*Time To First
Token*, tempo fino al primo token del modello), generazione, tool, retry, token,
cache hit, errori e saturazione. Propago un identificatore di trace attraverso
API, orchestrator, modello e tool, con campionamento più ricco per errori e
azioni sensibili.

L'**error budget** è la quota di inaffidabilità consentita dallo SLO; il *burn
rate* indica quanto velocemente la si sta consumando. Li uso per governare
rollout e priorità. Gli alert sono su sintomi utente e burn rate, non su ogni
fluttuazione interna. Dashboard per versione di modello, prompt, indice e tenant
rendono diagnosticabili le regressioni.

#### 9. Failure mode e degradazione

Un **failure mode** è un modo specifico in cui il sistema può fallire; una
degradazione controllata conserva una funzione ridotta ma sicura invece di
fallire in modo imprevedibile.

| Failure mode | Rilevazione | Degradazione/risposta |
|---|---|---|
| model provider lento/non disponibile | timeout, p95, error rate | modello fallback o search-only |
| indice non aggiornato/corrotto | freshness, canary query, eval | alias alla versione precedente |
| retrieval senza evidenza sufficiente | score + verifica supporto | astensione/escalation |
| timeout del tool dopo un possibile effetto | stato operazione ambiguo | ricerca tramite identificatore operazione, niente retry cieco |
| dipendenza core indisponibile | circuit/health metric | risposta informativa, azione accodata solo se sicura |
| prompt injection | detector e policy violation | ignora contenuto operativo, limita tool, escalation |
| data crossing fra tenant | canary di sicurezza/audit | blocco immediato, incident response e revoca |
| budget conversazione esaurito | contatori | sintesi, risposta parziale o handoff |

Ogni fallback è testato: un modello secondario non aiuta se usa lo stesso
provider o non supporta gli stessi tool. Per incidenti di confidenzialità fail
closed; per FAQ pubbliche può essere accettabile una modalità ridotta.

#### 10. Rollout e rollback

Distribuisco prima internamente, poi shadow, canary per tenant/coorte e infine
incremento graduale. I criteri di promozione e stop includono qualità, sicurezza,
SLO, outcome e costo, con soglie scelte sul rischio reale. Versiono separatamente
servizio, prompt, policy, modello e indice ma registro una release composta.

Rollback di codice/configurazione usa blue-green o revisione precedente; il
model gateway ripristina il modello; l'alias ripristina l'indice. Per schemi e
side effect uso migrazioni backward-compatible, perché un semplice rollback del
container non annulla dati già scritti.

#### 11. Costi

Attribuisco costi a ingestion/embedding, storage/index, retrieval/reranking,
token input/output, tool e osservabilità. Misuro costo per task riuscito e per
segmento. Ottimizzo con routing per complessità, prompt/context pruning,
batching offline, cache autorizzata, modelli piccoli per classificazione e
autoscaling. Mantengo budget e alert, ma verifico che il risparmio non sposti
costo verso errori o operatori umani.

#### 12. Evoluzione a 100x

Prima misuro il collo di bottiglia. Rendo stateless i serving worker e separo
state store; partiziono code e indici per tenant/regione; autoscaling segue
concorrenza, queue depth e limiti del provider. Introduco admission control,
backpressure, quote e priorità per proteggere traffico critico.

Sposto ingestion e attività lunghe su code asincrone, shardo retrieval solo
quando capacità e latenza lo richiedono, uso read replica/cache coerenti con ACL
e negozio o diversifico la capacità dei model provider. Eseguo load, soak e
chaos test, capacity planning e disaster recovery multi-zona o multi-regione.
Concordo RTO (*Recovery Time Objective*, tempo massimo per ripristinare il
servizio) e RPO (*Recovery Point Objective*, quantità massima di dati che si può
perdere). Non moltiplico i componenti in anticipo: ogni livello di scala deve
rispondere a una misura.

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

### Risposte modello alle domande pratiche

#### 1. Recall@5 sale ma la qualità finale scende

Recall@5 è la quota di query per cui almeno una fonte attesa compare nei primi
cinque risultati. Misura copertura del retrieval, non qualità della risposta.

**Ipotesi.** Il retriever trova più documenti “rilevanti” secondo le label, ma
introduce passaggi contraddittori, obsoleti o meno precisi; l'aumento può essere
concentrato su query facili; il reranker o l'ordine sono peggiorati; più contesto
causa distraction/lost-in-the-middle; le label di retrieval non misurano ciò che
serve alla risposta.

**Metodo diagnostico.**

1. blocco modello, prompt e golden set e confronto le due versioni query per
   query, non solo sulla media;
2. segmento per intento, lingua, fonte e difficoltà e ispeziono win/loss;
3. misuro precision/context relevance, rank della fonte utile, conflitti,
   freshness e copertura delle citazioni oltre a Recall@5;
4. rieseguo la generation con solo il passaggio corretto, poi con i top-k delle
   due versioni: così separo errore di retrieval da uso del contesto;
5. provo ablation su `k`, reranking, deduplica e ordine dei passaggi.

**Decisione.** Non promuovo sulla sola Recall@5. Scelgo la configurazione che
migliora la qualità end-to-end e i segmenti critici; posso aggiungere reranking,
filtri di versione, deduplica o un `k` adattivo.

**Trade-off.** Più recall può aumentare robustezza, ma anche token, latenza e
rumore. Il valore ottimale di `k` dipende dal corpus e dal modello.

#### 2. Il p95 raddoppia senza aumento del traffico

Il p95 è il valore di latenza sotto cui termina il 95% delle richieste: se
raddoppia, la coda lenta dell'esperienza è peggiorata anche se la media o il
volume restano stabili.

**Ipotesi.** È cambiata la composizione delle richieste, una dipendenza è lenta,
il provider fa throttling, la cache ha meno hit, una release ha aumentato token
o query, il pool è saturo, ci sono pause del GC (*Garbage Collector*, sistema
che recupera memoria non più usata) o limitazione della CPU, oppure un job
background compete per risorse.

**Metodo diagnostico.**

1. verifico definizione della metrica, finestra, regioni e correlazione con
   deploy/config/model/index;
2. scompongo il trace end-to-end in queue, app, retrieval, database, modello e
   tool, confrontando p50/p95/p99 e non solo la media;
3. segmento per endpoint, tenant, modello, cache hit, lunghezza input/output e
   codice di risposta;
4. controllo CPU, memoria/GC, connessioni, thread/event-loop lag, queue depth,
   rate limit, retry e saturazione delle dipendenze;
5. riproduco con la release precedente o faccio canary rollback; uso un load
   test rappresentativo solo dopo aver isolato il tratto lento.

**Decisione.** Mitigo il componente dominante: rollback, riduzione del contesto,
limite ai retry, aumento capacità, query fix o provider fallback. Confermo il
recupero sullo stesso SLI.

**Trade-off.** Scalare subito può mascherare una regressione e aumentare costo;
fare rollback riduce rischio ma rinuncia temporaneamente alla nuova funzione.

#### 3. Un agente crea due ticket dopo un retry

**Ipotesi.** Il difetto è l'assenza di idempotenza end-to-end: il primo tentativo
ha creato il ticket ma la risposta è andata persa, quindi l'orchestratore ha
ritentato il side effect. Un checkpoint scritto prima o dopo la chiamata non
chiude da solo questa finestra.

**Metodo diagnostico.**

1. correlaziono trace, operation ID e audit per ricostruire i due tentativi;
2. verifico se l'API ticket accetta una idempotency key e quale retention usa;
3. individuo la finestra fra commit remoto e persistenza dello stato locale;
4. provo timeout immediatamente dopo la creazione e crash/restart;
5. aggiungo test concorrenti con la stessa chiave.

**Decisione.** Genero una chiave stabile per intenzione logica, la persisto prima
dell'invocazione e la propago al sistema ticket/ledger con vincolo univoco. Su
timeout ambiguo faccio lookup per chiave; non creo di nuovo. Outbox e
riconciliazione gestiscono crash e consegna almeno-una-volta.

**Trade-off.** Il ledger e la retention aggiungono stato e cleanup; una chiave
definita troppo largamente può impedire azioni legittime successive.

#### 4. Metriche offline migliori ma utenti invariati

**Ipotesi.** La metrica è un proxy debole, il test non rappresenta traffico
reale, il miglioramento riguarda segmenti poco frequenti, la UX (*User
Experience*, esperienza d'uso) non espone il beneficio, latenza o costo sono
peggiorati oppure il sistema non è stato adottato.
Può anche mancare potenza statistica o strumentazione dell'outcome.

**Metodo diagnostico.**

1. definisco la catena causale fra metrica offline, comportamento e outcome
   utente;
2. verifico esposizione alla variante, logging, rapporto fra i campioni,
   eventuale effetto novità e qualità dell'esperimento;
3. segmento i risultati per intento/coorte e confronto distribuzione offline con
   produzione;
4. misuro task completion, escalation, correzioni, riaperture, retention e
   latenza insieme alla qualità;
5. intervisto utenti e campiono sessioni per scoprire ostacoli non catturati.

**Decisione.** Aggiorno golden set e rubric con casi reali e conduco A/B test o
rollout controllato sul KPI, indicatore chiave di risultato, concordato. Se il
proxy non predice valore, non promuovo solo per il guadagno offline.

**Trade-off.** Outcome affidabili arrivano spesso tardi e sono influenzati da
fattori esterni; l'offline resta utile come gate rapido, non come verdetto finale.

#### 5. Impedire a un documento indicizzato di comandare l'agente

**Ipotesi.** Il documento contiene prompt injection esplicita o testo che il
modello interpreta come istruzione. Il rischio diventa grave se l'agente ha tool
privilegiati o può esfiltrare altri dati.

**Metodo diagnostico.**

1. modello i confini di fiducia fra policy di sistema, input utente, documenti e
   output dei tool;
2. creo test avversariali con istruzioni nascoste, codifiche, link ed
   esfiltrazione;
3. verifico quali tool e dati sono raggiungibili e con quali credenziali;
4. controllo che autorizzazione e validazione avvengano fuori dal modello;
5. osservo trace e policy decision, inclusi tentativi bloccati.

**Decisione.** Delimito il documento come dato da citare, non istruzione;
applico ACL, liste di controllo che filtrano le fonti in base all'identità, prima
del retrieval, una lista di tool consentiti, argomenti validati, privilegi
minimi, controllo delle connessioni in uscita e approvazione umana per effetti
esterni. Un componente di policy deterministico rifiuta azioni non autorizzate
anche se il modello le propone. Posso usare un rilevatore di injection come
segnale aggiuntivo, non come unica difesa.

**Trade-off.** Filtri aggressivi producono falsi positivi; isolamento e approval
aumentano latenza, ma sono necessari in proporzione all'impatto del tool.

#### 6. Migrare embedding senza downtime

**Ipotesi.** Il nuovo modello cambia dimensione e spazio vettoriale, quindi
vecchi e nuovi vettori non sono confrontabili. La migrazione può inoltre cambiare
chunking, ranking, costi e qualità per segmento.

**Metodo diagnostico.**

1. versiono embedding, chunker, preprocessing, corpus e indice;
2. creo `index_vNext` e faccio backfill idempotente mentre le nuove modifiche
   alimentano entrambe le versioni o un log riproducibile;
3. valido conteggi, ACL, freshness e golden-set retrieval/generation;
4. eseguo shadow query o dual-read su un campione e confronto qualità, latenza e
   costo;
5. verifico lag di sincronizzazione e procedura di rollback.

**Decisione.** Quando i gate sono superati, commuto atomicamente un alias o la
configurazione verso `vNext`. Tengo `vCurrent` intatto per il rollback e
disattivo il dual-write solo dopo una finestra di stabilità.

**Trade-off.** Per un periodo raddoppiano storage, compute e complessità; una
migrazione in-place costa meno ma rende rischioso rollback e coerenza.

#### 7. Quando usare un modello locale

**Ipotesi.** Un modello locale è vantaggioso se privacy/residenza, funzionamento
offline, latenza di rete, volume stabile o controllo della versione superano i
benefici del servizio gestito. Non assumo che sia automaticamente più economico
o sicuro.

**Metodo diagnostico.**

1. definisco qualità minima, lingue, context window, tool/structured output e
   profilo di latenza;
2. benchmarko candidati sul golden set e sull'hardware previsto, includendo
   quantizzazione e concorrenza;
3. misuro throughput, p95, memoria, energia, utilizzo e failure sotto picco;
4. confronto TCO (*Total Cost of Ownership*, costo totale di possesso):
   hardware, capacità inattiva, deployment, patch, on-call e
   licenza contro costo API;
5. verifico supply chain, isolamento, logging, retention e aggiornamenti.

**Decisione.** Lo scelgo quando soddisfa gate di qualità e operativi e offre un
vantaggio misurabile o un requisito non negoziabile. Un routing ibrido può usare
locale per task semplici/sensibili e remoto per long tail, se la policy lo
permette.

**Trade-off.** Ottengo controllo e prevedibilità, ma assumo capacity planning,
GPU operations e aggiornamenti. Il break-even dipende da utilizzo e hardware.

#### 8. Stabilire se il fine-tuning vale il costo

**Ipotesi.** Il fine-tuning può aiutare un comportamento stabile, formato o
decisione ripetitiva; può invece essere una soluzione sbagliata se il problema è
conoscenza aggiornata, retrieval scarso, tool design o requisito ambiguo.

**Metodo diagnostico.**

1. definisco error taxonomy e segmento target su un eval set congelato;
2. costruisco baseline forti: prompt, esempi, RAG, tool, modello diverso e
   post-processing;
3. preparo dati curati, separo train/eval e controllo contaminazione, diritti e
   rappresentatività;
4. eseguo un esperimento piccolo e confrontabile, misurando qualità, varianza,
   regressioni di sicurezza, latenza e costo end-to-end;
5. stimo costo totale di labeling, training, hosting, nuove versioni e
   manutenzione, non solo la run iniziale;
6. valido in shadow/canary che il guadagno offline produca outcome.

**Decisione.** Procedo se il miglioramento sul target è significativo per il
prodotto, supera baseline più semplici, non viola guardrail e ha payback
accettabile. Mantengo dataset/versioni e rollback.

**Trade-off.** Può ridurre prompt e costo per chiamata, ma crea un ciclo di dati,
valutazione e retraining; può specializzare troppo e peggiorare il long tail.

## Errori da evitare

| Risposta superficiale | Perché è debole | Correzione |
|---|---|---|
| “I thread sono per I/O, i processi per CPU.” | ignora GIL, librerie native, overhead e misure | collega scelta al carico e cita concorrenza, isolamento e profiling |
| “Uso sempre async perché è più veloce.” | async non accelera CPU e il codice bloccante ferma il loop | parla di I/O concorrente, backpressure, timeout e limiti |
| “Protocol serve per il duck typing.” | vero ma incompleto | spiega disaccoppiamento, type checking e quando l'ereditarietà esprime invarianti |
| “Metto un retry con tre tentativi.” | numero arbitrario, rischio di retry storm e duplicati | classifica errori, usa deadline, backoff/jitter e idempotenza |
| “Accuracy è alta, quindi il modello funziona.” | ignora prevalenza e costo degli errori | scegli metriche e threshold dal caso d'uso e analizza segmenti |
| “Il drift si risolve facendo retraining.” | drift non implica necessariamente perdita di qualità | misura impatto su outcome e diagnostica il tipo di cambiamento |
| “RAG dà al modello dati aggiornati.” | non tratta retrieval, ACL, citazioni e astensione | descrivi ingestion, ranking, eval e trust boundary |
| “Abbasso la temperature per eliminare hallucination.” | riduce varianza, non garantisce verità | evidenze, verifica citazioni, constrained flow e astensione |
| “Il prompt dice di ignorare istruzioni nei documenti.” | il prompt non è enforcement | separa trust boundary e applica authorization/policy fuori dal modello |
| “Aumento `top_k` per migliorare il RAG.” | può aumentare rumore, costo e lost-in-the-middle | valuta recall e qualità finale, reranking e `k` adattivo |
| “Uso un agente perché il task è complesso.” | complessità non implica decisione dinamica | identifica quale scelta non è modellabile con workflow |
| “Il checkpoint impedisce duplicati.” | resta la finestra crash dopo il side effect | operation ID, API idempotente, ledger/outbox e riconciliazione |
| “Human-in-the-loop significa chiedere conferma.” | una conferma senza contesto è poco utile | mostra azione, argomenti, impatto e ricontrolla policy/stato |
| “Multi-agent scala meglio.” | spesso aumenta coordinamento, token e failure mode | confronta con singolo orchestratore su una metrica esplicita |
| “Airflow fa ETL e dbt trasforma i dati.” | ETL significa *Extract, Transform, Load*, ma la frase confonde orchestrazione, logica e affidabilità | tratta idempotenza, intervallo dati, test, lineage e backfill |
| “Snowflake scala automaticamente.” | warehouse, code, pruning e costi richiedono design | usa query profile, isolamento workload e guardrail di costo |
| “MCP rende sicuri i tool.” | MCP standardizza l'interfaccia, non la policy | autorizza ogni invocazione e tratta server/output come non fidati |
| “Docker garantisce portabilità.” | non copre runtime, architettura, segreti o stato | cita immagine minimale, health, non-root e config esterna |
| “Su AWS metto tutto in Fargate e autoscaling.” | manca IAM, rete, segnali e strategia di guasto | descrivi ruolo del task, distribuzione su più zone, osservabilità, scaling e rollback |
| “Promuovo perché la media è migliore.” | nasconde regressioni nei segmenti critici | usa gate, intervalli, worst-case, canary e criteri di stop |

Al colloquio evita anche numeri presentati come universali. Puoi proporre un
valore iniziale come ipotesi, ma specifica quali dati useresti per calibrarlo e
quale metrica determinerebbe la decisione.

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
- mesi 4-6: contribuisci a una libreria di AI (*Artificial Intelligence*,
  intelligenza artificiale) o pubblica benchmark riproducibili;
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
| Comunicazione | ADR (*Architecture Decision Record*, documento di una decisione architetturale), diagramma e demo basata su metriche |

Se manca una prova, non scrivere solo "conosco X": costruisci l'artefatto che la
dimostra.
