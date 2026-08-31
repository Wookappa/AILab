# Lezione passo-passo: partire da zero

## Cosa saprai fare alla fine

Alla fine di questa lezione saprai:

1. orientarti fra file e cartelle;
2. aprire un terminale ed eseguire un comando;
3. spiegare che cosa sono Python, Git e un ambiente virtuale;
4. installare le dipendenze del corso;
5. eseguire un piccolo programma Python;
6. leggere un file JSONL;
7. lanciare un test automatico;
8. capire a cosa servono `pytest`, Ruff e mypy.

Non devi conoscere già questi termini: vengono spiegati prima di usarli.

## Cosa devi sapere prima

Nulla. Questa è la prima lezione. Ti serve soltanto un computer Windows su cui puoi
installare programmi e creare file. Se un comando produce un risultato diverso da
quello mostrato, fermati su quel passaggio e confronta con la sezione **Errori
comuni** prima di proseguire.

## 1. Le quattro cose con cui lavorerai

### File

Un **file** contiene informazioni. Esempi:

- `README.md`: testo formattato;
- `stats.py`: codice Python;
- `tickets.jsonl`: dati;
- `pyproject.toml`: configurazione del progetto.

L'estensione dopo il punto suggerisce il formato. `.py` indica normalmente un file
Python. L'estensione non rende il file sicuro o corretto: descrive solo come dovrebbe
essere interpretato.

### Cartella

Una **cartella** raggruppa file e altre cartelle. Questo corso è dentro:

```text
AILab/
  AI-Mastery-Accelerator/
    00-setup/
    01-python-production/
    ...
```

### Programma

Un **programma** è una sequenza di istruzioni eseguita dal computer. Il codice sorgente
è il testo scritto dal programmatore; Python lo legge e lo esegue.

### Terminale

Il **terminale** è una finestra in cui scrivi comandi. Su Windows useremo PowerShell.
Un comando è una richiesta come "mostra la versione di Python" o "esegui questo file".

Apri PowerShell dal menu Start e scrivi:

```powershell
Get-Location
```

Output simile:

```text
Path
----
C:\Users\tuo-nome
```

`Get-Location` mostra la cartella in cui ti trovi. Non copiare il simbolo del prompt,
se presente: scrivi solo il comando.

## 2. Che cosa sono gli strumenti

### Python

**Python** è il linguaggio di programmazione principale del corso. Il programma
`python.exe`, chiamato interprete, legge ed esegue i file `.py`.

Verifica:

```powershell
python --version
```

Output atteso:

```text
Python 3.12.x
```

`x` può essere un numero diverso. Se `python` non viene trovato, installa Python 3.12
dal sito ufficiale e abilita l'opzione che aggiunge Python al `PATH`. Il `PATH` è
l'elenco di cartelle in cui il terminale cerca i programmi.

Su Windows può funzionare anche:

```powershell
py -3.12 --version
```

### Git

**Git** registra la storia dei file: che cosa è cambiato, quando e in quale versione.
Un progetto seguito da Git è chiamato **repository**.

Verifica:

```powershell
git --version
```

**GitHub** è un servizio online che ospita repository Git. Git e GitHub non sono la
stessa cosa: Git è lo strumento; GitHub è uno dei servizi che lo usa.

### Editor

Un **editor di codice** è il programma in cui leggi e modifichi i file. Puoi usare
Visual Studio Code con l'estensione Python. L'editor aiuta, ma il terminale resta utile
per capire esattamente che cosa viene eseguito.

### Docker

**Docker** esegue applicazioni in container, ambienti isolati e riproducibili. Non
serve nella prima lezione. Lo installerai prima dei moduli data platform e deploy.

## 3. Scaricare il corso

Scegli una cartella in cui conservare i progetti, poi esegui:

```powershell
git clone https://github.com/Wookappa/AILab.git
cd AILab\AI-Mastery-Accelerator
```

`git clone` scarica una copia della repository. `cd`, abbreviazione di *change
directory*, entra nella cartella indicata.

Controlla:

```powershell
Get-Location
Get-ChildItem
```

`Get-ChildItem` elenca i file. Dovresti vedere `pyproject.toml`, `00-setup` e le altre
cartelle del corso.

Se hai già scaricato la repository, non clonarla di nuovo: apri PowerShell nella
cartella esistente e usa `cd`.

## 4. Creare un ambiente virtuale

### Il problema

Progetti diversi possono richiedere versioni diverse della stessa libreria. Installare
tutto globalmente crea conflitti.

### La soluzione

Un **ambiente virtuale** è una cartella contenente un'installazione Python isolata per
il progetto.

Crealo:

```powershell
py -3.12 -m venv .venv
```

Spiegazione:

- `py -3.12`: usa Python 3.12;
- `-m venv`: esegue il modulo standard che crea ambienti virtuali;
- `.venv`: nome della cartella da creare.

Attivalo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Il prompt dovrebbe iniziare con `(.venv)`. Da questo momento `python` e `pip` indicano
le copie dell'ambiente.

Se PowerShell blocca lo script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

`-Scope Process` limita la modifica alla finestra corrente.

Controlla quale Python stai usando:

