# Glossario ragionato AI/ML Engineering

Usa questo glossario quando un termine non è chiaro, ma non imparare definizioni
isolate: collega sempre il concetto a un esempio, un rischio e una decisione tecnica.

## A

### A/B test

Esperimento online in cui utenti comparabili vengono assegnati casualmente a due
varianti. Misura impatto causale su metriche di prodotto; richiede campione, durata e
guardrail adeguati.

### ACL (Access Control List)

Elenco di identità o ruoli autorizzati ad accedere a una risorsa. In RAG deve filtrare
i documenti prima che raggiungano retriever, reranker o modello.

### Adapter

Componente che traduce un'interfaccia del dominio verso una tecnologia concreta, per
esempio da `Retriever` a Snowflake. Consente di cambiare provider e testare con fake.

### Agente

Sistema in cui un modello sceglie dinamicamente azioni o tool per raggiungere un
obiettivo. Include stato, runtime, policy, limiti e osservabilità, non solo un prompt.

### Airflow

Piattaforma di orchestrazione che schedula DAG di task, retry, backfill e dipendenze.
Coordina il lavoro; la logica dati dovrebbe restare in package o strumenti dedicati.

### ANN (Approximate Nearest Neighbor)

Ricerca approssimata dei vettori più vicini. Sacrifica una piccola parte di recall per
ridurre drasticamente latenza rispetto al confronto con tutti i vettori.

### API (Application Programming Interface)

Contratto con cui componenti software comunicano. Definisce operazioni, schema,
autenticazione, errori e versionamento.

### Artifact

Output versionato di build o training: immagine Docker, modello, report eval, indice
o manifest. Deve essere immutabile e collegato al codice che lo ha prodotto.

### Asyncio

Runtime Python per concorrenza cooperativa. È efficace quando task attendono I/O; non
accelera automaticamente calcolo CPU-bound.

### Attention

Meccanismo del Transformer che combina rappresentazioni assegnando pesi alle
relazioni fra token. Non va interpretato automaticamente come spiegazione causale.

### Autenticazione

Verifica chi è un principal, per esempio tramite sessione o token. Risponde "chi sei?".

### Autorizzazione

Verifica quali azioni o dati sono consentiti al principal autenticato. Risponde "che
cosa puoi fare?" e deve essere applicata dal codice, non dal modello.

## B

### Backfill

Riesecuzione di una pipeline su intervalli storici. Deve essere idempotente e
versionata per non duplicare o corrompere dati.

### Backoff e jitter

Il backoff aumenta l'attesa fra retry; il jitter aggiunge casualità per evitare che
molti client riprovino simultaneamente.

### Backpressure

Meccanismo che rallenta o rifiuta nuovo lavoro quando il sistema è saturo. Evita code
illimitate e collasso della latenza.

### Baseline

Soluzione semplice contro cui confrontare un candidato: regola, modello lineare, BM25
o workflow deterministico. Quantifica il valore reale della complessità.

### Batch inference

Produzione di previsioni su gruppi di record, spesso schedulata. Privilegia throughput
rispetto alla latenza della singola richiesta.

### BM25

Algoritmo di ranking lessicale che considera frequenza dei termini, rarità nel corpus
e lunghezza del documento. È forte su codici, nomi e parole esatte.

### Bootstrap

Tecnica statistica che ricampiona con sostituzione le osservazioni per stimare
variabilità o intervalli di confidenza di una metrica.

### Brier score

Media dell'errore quadratico fra probabilità predetta e risultato binario. Valuta
anche la calibrazione; più basso è migliore.

### Bulkhead

Isolamento di risorse fra workload, ispirato ai compartimenti di una nave. Impedisce
che la saturazione di una funzione abbatta l'intero servizio.

## C

### Cache

Memoria di risultati riutilizzabili. La chiave deve includere tutto ciò che influenza
l'output, inclusi tenant, permessi, versione modello, prompt e indice.

### Calibrazione

Coerenza fra probabilità predetta e frequenza osservata. Se casi stimati al 70% sono
positivi circa sette volte su dieci, il modello è calibrato in quella regione.

### Canary deployment

Rilascio della nuova versione a una piccola percentuale di traffico per confrontare
metriche e limitare l'impatto di regressioni.

### Checkpoint

