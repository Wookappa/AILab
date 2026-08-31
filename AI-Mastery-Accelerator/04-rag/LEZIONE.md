# Lezione passo-passo: cercare fonti e costruire un RAG

## Cosa saprai fare alla fine

Alla fine saprai:

1. spiegare perché `Ctrl+F` non basta su molti documenti;
2. distinguere documento, corpus, chunk, metadati, indice e query;
3. costruire una ricerca lessicale simile a BM25;
4. capire embedding e similarità senza formule misteriose;
5. descrivere retrieval ibrido, RRF e reranker nell'ordine corretto;
6. disegnare una pipeline RAG completa;
7. calcolare Recall@k, Precision@k e MRR;
8. separare domande con risposta e senza risposta;
9. applicare filtri di tenant e permessi prima di mostrare contenuti;
10. eseguire un piccolo laboratorio RAG interamente locale.

## Cosa devi sapere prima

Completa [la lezione su LLM e prompt](../03-llm-foundations/LEZIONE.md). Devi conoscere
input, output, token, contesto e allucinazione.

Devi inoltre saper eseguire un file Python e leggere liste, dizionari, cicli e
funzioni. Se serve, ripassa
[Python passo-passo](../01-python-production/LEZIONE.md).

Il laboratorio usa solo la libreria standard di Python: non scarica modelli, non
richiede chiavi e non usa internet.

## 1. Il problema parte da Ctrl+F

Hai tre documenti aziendali e vuoi trovare la procedura per reimpostare una password.
Apri un file e premi `Ctrl+F`. Cerchi `password` e trovi la sezione giusta.

Questa è già una forma semplice di **retrieval**, cioè recupero: data una domanda,
cerchi il testo utile.

Ora immagina 50.000 documenti. Alcuni scrivono “credenziali”, altri “accesso”, altri
“codice segreto”. `Ctrl+F`:

- lavora di solito su un file alla volta;
- cerca la parola esatta;
- non ordina bene migliaia di risultati;
- non comprende sinonimi;
- non applica automaticamente tutti i permessi;
- non prepara una risposta con fonti.

Serve quindi un sistema che recuperi pochi passaggi rilevanti prima di chiedere a un
modello linguistico di rispondere.

## 2. Le parole fondamentali

Un **documento** è un'unità originale: un file Markdown, una pagina, un contratto o
un record del database. Esempio: `procedura-ferie.md`.

Il **corpus** è l'intera collezione ricercabile. Analogia: non un libro, ma tutta la
biblioteca.

Un **chunk**, cioè blocco, è una porzione di documento. Dividiamo documenti lunghi
per recuperare la sezione utile senza passare cento pagine al modello.

```text
documento "manuale HR"
├── chunk 1: ferie
├── chunk 2: buste paga
└── chunk 3: note spese
```

I **metadati** sono dati che descrivono il contenuto: titolo, fonte, data, lingua,
tenant e ruoli ammessi. Non sono il testo principale, ma servono a filtrare,
aggiornare e citare.

Un **indice** è una struttura preparata per cercare velocemente. L'indice di un libro
rimanda da una parola alle pagine; un indice software svolge un compito simile su
molti contenuti.

La **query** è la richiesta di ricerca. Può essere composta da parole, come
`reset password`, o da una domanda, come `Come recupero l'accesso?`.

## 3. Preparare i documenti: ingestion e chunking

L'**ingestion**, cioè acquisizione, è il processo che legge le fonti e le rende
ricercabili:

```text
fonti -> estrazione testo -> pulizia -> chunk -> metadati -> indice
```

Il **chunking** è la divisione in blocchi.

- Chunk troppo piccolo: può separare una regola dalla sua eccezione.
- Chunk troppo grande: aggiunge rumore e consuma token.
- Divisione per sezioni e paragrafi: conserva meglio il significato.

Ogni chunk dovrebbe mantenere almeno identificatore, documento di origine, testo,
sezione, versione e permessi.

Esempio:

```python
chunk = {
    "id": "hr-001-ferie",
    "documento": "manuale-hr",
    "sezione": "Ferie",
    "testo": "Le ferie devono essere approvate dal responsabile.",
    "tenant_id": "azienda-a",
    "ruoli": ["dipendente", "manager"],
}
```

Senza `documento` e `sezione` non puoi costruire una citazione utile. Senza
`tenant_id` e `ruoli` rischi di recuperare dati per la persona sbagliata.

## 4. Ricerca lessicale e idea di BM25

La ricerca **lessicale** confronta le parole della query con quelle dei documenti.
È simile a `Ctrl+F`, ma può assegnare un punteggio e ordinare tutti i risultati.