```powershell
python -c "import sys; print(sys.executable)"
```

Il percorso deve contenere `AI-Mastery-Accelerator\.venv`.

## 5. Installare il progetto

Una **dipendenza** è codice esterno usato dal progetto. Un **pacchetto Python** è un
insieme installabile di moduli Python. `pip` è lo strumento che installa pacchetti.

Esegui:

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Spiegazione:

- `-e`: installazione editable; le modifiche locali sono visibili senza reinstallare;
- `.`: il progetto nella cartella corrente;
- `[dev]`: strumenti di sviluppo dichiarati nel `pyproject.toml`.

Non stai installando ancora tutte le librerie AI: arriveranno quando servono.

## 6. Il primo programma

Esegui:

```powershell
python -c "print('Python funziona')"
```

`-c` esegue il testo che segue come codice Python. `print` mostra un valore.

Output:

```text
Python funziona
```

Ora esegui il programma incluso nel corso:

```powershell
python -m ai_mastery.setup_basics examples\tickets.jsonl
```

Output:

```text
Record validi: 4
Conteggi per label:
- contract: 1
- leave: 1
- payroll: 2
```

Che cosa è successo?

1. Python ha aperto `examples\tickets.jsonl`;
2. ha letto una riga alla volta;
3. ha controllato che ogni riga avesse `id`, `text` e `label`;
4. ha contato i record con la stessa label;
5. ha stampato il risultato.

Apri `src\ai_mastery\setup_basics.py` nell'editor. Non devi ancora capire ogni
istruzione. Segui l'ordine:

```text
input file -> lettura -> validazione -> conteggio -> output
```

## 7. Che cosa sono JSON e JSONL

**JSON** è un formato testuale per rappresentare dati con chiavi e valori:

```json
{
  "id": "t-001",
  "text": "Il totale del cedolino non è corretto",
  "label": "payroll"
}
```

- `id` è la chiave; `"t-001"` è il valore;
- le stringhe sono fra doppi apici;
- le coppie sono separate da virgole.

**JSONL**, o JSON Lines, contiene un oggetto JSON completo su ogni riga:

```json
{"id":"t-001","text":"Cedolino errato","label":"payroll"}
{"id":"t-002","text":"Richiesta ferie","label":"leave"}
```

È comodo per dataset grandi perché il programma può elaborare una riga alla volta
senza caricare tutto in memoria.

## 8. Leggere il programma senza magia

Una versione semplificata:

```python
from collections import Counter

labels = ["payroll", "leave", "payroll"]
counts = Counter(labels)
print(counts["payroll"])
```

Output:

```text
2
```

- `from ... import ...` rende disponibile codice di una libreria;
- `labels` è una variabile: un nome associato a un valore;
- `[...]` crea una lista;
- `Counter` conta quante volte appare ogni elemento;
- `counts["payroll"]` recupera il conteggio della chiave `payroll`.

Il modulo Python successivo spiegherà variabili, funzioni, liste e dizionari con calma.

## 9. Test automatici

Un **test automatico** esegue codice e controlla che il risultato sia quello previsto.

Esegui:

```powershell
python -m pytest
```

Output finale atteso:

```text
... passed
```

Il numero esatto dipende da quanti laboratori sono già presenti nella versione del
corso. La parte importante è che non compaia `failed`.

Un test usa spesso `assert`:

```python
tickets = [
    {"id": "t-1", "text": "Cedolino", "label": "payroll"},
    {"id": "t-2", "text": "Ferie", "label": "leave"},
    {"id": "t-3", "text": "Voce mancante", "label": "payroll"},
]
assert count_labels(tickets) == {
    "payroll": 2,
    "leave": 1,
}
```

Se i due valori non coincidono, il test fallisce e indica dove. Un test non dimostra
che non esistano errori; verifica casi specifici e rende visibili le regressioni.
Una **regressione** è un comportamento che funzionava e viene rotto da una modifica.

## 10. Ruff e mypy

Esegui:

```powershell
ruff check src tests
mypy src tests
```

Output atteso:

```text
All checks passed!
Success: no issues found in ... source files
```

Il numero di file può crescere nelle versioni successive del corso.

**Ruff** è un linter: cerca errori e problemi di stile senza eseguire il programma.

**mypy** è un type checker: confronta le annotazioni di tipo con l'uso dei valori.

Esempio:

```python
def double(value: int) -> int:
    return value * 2

double("ciao")
```

`value: int` dice che la funzione accetta un numero intero. mypy segnala che `"ciao"`
è testo, quindi il chiamante probabilmente ha sbagliato.

I tipi non sostituiscono i test:

- mypy controlla compatibilità strutturale;
- pytest controlla comportamento su esempi;
- Ruff trova altre classi di errore.

## 11. Che cosa significano AI, ML e LLM

Per ora basta questa mappa:

- **AI (Artificial Intelligence, intelligenza artificiale):** insieme ampio di
  tecniche per costruire sistemi che svolgono compiti associati all'intelligenza;
- **ML (Machine Learning, apprendimento automatico):** sistemi che apprendono regole
  da dati invece di riceverle tutte scritte a mano;