Snapshot persistito dello stato e della posizione di un workflow. Permette resume e
human-in-the-loop, ma non rende da solo idempotenti gli effetti esterni.

### Chunk

Porzione di documento indicizzata e recuperata in un sistema RAG. Conserva testo,
provenienza, posizione, versione e autorizzazioni.

### CI/CD

**Continuous Integration** automatizza controlli a ogni modifica. **Continuous
Delivery/Deployment** automatizza preparazione o rilascio delle versioni approvate.

### Circuit breaker

Interrompe temporaneamente chiamate a una dipendenza che fallisce ripetutamente,
evitando di accumulare attese e dando tempo al servizio di recuperare.

### Class imbalance

Distribuzione in cui una classe è molto meno frequente. Accuracy può diventare
fuorviante; precision, recall e PR-AUC sono spesso più informative.

### Concept drift

Cambiamento della relazione fra input e target, `P(y|X)`. Può degradare il modello
anche se la distribuzione apparente delle feature resta simile.

### Context window

Numero massimo di token che un LLM può considerare in una richiesta, inclusi prompt,
cronologia, documenti, tool result e output.

### Contract test

Test che verifica la compatibilità fra consumer e provider: schema, errori, semantica
e versioni di API, tool o dati.

### Correlation ID

Identificatore propagato fra servizi, log e trace per ricostruire una richiesta.

### Corpus

Insieme dei documenti ricercabili da un sistema di information retrieval.

### CPU-bound e I/O-bound

Un task CPU-bound passa il tempo a calcolare; un task I/O-bound attende rete, disco o
database. Thread/async aiutano soprattutto il secondo; processi o codice nativo il primo.

### Cross-encoder

Modello che legge insieme query e documento per assegnare rilevanza. È accurato ma
più costoso di embedding separati, quindi viene usato come reranker.

### Cross-validation

Valutazione su più suddivisioni train/validation. Deve rispettare tempo, gruppi e
dipendenze del dominio.

### CVE (Common Vulnerabilities and Exposures)

Identificatore pubblico di una vulnerabilità nota. Uno scan container cerca CVE nelle
dipendenze, ma severity ed esposizione reale vanno contestualizzate.

## D

### DAG (Directed Acyclic Graph)

Grafo orientato senza cicli. In Airflow rappresenta task e dipendenze; in un workflow
AI può rappresentare nodi e transizioni.

### Data contract

Accordo verificabile su schema, semantica, qualità, freschezza e compatibilità di un
dataset fra producer e consumer.

### Data drift

Cambiamento della distribuzione degli input `P(X)`. È un segnale da indagare, non una
prova automatica di perdita di performance.

### Data lineage

Tracciamento della provenienza dei dati e delle trasformazioni attraversate.

### Data product

Dataset o servizio dati trattato come prodotto: owner, utenti, contratto, qualità,
documentazione, SLO e ciclo di vita.

### dbt (data build tool)

Strumento che trasforma dati nel warehouse con SQL versionato, dipendenze, test,
documentazione e lineage.

### Deadline e timeout

Il timeout limita una singola operazione; la deadline è l'istante entro cui l'intera
richiesta deve terminare. Le dipendenze devono condividere il budget totale.

### Deduplica

Identificazione e rimozione/accorpamento di record uguali o equivalenti.

### Dense retrieval

Ricerca semantica basata su vettori densi prodotti da un modello di embedding.

### dlt (data load tool)

Libreria Python per estrarre e caricare dati gestendo schema, stato incrementale,
normalizzazione e destinazioni.

### Distillation

Addestramento di un modello più piccolo a imitare output o distribuzioni di uno più
grande, per ridurre costo e latenza.

### Docker image e container

L'immagine è un artifact immutabile con filesystem e metadata; il container è
un'istanza in esecuzione dell'immagine.

## E

### Embedding

Vettore numerico che rappresenta un elemento. La vicinanza riflette relazioni apprese
dal modello, non una probabilità universale.

### Error budget

Quota di fallimenti consentita da un SLO. Se viene consumata troppo rapidamente, si
riduce il ritmo di rilascio e si investe in affidabilità.

### Evaluation o eval

Processo sistematico che misura comportamento e vincoli su un dataset definito. Deve
versionare dati, configurazione, evaluator e risultati.

### ETL ed ELT