**BM25** è un algoritmo di ranking, cioè ordinamento per rilevanza. In linguaggio
semplice:

1. premia un documento che contiene le parole cercate;
2. premia di più parole rare, perché distinguono meglio;
3. evita che ripetere una parola cento volte dia cento volte il vantaggio;
4. compensa la lunghezza, così un documento enorme non vince solo perché contiene
   quasi ogni parola.

Esempio: la query `errore payroll PX-104` contiene un codice raro. BM25 tende a essere
molto efficace perché il codice esatto è più informativo della parola comune
`errore`.

BM25 non “capisce” automaticamente che `cedolino` e `busta paga` sono simili se le
parole non coincidono.

## 5. Embedding e similarità

Un **embedding** è una lista di numeri che rappresenta il significato appreso di un
testo. Un modello di embedding trasforma query e chunk in vettori.

Analogia: immaginiamo una mappa. Testi sulle ferie finiscono vicini; testi sulle reti
informatiche finiscono in un'altra zona. La posizione non è una coordinata geografica,
ma un insieme di numeri appreso dal modello.

```text
"non vedo il cedolino" -> [0,8, 0,1, 0,4]
"manca la busta paga"  -> [0,75, 0,12, 0,42]
"configura il router"  -> [0,05, 0,9, 0,02]
```

La **similarità**, cioè misura di somiglianza, confronta due vettori. Una misura comune
è la similarità del coseno: guarda quanto i vettori puntano nella stessa direzione.
Un valore maggiore indica in genere maggiore vicinanza nel modello, non una
probabilità che la risposta sia corretta.

La ricerca tramite embedding è detta spesso **semantica**, perché può avvicinare
sinonimi. Può però perdere codici esatti, nomi rari o dettagli numerici. Per questo
non sostituisce sempre BM25.

## 6. Dalle basi al retrieval ibrido

Il **retrieval ibrido** unisce ricerca lessicale e ricerca tramite embedding.

Esempio:

- BM25 trova `PX-104` perché coincide esattamente;
- embedding trova `cedolino` per la query `busta paga`;
- la combinazione conserva entrambi i vantaggi.

I due sistemi producono punteggi su scale diverse. Sommarli direttamente può essere
fuorviante. **RRF**, da *Reciprocal Rank Fusion*, cioè fusione dei ranghi reciproci,
combina invece le posizioni nelle classifiche:

```text
punteggio = somma di 1 / (costante + posizione)
```

Un documento primo in entrambe le liste riceve più credito di uno presente in una
sola lista e molto in basso. La costante riduce differenze troppo aggressive.

Dopo aver recuperato, per esempio, 30 candidati, possiamo usare un **reranker**, cioè
un secondo ordinatore più accurato e costoso. Il reranker legge insieme query e
testo, poi riordina pochi candidati. Non può recuperare un documento escluso dalla
prima fase: prima serve un buon richiamo, poi si migliora l'ordine.

## 7. La pipeline RAG completa

**RAG** significa *Retrieval-Augmented Generation*, cioè generazione aumentata dal
recupero. La pipeline completa è:

```text
documenti
  -> acquisizione
  -> chunk e metadati
  -> indice

utente autenticato + domanda
  -> filtro tenant e permessi
  -> retrieval
  -> eventuale fusione e reranking
  -> pochi chunk con identificatori
  -> prompt con domanda e fonti
  -> modello linguistico
  -> risposta o astensione
  -> verifica delle citazioni
```

Il retrieval porta informazioni nel contesto della singola richiesta. Non modifica
permanentemente il modello.

Il modello deve poter dire: “Non trovo informazioni sufficienti nelle fonti
autorizzate”. Questa **astensione** è migliore di una risposta inventata.

Le citazioni devono riferirsi solo agli identificatori effettivamente recuperati.
L'applicazione deve verificarle prima di mostrarle.

## 8. Metriche con un esempio calcolato

Per valutare il retrieval prepariamo un insieme di risposte attese, chiamato
**golden set**. Per una domanda, supponiamo che i documenti rilevanti siano:

```text
{A, C}
```

Il sistema restituisce i primi cinque:

```text
[B, A, D, C, E]
```

**Recall@k**, cioè richiamo ai primi `k`, risponde: “Quanti documenti rilevanti ho
trovato fra tutti quelli rilevanti?”.

Ai primi 3 risultati troviamo solo `A`:

```text
Recall@3 = 1 trovato / 2 rilevanti = 0,50
```

**Precision@k**, cioè precisione ai primi `k`, risponde: “Quanti dei risultati mostrati
sono rilevanti?”.

