# Lezione passo-passo: prepararsi al colloquio tecnico

## Cosa saprai fare alla fine

Saprai:

1. capire che cosa valuta un colloquio AI Engineer;
2. strutturare una risposta senza recitare;
3. affrontare una domanda che non conosci completamente;
4. progettare un sistema partendo dai requisiti;
5. raccontare il capstone con evidenze;
6. usare le risposte modello del capitolo come verifica, non come copione.

## Cosa devi sapere prima

Affronta questa lezione dopo aver completato almeno i moduli da 00 a 07. Per
raccontare un progetto reale durante il colloquio, completa anche il
[capstone passo-passo](../08-capstone/LEZIONE.md).

Non devi ricordare ogni libreria a memoria. Devi invece saper spiegare con parole tue
le scelte fatte, i risultati misurati e gli errori che il sistema deve gestire.

## 1. Che cosa viene valutato

Un buon colloquio non misura soltanto quante definizioni ricordi. Cerca segnali:

- comprendi il problema prima di scegliere strumenti;
- distingui ipotesi e fatti;
- sai costruire una baseline;
- misuri qualità, costo e latenza;
- prevedi errori;
- proteggi dati e azioni;
- spieghi trade-off;
- porti un sistema fino alla produzione.

Un **trade-off** è un compromesso: migliorare una proprietà può peggiorarne un'altra.
Esempio: un reranker può aumentare precisione ma aggiungere latenza e costo.

## 2. Struttura di una risposta

Usa questa sequenza:

```text
1. Definizione
2. Requisito/contesto
3. Opzioni
4. Scelta
5. Misura
6. Failure mode
7. Trade-off
```

Domanda: "Useresti un agente?"

Risposta debole:

```text
Sì, userei LangGraph perché gestisce agenti complessi.
```

Risposta migliore:

```text
Un agente lascia al modello la scelta dinamica dei passi.
Prima chiarirei se i passi sono realmente variabili.
Se sono noti, preferirei un workflow deterministico: costa meno ed è più verificabile.
Se il modello deve scegliere fra tool in base a input non prevedibili, userei un
grafo con massimo passi, timeout, tool autorizzati e checkpoint.
Confronterei task success, costo, p95 e failure rate contro il workflow baseline.
```

## 3. Se non conosci la risposta

Non inventare.

Puoi dire:

```text
Non ho usato questa tecnologia in produzione. Conosco il problema che risolve:
...
Per valutarla controllerei:
...
La confronterei con:
...
Il rischio principale che verificherei è:
...
```

Questo mostra metodo. Fingere esperienza produce contraddizioni nelle domande
successive.

## 4. Domande di chiarimento

Prima del system design chiedi:

- chi usa il sistema?
- quale decisione deve supportare?
- quali dati può vedere?
- qual è il volume?
- quale latenza è accettabile?
- quanto costa un errore?
- serve scrivere o solo leggere?
- quali requisiti legali e di retention esistono?

Non passare dieci minuti a interrogare l'intervistatore. Fai poche domande che cambiano
l'architettura e dichiara assunzioni per il resto.

## 5. Esempio guidato: progettare un assistente HR

### Passo 1: obiettivo

```text
L'assistente aiuta operatori autenticati a trovare procedure e aprire ticket con
approvazione.
```

### Passo 2: non-obiettivi

```text
Non modifica cedolini.
Non risponde senza fonte.
Non apprende automaticamente da conversazioni.
```

### Passo 3: baseline

```text
Ricerca BM25 con link ai documenti, senza generazione.
```

### Passo 4: flusso

```text
utente -> autenticazione -> retrieval con ACL -> risposta citata
      -> eventuale proposta tool -> approval -> esecuzione idempotente
```

### Passo 5: dati

```text
fonti -> dlt -> Snowflake -> dbt/test -> indice candidato -> eval -> alias attivo
```

### Passo 6: metriche

- Recall@5 sui casi con risposta;
- unauthorized hit uguale a zero;
- citation precision;
- corretta astensione;
- task completion;
- p95;
- costo per richiesta.

### Passo 7: failure mode

- indice vecchio;
- provider lento;
- prompt injection;
- tool timeout dopo scrittura;
- cross-tenant;
- budget esaurito.

Per ciascuno indica rilevazione, comportamento sicuro e rollback.

## 6. Come raccontare il capstone

Usa:

```text
Problema
-> prima baseline
-> errore incontrato
-> esperimento
-> scelta
-> risultato misurato
-> limite
-> prossimo passo
```

Esempio:

```text
La baseline BM25 falliva sulle domande semantiche.
Ho creato un golden set separando codici e linguaggio naturale.
Il retrieval ibrido ha migliorato Recall@5 sul segmento semantico, con p95 maggiore.
Ho aggiunto RRF e mantenuto il reranker solo perché superava il gate.
Il limite è che il corpus è sintetico; validerei su query reali redatte.
```

Non dire soltanto "ho usato LangChain, Airflow e AWS". I nomi non mostrano decisioni.