Extract-Transform-Load trasforma prima di caricare; Extract-Load-Transform carica raw
e trasforma nel warehouse. Lo stack dlt+Snowflake+dbt segue tipicamente ELT.

### Exactly-once e at-least-once

At-least-once può consegnare un evento più volte; exactly-once promette un solo effetto
osservabile ma richiede forti garanzie. In pratica si usa spesso at-least-once con
consumer idempotenti.

## F

### Faithfulness

Grado in cui una risposta è supportata dalle evidenze fornite. Non garantisce che la
fonte stessa sia aggiornata o vera.

### F1 score

Media armonica di precision e recall: `2PR/(P+R)`. Bilancia le due metriche ma non
incorpora direttamente costi asimmetrici o calibrazione.

### Feature

Variabile usata dal modello per produrre una previsione. Deve essere disponibile al
momento reale dell'inference.

### Fine-tuning

Aggiornamento dei pesi di un modello su dati specifici. Serve per comportamento o task
stabili, non come sostituto naturale di una knowledge base aggiornata.

### Few-shot

Prompting che include pochi esempi input-output per mostrare il comportamento atteso.
Consuma contesto e può introdurre bias dagli esempi scelti.

## G

### GIL (Global Interpreter Lock)

Meccanismo di CPython che, nelle build tradizionali, limita l'esecuzione simultanea di
bytecode Python in un processo. I thread restano utili per I/O; per CPU Python puro si
usano spesso processi o estensioni native.

### Golden set

Dataset curato e revisionato usato per confrontare versioni. Include casi normali,
limite, negativi, segmenti e severità.

### Graceful shutdown

Arresto che smette di accettare lavoro, completa o cancella in modo controllato ciò
che è in corso e chiude risorse.

### Guardrail

Vincolo che non deve peggiorare mentre si ottimizza la metrica principale, per esempio
zero leakage fra tenant.

## H

### Hallucination

Output plausibile ma non supportato o falso. RAG può ridurla per fatti documentali ma
richiede retrieval, citazioni, astensione e valutazione.

### HNSW

Indice ANN basato su un grafo navigabile multilivello. Offre ricerca vettoriale rapida
con trade-off fra memoria, build time, latenza e recall.

### Human-in-the-loop

Passaggio in cui una persona revisiona o approva una decisione. L'approvazione deve
essere legata all'azione e al payload esatti.

## I

### IAM (Identity and Access Management)

Sistema AWS per identità, ruoli e policy. Un workload dovrebbe usare ruoli temporanei
con privilegi minimi, non chiavi statiche.

### Idempotenza

Proprietà per cui ripetere la stessa operazione produce lo stesso stato logico senza
duplicare effetti. È essenziale per retry, code e resume.

### Inference

Uso di un modello già addestrato per produrre una previsione o generazione.

### Information retrieval

Disciplina che recupera e ordina informazioni rilevanti rispetto a una query.

## J

### JSON-RPC

Protocollo di chiamata remota che rappresenta request, response, errori e notifiche in
JSON. MCP usa JSON-RPC per i propri messaggi.

### Jensen-Shannon divergence

Misura simmetrica e limitata della differenza fra due distribuzioni. Può segnalare
data drift; valore e soglia dipendono da binning, campione e dominio.

## L

### Label o target

Valore vero che un modello supervisionato deve prevedere.

### LangChain

Libreria di componenti e integrazioni per applicazioni LLM: modelli, prompt, tool,
retriever e structured output.

### LangGraph

Runtime/libreria per workflow stateful modellati come grafi con nodi, transizioni,
checkpoint e human-in-the-loop.

### Latenza p50/p95/p99

Percentili: p95 è il valore sotto cui cade il 95% delle richieste. Descrivono la coda
della distribuzione meglio della sola media.

### Leakage

Uso o esposizione di informazione non consentita. Nel ML è informazione futura nel
training; in sicurezza può essere dato di un altro tenant o PII nei log.

### LLM (Large Language Model)

Modello neurale con molti parametri addestrato principalmente a predire token. Genera
testo e output strutturati ma non garantisce verità o autorizzazione.

### LLM-as-judge

Uso di un LLM come evaluator. Scala più della review umana, ma va calibrato perché può
avere bias e variabilità.

### Log-loss