```text
Precision@3 = 1 rilevante / 3 risultati = 0,33
```

**Reciprocal Rank** è l'inverso della posizione del primo risultato rilevante. Qui `A`
è secondo:

```text
Reciprocal Rank = 1 / 2 = 0,50
```

**MRR**, da *Mean Reciprocal Rank*, è la media dei reciprocal rank su più domande. Se
tre domande hanno il primo rilevante alle posizioni 1, 2 e 4:

```text
MRR = (1/1 + 1/2 + 1/4) / 3
    = (1 + 0,50 + 0,25) / 3
    = 1,75 / 3
    = 0,58
```

### Domande senza risposta

Se nel corpus non esiste alcuna fonte rilevante, Recall produce una divisione `0/0`.
Non inserire questi casi nella stessa media.

Valutali separatamente:

- percentuale di astensioni corrette;
- percentuale di false risposte;
- numero di risultati non autorizzati, che deve essere zero.

Questa separazione impedisce di premiare un sistema che recupera sempre qualcosa,
anche quando non dovrebbe rispondere.

## 9. Sicurezza: tenant e ACL

Un **tenant** è un cliente o spazio organizzativo isolato dagli altri. Un servizio può
contenere documenti di `azienda-a` e `azienda-b`, ma un utente della prima non deve
vedere quelli della seconda.

Una **ACL**, da *Access Control List*, cioè lista di controllo degli accessi, descrive
chi può leggere una risorsa.

Analogia: in una biblioteca aziendale, il badge decide quali stanze puoi aprire. Non
portiamo prima tutti i fascicoli sul tavolo per poi nascondere quelli vietati. Il
filtro deve avvenire prima o durante la ricerca.

Sequenza corretta:

```text
identità verificata -> tenant e ruoli dal server -> ricerca filtrata -> risultati
```

Il modello non deve scegliere liberamente `tenant_id`. Il valore arriva
dall'autenticazione. Anche log, cache, reranker e prompt devono ricevere soltanto dati
autorizzati.

## 10. Programma locale completo

Questo laboratorio implementa un piccolo retrieval lessicale ispirato ai principi di
BM25. Per chiarezza non replica ogni dettaglio matematico della libreria
`rank-bm25`, ma include frequenza, rarità e normalizzazione della lunghezza.

Copia in `rag_locale.py`:

```python
import math
import re
from collections import Counter


STOP_WORDS = {
    "a", "al", "alla", "che", "come", "da", "di", "dove", "e", "è",
    "gli", "i", "il", "in", "la", "le", "lo", "per", "qual", "un", "una",
}

DOCUMENTI = [
    {
        "id": "hr-ferie",
        "tenant_id": "azienda-a",
        "titolo": "Ferie",
        "testo": "Le ferie devono essere richieste nel portale e approvate dal manager.",
    },
    {
        "id": "hr-payroll",
        "tenant_id": "azienda-a",
        "titolo": "Cedolino",
        "testo": "La busta paga si scarica dal portale Payroll nella sezione Documenti.",
    },
    {
        "id": "it-password",
        "tenant_id": "azienda-a",
        "titolo": "Password",
        "testo": "Per reimpostare la password usa il collegamento Recupera accesso.",
    },
    {
        "id": "segreto-b",
        "tenant_id": "azienda-b",
        "titolo": "Budget",
        "testo": "Il budget riservato di azienda-b è 900000 euro.",
    },
]


def tokenizza(testo: str) -> list[str]:
    token = re.findall(r"[a-zà-ù0-9]+", testo.lower())
    return [parola for parola in token if parola not in STOP_WORDS]


def cerca(query: str, tenant_id: str, limite: int = 3) -> list[dict]:
    autorizzati = [
        documento
        for documento in DOCUMENTI
        if documento["tenant_id"] == tenant_id
    ]
    if not autorizzati:
        return []

    query_token = tokenizza(query)
    documenti_token = [tokenizza(d["testo"]) for d in autorizzati]
    lunghezza_media = sum(map(len, documenti_token)) / len(documenti_token)

    risultati = []
    for documento, token in zip(autorizzati, documenti_token, strict=True):
        frequenze = Counter(token)
        punteggio = 0.0
        for parola in query_token:
            documenti_con_parola = sum(parola in t for t in documenti_token)
            rarita = math.log(
                1 + (len(documenti_token) - documenti_con_parola + 0.5)
                / (documenti_con_parola + 0.5)
            )
            frequenza = frequenze[parola]
            normalizzazione = frequenza + 1.2 * (
                0.25 + 0.75 * len(token) / lunghezza_media
            )
            if frequenza:
                punteggio += rarita * (frequenza * 2.2) / normalizzazione

        if punteggio > 0:
            risultati.append({**documento, "punteggio": round(punteggio, 3)})

    return sorted(
        risultati,
        key=lambda risultato: risultato["punteggio"],
        reverse=True,
    )[:limite]


def rispondi(query: str, tenant_id: str) -> dict:
    fonti = cerca(query, tenant_id)
    if not fonti:
        return {
            "risposta": "Non trovo informazioni sufficienti nelle fonti autorizzate.",
            "fonti": [],
        }

    migliore = fonti[0]
    return {
        "risposta": migliore["testo"],
        "fonti": [migliore["id"]],
    }


if __name__ == "__main__":
    casi = [
        ("Dove scarico la busta paga?", "azienda-a"),
        ("Come cambio la password?", "azienda-a"),
        ("Qual è il budget riservato?", "azienda-a"),
    ]
    for domanda, tenant in casi:
        risultato = rispondi(domanda, tenant)
        print(f"Domanda: {domanda}")
        print(f"Risposta: {risultato['risposta']}")
        print(f"Fonti: {risultato['fonti']}\n")
```