## 7. Coding interview

Durante un esercizio Python:

1. ripeti il problema con parole tue;
2. chiarisci input, output e casi limite;
3. scrivi una soluzione semplice;
4. esegui un esempio a mano;
5. analizza complessità;
6. aggiungi test;
7. migliora solo se necessario.

Parla mentre prendi decisioni, non mentre scrivi ogni carattere.

Esempio: elaborare un file grande.

Prima domanda:

```text
Il file entra in memoria? L'ordine va mantenuto? Come gestiamo righe invalide?
```

Soluzione iniziale: generatore che legge una riga alla volta, validazione con errore
contenente numero riga, output streaming.

## 8. Domande comportamentali

Usa **STAR**:

- Situation: contesto;
- Task: responsabilità;
- Action: azioni tue;
- Result: risultato misurabile.

Per un ruolo production AI prepara storie su:

- incidente;
- decisione con dati incompleti;
- regressione evitata;
- disaccordo tecnico;
- progetto end-to-end;
- errore tuo e correzione.

Non attribuire al singolo ciò che ha fatto il team; chiarisci il tuo contributo.

## 9. Piano di allenamento

### Ogni settimana

1. una sessione Python da 45 minuti;
2. un system design da 45 minuti;
3. una spiegazione capstone da 15 minuti;
4. revisione degli errori.

### Score

Assegna 0-2:

| Area | Domanda |
|---|---|
| chiarezza | ho definito i termini? |
| requisiti | ho chiarito il problema? |
| decisione | ho motivato la scelta? |
| misura | ho indicato come verificarla? |
| rischio | ho trattato failure e sicurezza? |

Target: almeno 8/10 per tre sessioni consecutive.

## 10. Come usare le risposte modello

Il [manuale con le risposte modello](README.md) è lungo perché copre molte domande.
Usalo così:

1. leggi una domanda;
2. rispondi senza guardare;
3. scrivi assunzioni e misura;
4. confronta con la risposta modello;
5. aggiungi ciò che mancava;
6. ripeti due giorni dopo.

Non memorizzare la formulazione. Al colloquio requisiti diversi richiedono una scelta
diversa.

## 11. Laboratorio guidato

Scegli una domanda dal manuale e registra una risposta di massimo cinque minuti:

```text
Progetta un assistente HR che risponda usando documenti aziendali.
```

Procedi così:

1. dedica 30 secondi a chiarire utenti, dati, permessi e obiettivo;
2. disegna il flusso dati → retrieval → LLM → risposta;
3. indica una baseline senza LLM;
4. scegli una metrica di qualità e una operativa;
5. descrivi almeno due failure mode e il rollback;
6. riascolta la registrazione e assegna lo score della sezione 9.

## 12. Esercizi

### Base

Spiega in 90 secondi la differenza fra workflow e agente senza nominare framework.

### Intermedio

Disegna un RAG multi-tenant e indica dove applichi autorizzazione, valutazione e
osservabilità.

### Avanzato

Racconta un incidente del capstone con il metodo STAR e concludi con la misura che
dimostra la correzione.

## 13. Soluzioni ragionate

### Base

Un workflow segue transizioni progettate; un agente lascia al modello la scelta
dinamica di alcuni passi. Parti dal workflow perché è più prevedibile e passa
all'agente solo se i percorsi non sono enumerabili in modo sostenibile.

### Intermedio

Autentica l'utente prima della query, filtra tenant e ACL nel retrieval, valuta
separatamente retrieval e risposta, traccia latenza/errori/costi senza registrare dati
sensibili e verifica le citazioni prima dell'output.

### Avanzato

Una risposta completa distingue contesto, tua responsabilità, azione e risultato.
Non esiste una storia universale: usa un episodio reale del progetto e quantifica
almeno test falliti prima/dopo, tempo di recupero, tasso di duplicazione o metrica di
qualità.

## 14. Errori comuni

- Nominare framework prima del problema.
- Usare numeri universali senza contesto.
- Dire "dipende" senza spiegare da cosa.
- Descrivere solo happy path.
- Ignorare autorizzazione e dati sensibili.
- Confondere metrica offline e valore utente.
- Inventare esperienza.
- Parlare per dieci minuti senza una struttura.

## 15. Domande di autoverifica

**Qual è la prima cosa in un system design?**  
Chiarire utente, obiettivo, vincoli e rischio.

**Che cosa rende forte una scelta tecnica?**  
Alternative, evidenza, trade-off e criterio di revisione.

**Che cosa dire se non hai usato uno strumento?**  
Dichiararlo, spiegare il problema e descrivere come lo valuteresti.

**Perché non memorizzare le risposte modello?**  
Perché cambiano requisiti e assunzioni; serve dimostrare ragionamento.

## 16. Prossimo passo

Apri il [manuale completo delle risposte](README.md), scegli cinque domande e registrati
mentre rispondi con la struttura definizione → contesto → scelta → misura → rischio.