- **modello:** funzione con parametri appresi dai dati;
- **LLM (Large Language Model):** modello addestrato su testo per elaborare e generare
  sequenze di token;
- **token:** piccola unità di testo elaborata dal modello;
- **notebook:** documento interattivo con celle di codice, utile per esplorare;
- **servizio:** programma sempre disponibile che riceve richieste da altri programmi;
- **API:** regole con cui due programmi si scambiano richieste e risposte.

Non serve memorizzare tutto ora. Ogni concetto verrà ricostruito nel suo modulo.

## 12. Laboratorio guidato

### Passo 1: crea una copia e aggiungi un record

Non modificare il file originale, perché viene usato dai test. Copialo:

```powershell
Copy-Item examples\tickets.jsonl examples\tickets-extra.jsonl
```

Apri `examples\tickets-extra.jsonl`, vai a capo dopo l'ultima riga e aggiungi:

```json
{"id":"t-005","text":"Devo modificare il contratto","label":"contract"}
```

Esegui:

```powershell
python -m ai_mastery.setup_basics examples\tickets-extra.jsonl
```

Il totale deve diventare 5 e `contract` deve diventare 2. I test continuano a usare
il file originale da quattro record.

### Passo 2: prova un errore

Copia `examples\tickets-extra.jsonl` in `examples\tickets-invalid.jsonl` e rimuovi
`label` da una riga.

Esegui:

```powershell
python -m ai_mastery.setup_basics examples\tickets-invalid.jsonl
```

Il programma deve terminare con un messaggio che indica la riga invalida. Questo è
meglio di ignorare silenziosamente dati incompleti.

### Passo 3: aggiungi un test

Apri `tests\test_setup_basics.py` e aggiungi:

```python
def test_empty_labels_produce_empty_counts() -> None:
    assert count_labels([]) == {}
```

Riesegui `python -m pytest`. Ora il totale deve aumentare di un test.

## 13. Esercizi graduati

### Base

Modifica la stampa per mostrare prima la label più frequente.

### Intermedio

Aggiungi una funzione che calcoli la lunghezza media del campo `text`.

### Avanzato

Aggiungi l'opzione `--label payroll` per contare solo una label. Prima di modificare il
codice, scrivi un test che descriva il comportamento desiderato.

## 14. Soluzioni ragionate

### Soluzione base

`Counter.most_common()` restituisce coppie ordinate per frequenza:

```python
for label, count in counts.most_common():
    print(f"- {label}: {count}")
```

### Soluzione intermedia

La media è somma delle lunghezze divisa per numero di record:

```python
def average_text_length(records: list[dict[str, str]]) -> float:
    if not records:
        return 0.0
    total = sum(len(record["text"]) for record in records)
    return total / len(records)
```

Il controllo della lista vuota evita una divisione per zero.

### Soluzione avanzata

Usa `argparse` per leggere un'opzione senza interpretare manualmente `sys.argv`.
La funzione che filtra resta separata e quindi testabile:

```python
def filter_by_label(records: list[Ticket], label: str | None) -> list[Ticket]:
    if label is None:
        return records
    return [record for record in records if record["label"] == label]
```

Nel `main`, applicala subito dopo il caricamento. Prima scrivi almeno questi casi:
senza filtro conserva tutti i record; con `payroll` conserva soltanto i record
payroll; con una label assente restituisce una lista vuota.

## 15. Errori comuni

- Eseguire i comandi dalla cartella sbagliata: usa `Get-Location` e verifica che il
  percorso termini con `AI-Mastery-Accelerator`.
- Copiare anche il simbolo `>` del terminale: copia soltanto il comando.
- Usare `pip` fuori dall'ambiente virtuale: il prompt deve iniziare con `(.venv)`.
- Salvare `tickets.jsonl` come `tickets.jsonl.txt`: abilita la visualizzazione delle
  estensioni in Esplora file.
- Inserire più oggetti sulla stessa riga JSONL: ogni riga deve essere un JSON
  completo.
- Correggere il codice senza rileggere il primo messaggio di errore: parti dalla
  prima riga che indica un tuo file.

## 16. Domande di autoverifica

**Che differenza c'è fra Git e GitHub?**  
Git registra versioni localmente; GitHub ospita repository online.

**Perché creiamo `.venv`?**  
Per isolare dipendenze e versioni di questo progetto dagli altri.

**Che differenza c'è fra JSON e JSONL?**  
JSON rappresenta un valore completo; JSONL contiene un oggetto JSON indipendente per
riga.

**Perché un test può passare anche se esiste un bug?**  
Perché verifica soltanto i casi che abbiamo scritto.

**Che cosa fa `python -m`?**  
Chiede a Python di eseguire un modulo importabile.

## 17. Quando hai davvero finito

Passa al modulo successivo quando:

- sai entrare nella cartella corretta;
- l'ambiente virtuale è attivo;
- il programma produce i conteggi;
- hai provocato e compreso un errore;
- i test passano;
- sai spiegare file, terminale, repository, dipendenza e test.

Solo dopo questa lezione usa la [guida avanzata su metodo e
riproducibilità](GUIDA.md).