Esegui:

```powershell
python rag_locale.py
```

Output atteso:

```text
Domanda: Dove scarico la busta paga?
Risposta: La busta paga si scarica dal portale Payroll nella sezione Documenti.
Fonti: ['hr-payroll']

Domanda: Come cambio la password?
Risposta: Per reimpostare la password usa il collegamento Recupera accesso.
Fonti: ['it-password']

Domanda: Qual è il budget riservato?
Risposta: Non trovo informazioni sufficienti nelle fonti autorizzate.
Fonti: []
```

Il filtro `tenant_id` viene applicato prima del punteggio. Il documento di
`azienda-b` non entra quindi nel retrieval di `azienda-a`. `rispondi` è una
generazione estrattiva molto semplice: riusa una fonte anziché chiamare un LLM. È
voluto, perché permette di capire e testare il retrieval separatamente. La piccola
lista `STOP_WORDS` evita che parole comuni come `il` bastino da sole a creare una
falsa corrispondenza. In produzione lista, lingua e soglia vanno valutate su casi
reali, non scelte a intuito.

## 11. Laboratorio guidato

1. **Crea `rag_locale.py` con il programma.**
   Verifica: `python rag_locale.py` termina senza errori.
2. **Controlla il caso busta paga.**
   Verifica: la fonte è `hr-payroll`.
3. **Controlla l'isolamento.**
   Verifica: la domanda sul budget fatta da `azienda-a` non restituisce
   `segreto-b`.
4. **Ripeti come `azienda-b`.**
   Cambia il tenant dell'ultima domanda.
   Verifica: ora la fonte può essere `segreto-b`.
5. **Aggiungi un documento sulle note spese.**
   Verifica: una query con parole presenti lo recupera.
6. **Prova un sinonimo assente.**
   Cerca `credenziali dimenticate`.
   Verifica: il sistema lessicale può non trovare `password`; annota il limite.
7. **Crea cinque query attese.**
   Per ciascuna scrivi prima l'identificatore rilevante o “senza risposta”.
   Verifica: calcola Recall@3 solo sui casi con risposta e astensione sui restanti.

## 12. Esercizi graduati

### Base

1. Aggiungi il metadato `ruoli` e filtra anche per ruolo.
2. Restituisci titolo e punteggio oltre all'identificatore.
3. Impedisci valori `limite` minori di 1 o maggiori di 10.

### Intermedio

1. Implementa `reciprocal_rank_fusion` per unire due classifiche di identificatori.
2. Calcola automaticamente Recall@3 e Precision@3 per cinque query con risposta.
3. Calcola separatamente la percentuale di astensione corretta per query senza
   risposta.

### Avanzato

Aggiungi un vero modello di embedding locale e confrontalo con BM25 sugli stessi
casi. Poi combina le classifiche con RRF. Cambia una sola variabile per esperimento e
misura qualità e tempo.

## 13. Soluzioni ragionate

Filtro per ruolo:

```python
def autorizzato(documento: dict, tenant_id: str, ruolo: str) -> bool:
    stesso_tenant = documento["tenant_id"] == tenant_id
    ruolo_ammesso = ruolo in documento["ruoli"]
    return stesso_tenant and ruolo_ammesso
```

Questa funzione deve essere usata prima di calcolare punteggi o costruire prompt.

Per mostrare titolo e punteggio, seleziona i campi già restituiti da `cerca`:

```python
[
    {
        "id": risultato["id"],
        "titolo": risultato["titolo"],
        "punteggio": risultato["punteggio"],
    }
    for risultato in cerca("busta paga", "azienda-a")
]
```