Penalità probabilistica che cresce molto quando il modello assegna alta confidenza a
una classe sbagliata. Più bassa è migliore.

### LoRA (Low-Rank Adaptation)

Fine-tuning parameter-efficient che addestra piccole matrici aggiuntive invece di
tutti i pesi del modello.

## M

### MCP (Model Context Protocol)

Protocollo che standardizza la scoperta e l'uso di resource, tool e prompt esposti da
server a host AI. Non sostituisce autenticazione, autorizzazione o sandbox.

### MAP (Mean Average Precision)

Media dell'Average Precision sulle query. Considera la precisione nelle posizioni in
cui appare un risultato rilevante ed è utile con più risultati rilevanti.

### Metadata

Dati che descrivono altri dati: fonte, versione, tenant, lingua, timestamp e ruoli.

### MLOps

Pratiche per training, versioning, deploy e monitoraggio di sistemi ML. LLMOps estende
il ciclo a prompt, retrieval, tool e modelli generativi.

### Model registry

Catalogo di versioni modello, metadata, metriche e stato di promozione.

### MRR (Mean Reciprocal Rank)

Media dell'inverso della posizione del primo risultato rilevante. Premia trovare
presto almeno una risposta, ma ignora gli altri risultati rilevanti.

### Multi-agent

Sistema con più agenti/ruoli che comunicano. Aumenta flessibilità ma anche costo,
latenza, handoff e difficoltà di test.

## N

### NDCG (Normalized Discounted Cumulative Gain)

Metrica di ranking con rilevanza graduata. Sconta le posizioni basse e normalizza il
risultato rispetto all'ordine ideale.

## O

### OCR (Optical Character Recognition)

Conversione di immagini contenenti testo in caratteri. Può introdurre errori da
misurare prima dell'indicizzazione.

### OLAP e OLTP

OLTP gestisce transazioni applicative brevi; OLAP gestisce analisi e aggregazioni su
molti dati.

### Orchestrazione

Coordinamento di task, dipendenze, stato, retry, timeout e scheduling. Non dovrebbe
contenere tutta la business logic.

### Overfitting e underfitting

Overfitting: modello impara troppo i dati train e generalizza male. Underfitting:
modello non rappresenta neppure il segnale train.

## P

### PII (Personally Identifiable Information)

Informazione che identifica o rende identificabile una persona. Richiede
classificazione, minimizzazione, accesso, retention e redazione appropriati.

### PR-AUC

Area sotto la curva Precision-Recall al variare del threshold. È informativa quando la
classe positiva è rara; va confrontata anche con la prevalenza baseline.

### Precision e recall

Precision: quota di predizioni positive corrette. Recall: quota di positivi reali
trovati. La priorità dipende dal costo degli errori.

### Precision@k e Recall@k

Precision@k è la quota dei primi `k` risultati rilevanti; Recall@k è la quota di tutti
i rilevanti trovata nei primi `k`. Recall@k non è definita per query senza rilevanti.

### PSI (Population Stability Index)

Somma sui bin di `(quota_corrente - quota_reference) *
ln(quota_corrente/quota_reference)`. Confronta distribuzioni ma dipende fortemente da
binning e numerosità; soglie convenzionali non sostituiscono il dominio.

### Principal

Identità autenticata, umana o di servizio, con attributi e ruoli usati dalle policy.

### Prompt

Insieme di istruzioni e contesto inviati al modello. È configurazione versionata, non
una barriera di sicurezza.

### Prompt injection

Input o contenuto recuperato che tenta di modificare istruzioni o indurre azioni non
consentite. Le difese decisive sono privilegi minimi, policy e validazione nel codice.

### Protocol

Nel typing Python, interfaccia strutturale: un oggetto è compatibile se implementa i
metodi richiesti, senza ereditare esplicitamente.

## Q

### Quantizzazione

Rappresentazione dei pesi con meno bit per ridurre memoria e talvolta latenza, con
possibile perdita di qualità.

### Query rewriting

Riscrittura di una domanda per renderla più adatta al retrieval. Va valutata perché
può perdere vincoli dell'originale.

## R

### RAG

Retrieval-Augmented Generation: recupera evidenze da un corpus e le passa a un modello
per generare la risposta.

### ROC-AUC