Valida `limite` all'inizio di `cerca`:

```python
if not 1 <= limite <= 10:
    raise ValueError("limite deve essere compreso fra 1 e 10")
```

Soluzione RRF:

```python
from collections import defaultdict


def reciprocal_rank_fusion(
    classifiche: list[list[str]],
    costante: int = 60,
) -> list[str]:
    punteggi: dict[str, float] = defaultdict(float)
    for classifica in classifiche:
        for posizione, documento_id in enumerate(classifica, start=1):
            punteggi[documento_id] += 1 / (costante + posizione)
    return sorted(punteggi, key=punteggi.__getitem__, reverse=True)


assert reciprocal_rank_fusion(
    [["A", "B", "C"], ["B", "A", "D"]]
)[:2] == ["A", "B"]
```

`A` e `B` sono presenti in entrambe le classifiche e ottengono lo stesso punteggio:
uno è primo e secondo, l'altro secondo e primo. Python conserva qui l'ordine di
inserimento e mette `A` prima di `B`. In una valutazione reale devi gestire
esplicitamente anche i pareggi.

Metriche per una query:

```python
def metriche(rilevanti: set[str], risultati: list[str], k: int) -> tuple[float, float]:
    primi_k = risultati[:k]
    trovati = len(rilevanti.intersection(primi_k))
    recall = trovati / len(rilevanti)
    precision = trovati / k
    return recall, precision


assert metriche({"A", "C"}, ["B", "A", "D", "C"], 3) == (0.5, 1 / 3)
```

Chiama questa funzione solo quando `rilevanti` non è vuoto. I casi senza risposta
richiedono la metrica di astensione separata.

Per più query, calcola ogni coppia di metriche e poi la media. Per i casi senza
risposta usa invece:

```python
def astensione_corretta(risultati: list[str]) -> bool:
    return len(risultati) == 0
```

La percentuale è il numero di `True` diviso per il totale dei casi senza risposta.

### Soluzione avanzata: criteri di verifica

Una soluzione adeguata usa lo stesso golden set per lessicale, embedding e ibrido;
misura almeno Recall@3, MRR e latenza; registra modello e versione; applica gli
stessi filtri di autorizzazione prima di ogni ranking. Il risultato non deve essere
"l'embedding sembra migliore", ma una tabella comparabile che mostra su quali query
ogni variante vince o perde.

## 14. Errori comuni

- **Partire dal database vettoriale.** Prima definisci documenti, query e misura; lo
  strumento non corregge dati scadenti.
- **Usare solo embedding.** Codici, nomi e numeri possono favorire BM25.
- **Creare chunk enormi.** Aumentano rumore, costo e rischio di perdere il dettaglio.
- **Filtrare permessi dopo il retrieval.** Dati vietati possono già arrivare a log,
  cache, reranker o modello.
- **Valutare soltanto la risposta finale.** Se la fonte non viene recuperata, cambiare
  prompt non risolve il problema.
- **Trattare il punteggio come probabilità.** È un valore di ordinamento dipendente dal
  sistema.
- **Forzare sempre una risposta.** Le query senza fonte devono poter produrre
  astensione.
- **Accettare citazioni inventate.** Verifica che ogni identificatore sia fra i chunk
  forniti al modello.
- **Mescolare casi con e senza risposta nel Recall.** Misurali in segmenti distinti.

## 15. Domande di autoverifica

**Perché `Ctrl+F` non basta su un grande corpus?**  
Perché cerca parole esatte, spesso in un file, senza ranking semantico e filtri
completi.

**Che differenza c'è fra documento e chunk?**  
Il documento è l'unità originale; il chunk è una sua porzione indicizzata.

**A che cosa servono i metadati?**  
A filtrare, citare, aggiornare e applicare permessi.

**Qual è il punto forte di BM25?**  
Parole esatte, termini rari, codici e nomi.

**Che cosa rappresenta un embedding?**  
Un testo come vettore numerico in uno spazio appreso.

**Perché usare retrieval ibrido?**  
Per combinare i punti forti della ricerca lessicale e semantica.

**Che cosa misura Recall@3?**  
La quota di tutti i documenti rilevanti trovata nei primi tre risultati.

**Come valuti una domanda senza risposta nel corpus?**  
Con astensione corretta e false risposte, non con Recall.

**Quando va applicato il filtro tenant?**  
Prima o durante il retrieval, mai affidandolo al modello.

## Approfondimento tecnico

Dopo il laboratorio, continua con la
[GUIDA tecnica su RAG in produzione](GUIDA.md).