Probabilità che un positivo casuale riceva score maggiore di un negativo casuale.
Riassume il ranking ma può nascondere prestazioni scarse sulla classe rara.

### Rate limit

Limite al numero o costo di richieste in un intervallo, applicato globalmente o per
utente/tenant.

### Reducer

In LangGraph, funzione che combina aggiornamenti di stato, per esempio concatenando
messaggi invece di sovrascriverli.

### Reranker

Modello o algoritmo che riordina una lista breve di candidati con maggiore precisione.

### Retrieval ibrido

Combinazione di ricerca lessicale e densa per coprire termini esatti e semantica.

### Retry

Nuovo tentativo dopo un errore transitorio. Richiede limite, backoff, jitter,
idempotenza e budget.

### RRF (Reciprocal Rank Fusion)

Metodo che combina ranking sommando contributi inversi della posizione. Evita di
normalizzare score eterogenei.

### Rollback

Ritorno a una versione nota funzionante. Deve includere app, prompt, modello e indice,
che possono evolvere separatamente.

## S

### Schema

Struttura attesa di dati o output: campi, tipi e vincoli. La validazione impedisce che
dati malformati entrino nel core.

### SBOM (Software Bill of Materials)

Inventario di componenti e versioni contenuti in un artifact software. Supporta
vulnerability management e supply-chain audit.

### Semaphore

Primitiva che limita quante operazioni possono entrare contemporaneamente in una
sezione, utile per proteggere provider e connection pool.

### Shadow deployment

Invia una copia del traffico alla nuova versione senza usarne l'output per l'utente.
Permette confronto realistico ma richiede attenzione a costi e side effect.

### SLI, SLO e SLA

SLI è una misura; SLO è il target interno; SLA è un accordo contrattuale con
conseguenze. Esempio: SLI disponibilità, SLO 99,5%, SLA definita col cliente.

### Split

Suddivisione dei dati in train, validation e test. Deve impedire condivisione indebita
di tempo, utenti o informazione.

### Streaming

Invio progressivo di output o elaborazione continua di eventi. Nei LLM riduce il tempo
percepito al primo token ma complica errori, validazione e cancellazione.

### Structured output

Output vincolato a uno schema, per esempio JSON validato da Pydantic. È preferibile al
parsing fragile di testo libero.

## T

### Temperature

Parametro che modifica quanto è concentrata la distribuzione dei prossimi token. Non
aggiunge conoscenza e non garantisce creatività o correttezza.

### Tenant

Cliente o spazio isolato in un sistema multi-tenant. L'identità del tenant deriva
dall'autenticazione, non dall'input scelto dal modello.

### Threshold

Soglia che converte uno score/probabilità in decisione. Va scelta su validation in
base a costo e capacità operative.

### Token

Unità numerica elaborata da un modello linguistico. Costo e context window sono
normalmente espressi in token.

### Tool calling

Produzione da parte del modello di nome e argomenti di una funzione. Il runtime valida,
autorizza ed esegue; il modello non chiama direttamente il sistema.

### Trace

Rappresentazione del percorso di una richiesta fra servizi e step, con tempi, status e
correlation.

### Training

Processo che stima i parametri di un modello minimizzando una funzione obiettivo sui
dati.

### Transformer

Architettura neurale basata principalmente su attention, feed-forward layer e
connessioni residue.

### TTFT (Time To First Token)

Tempo fra richiesta e primo token ricevuto in streaming.

### TTL (Time To Live)

Durata per cui un dato o una cache è considerato valido prima di scadere.

## V

### Vector database

Sistema che memorizza embedding, metadata e indici per similarity search. Deve
integrarsi con source-of-truth, aggiornamenti e autorizzazioni.

### Vector similarity

Misura di vicinanza fra vettori, come cosine similarity o dot product. Il significato
dei valori dipende dal modello e dalla normalizzazione.

## W

### Warehouse

Sistema analitico che conserva dati strutturati e separa spesso storage e compute.
Snowflake è il warehouse usato nello stack del corso.

### Workflow deterministico

Processo in cui transizioni e azioni sono definite dal codice. È più prevedibile e va
preferito quando la flessibilità agentica non aggiunge valore misurabile.

## Z

### Zero-shot

Prompting che richiede un task senza fornire esempi input-output. È la baseline più
semplice da confrontare con few-shot o fine-tuning.
