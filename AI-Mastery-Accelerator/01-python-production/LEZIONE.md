# Lezione passo-passo: Python dalle basi a un piccolo servizio

## Cosa saprai fare alla fine

Saprai:

1. usare variabili, stringhe, numeri, liste e dizionari;
2. prendere decisioni con `if` e ripetere operazioni con `for`;
3. scrivere funzioni;
4. segnalare e gestire errori;
5. rappresentare dati con classi e Pydantic;
6. usare annotazioni di tipo;
7. capire la differenza fra codice sincrono e asincrono;
8. costruire e testare un piccolo servizio.

## Cosa devi sapere prima

Completa [la lezione di setup](../00-setup/LEZIONE.md). Devi saper attivare `.venv`,
eseguire `python -m ...` e lanciare `pytest`.

## 1. Il problema che risolveremo

Costruiremo un piccolo servizio che riceve una domanda HR e restituisce una risposta.
All'inizio userà regole semplici, non un modello AI:

```text
domanda -> controllo input -> generatore -> risposta
```

Separare le parti ci permetterà più avanti di sostituire il generatore con un LLM
senza riscrivere tutto.

## 2. Valori e variabili

Un **valore** è un dato. Una **variabile** è un nome associato a un valore.

```python
employee_name = "Anna"
vacation_days = 12
is_manager = False
```

- `"Anna"` è una stringa, cioè testo;
- `12` è un intero;
- `False` è un booleano, cioè vero/falso.

Il simbolo `=` assegna il valore a destra al nome a sinistra. Non significa
"matematicamente uguale".

Visualizza i valori:

```python
print(employee_name)
print(vacation_days)
```

Le variabili distinguono maiuscole e minuscole: `name` e `Name` sono nomi diversi.

## 3. Liste e dizionari

### Lista

Una **lista** conserva valori in ordine:

```python
labels = ["payroll", "leave", "contract"]
print(labels[0])
```

Output:

```text
payroll
```

L'indice parte da zero. `labels[0]` è il primo elemento.

### Dizionario

Un **dizionario** associa chiavi e valori:

```python
ticket = {
    "id": "t-001",
    "text": "Come richiedo le ferie?",
    "label": "leave",
}
print(ticket["text"])
```

Un dizionario assomiglia a un oggetto JSON, ma è un valore Python in memoria.

## 4. Condizioni

`if` esegue codice soltanto quando una condizione è vera:

```python
days_requested = 3
days_available = 10

if days_requested <= days_available:
    print("Richiesta possibile")
else:
    print("Giorni insufficienti")
```

I quattro spazi iniziali sono **indentazione**. In Python definiscono quali righe
appartengono al blocco. Non sono decorazione.

Operatori utili:

| Operatore | Significato |
|---|---|
| `==` | uguale |
| `!=` | diverso |
| `<`, `>` | minore, maggiore |
| `<=`, `>=` | minore/uguale, maggiore/uguale |
| `and` | entrambe le condizioni |
| `or` | almeno una condizione |
| `not` | nega la condizione |

## 5. Cicli

Un **ciclo** ripete un blocco:

```python
questions = [
    "Come richiedo le ferie?",
    "Quando arriva il cedolino?",
]

for question in questions:
    print(question)
```

Ad ogni giro, `question` contiene un elemento diverso.

Usa `for` quando attraversi una collezione. Evita di modificare la stessa lista mentre
la stai attraversando: spesso crea comportamenti difficili da capire.

## 6. Funzioni

Una **funzione** è codice con un nome che può ricevere input e restituire output:

```python
def normalize_question(question: str) -> str:
    return question.strip().lower()
```

Spiegazione:

- `def` inizia la definizione;
- `question` è un parametro;
- `: str` indica che ci aspettiamo testo;
- `-> str` indica che restituiamo testo;
- `strip()` rimuove spazi iniziali/finali;
- `lower()` converte in minuscolo;
- `return` restituisce il risultato.

Uso:

```python
normalized = normalize_question("  Come Richiedo le Ferie?  ")
print(normalized)
```

Output:

```text
come richiedo le ferie?
```

Una funzione dovrebbe avere una responsabilità chiara. "Normalizzare una domanda" è
più facile da testare di "fare tutto".

## 7. Errori ed eccezioni

Un'**eccezione** segnala che l'operazione non può continuare normalmente.

```python
def validate_question(question: str) -> str:
    cleaned = question.strip()
    if len(cleaned) < 3:
        raise ValueError("La domanda deve contenere almeno 3 caratteri")
    return cleaned
```

`raise` interrompe la funzione. `ValueError` dice che il valore ricevuto non è valido.

Il chiamante può gestire un errore previsto:

```python
try:
    validate_question(" ")
except ValueError as error:
    print(f"Input non valido: {error}")
```

Non scrivere:

```python
try:
    do_everything()
except Exception:
    pass
```

Questo nasconde qualunque errore e fa sembrare riuscita un'operazione fallita.

## 8. Classi e oggetti

Una **classe** definisce dati e comportamento di un tipo di oggetto.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Answer:
    text: str
    source: str
```

Uso:

```python
answer = Answer(
    text="Apri la sezione Ferie.",
    source="policy-leave.md",
)
print(answer.text)
```

`@dataclass` genera automaticamente codice ripetitivo come il costruttore.
`frozen=True` impedisce modifiche dopo la creazione: utile per valori che devono
rimanere coerenti.

## 9. Validare input con Pydantic

**Pydantic** è una libreria che controlla dati ricevuti dall'esterno:

```python
from pydantic import BaseModel, Field

class Question(BaseModel):
    text: str = Field(min_length=3, max_length=2_000)
```

```python
question = Question(text="Come richiedo le ferie?")
```

Se il testo è troppo corto o lungo, Pydantic produce un errore dettagliato.

Perché non basta `text: str`? Le annotazioni di tipo aiutano il type checker, ma Python
non valida automaticamente un JSON ricevuto via rete. Pydantic esegue il controllo a
runtime, cioè mentre il programma gira.

## 10. Annotazioni di tipo

Le annotazioni descrivono valori attesi:

```python
def count_words(text: str) -> int:
    return len(text.split())
```

mypy può segnalare:

```python
count_words(42)
```

perché `42` è un intero e la funzione richiede una stringa.

Le annotazioni:

- documentano il codice;
- aiutano l'editor;
- permettono controlli prima dell'esecuzione;
- non sostituiscono la validazione di input esterni.

## 11. Dipendere da un comportamento, non da un provider

Un **Protocol** descrive quali metodi deve offrire un oggetto:

```python
from typing import Protocol

class Generator(Protocol):
    async def generate(self, question: str) -> str:
        ...
```

Il servizio non sa se la risposta arriva da una regola, da OpenAI o da un altro
provider. Richiede solo un oggetto con `generate`.

Questa tecnica è **dependency injection**: la dipendenza viene passata dall'esterno.
Non è magia; significa semplicemente:

```python
service = AnswerService(generator=RuleBasedGenerator())
```

Nei test potremo passare un fake prevedibile.

## 12. Sincrono e asincrono

### Sincrono

Nel codice **sincrono**, ogni operazione termina prima della successiva:

```text
chiama servizio A -> attendi -> chiama servizio B -> attendi
```

### Asincrono

Nel codice **asincrono**, mentre un'operazione aspetta rete o disco, Python può
proseguire con altro lavoro:

```text
avvia A -> A attende rete -> avvia B -> B attende -> riprendi A
```

`async def` definisce una coroutine:

```python
import asyncio

async def wait_and_answer() -> str:
    await asyncio.sleep(0.1)
    return "risposta"

print(asyncio.run(wait_and_answer()))
```

`await` sospende la coroutine fino al risultato senza bloccare l'intero event loop.
L'**event loop** è il coordinatore che riprende le coroutine pronte.

Async aiuta operazioni I/O, cioè attese verso rete, file o database. Non rende più
veloce un calcolo pesante sulla CPU.

## 13. Esempio completo

Il file `src\ai_mastery\python_service.py` contiene:

```python
from typing import Protocol

from pydantic import BaseModel, Field

class Question(BaseModel):
    text: str = Field(min_length=3, max_length=2_000)

class Generator(Protocol):
    async def generate(self, question: str) -> str:
        ...

class RuleBasedGenerator:
    async def generate(self, question: str) -> str:
        normalized = question.lower()
        if "ferie" in normalized:
            return "Consulta la procedura ferie."
        if "cedolino" in normalized:
            return "Consulta la procedura payroll."
        return "Non conosco ancora la risposta."

class AnswerService:
    def __init__(self, generator: Generator) -> None:
        self._generator = generator

    async def answer(self, question: Question) -> str:
        return await self._generator.generate(question.text)
```

Esegui:

```powershell
python -m ai_mastery.python_service "Come richiedo le ferie?"
```

Output:

```text
Consulta la procedura ferie.
```

Flusso:

1. il terminale passa il testo al programma;
2. Pydantic crea e valida `Question`;
3. `AnswerService` chiama il `Generator`;
4. `RuleBasedGenerator` applica la regola;
5. il risultato viene stampato.

## 14. Testare con un fake

Un **fake** è un'implementazione semplice usata nei test:

```python
class FakeGenerator:
    async def generate(self, question: str) -> str:
        return f"fake:{question}"
```

Test:

```python
import pytest

@pytest.mark.asyncio
async def test_service_uses_generator() -> None:
    service = AnswerService(FakeGenerator())

    result = await service.answer(Question(text="Domanda valida"))

    assert result == "fake:Domanda valida"
```

Il test non usa rete, non costa denaro e restituisce sempre lo stesso risultato.

## 15. Laboratorio guidato

### Passo 1

Esegui i tre input:

```powershell
python -m ai_mastery.python_service "Come richiedo le ferie?"
python -m ai_mastery.python_service "Dove trovo il cedolino?"
python -m ai_mastery.python_service "Ciao, chi sei?"
```

Controlla i tre rami della funzione.

### Passo 2

Aggiungi una regola per la parola `contratto`. Prima scrivi un test che fallisce:

```python
@pytest.mark.asyncio
async def test_contract_question() -> None:
    generator = RuleBasedGenerator()
    assert await generator.generate("Quando scade il contratto?") == (
        "Consulta la procedura contratti."
    )
```

Poi implementa la regola e verifica che il test passi.

### Passo 3

Prova:

```powershell
python -m ai_mastery.python_service "x"
```

Pydantic deve rifiutare la domanda troppo corta. Leggi l'errore: campo, regola violata
e valore ricevuto.

## 16. Esercizi

### Base

Scrivi `contains_sensitive_word(text: str) -> bool` che restituisce `True` per
`password` o `token`.

### Intermedio

Per questo esercizio sostituisci la classe `Answer(text, source)` della sezione 8 con
una nuova versione e modifica il generatore perché restituisca:

```python
Answer(text="...", category="leave")
```

invece di una stringa.

### Avanzato

Esegui tre domande contemporaneamente con `asyncio.gather`, mantenendo l'ordine.

## 17. Soluzioni

### Base

```python
def contains_sensitive_word(text: str) -> bool:
    normalized = text.lower()
    return "password" in normalized or "token" in normalized
```

### Intermedio

Questa definizione sostituisce, solo per l'esercizio, quella con il campo `source`
della sezione 8:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Answer:
    text: str
    category: str
```

Poi modifica il tipo di ritorno da `str` ad `Answer` nel Protocol e nelle
implementazioni. mypy aiuta a trovare tutti i punti da aggiornare.

### Avanzato

```python
import asyncio

async def main() -> None:
    service = AnswerService(RuleBasedGenerator())
    results = await asyncio.gather(
        service.answer(Question(text="Domanda ferie")),
        service.answer(Question(text="Domanda cedolino")),
        service.answer(Question(text="Domanda contratto")),
    )
    print(results)

asyncio.run(main())
```

`gather` restituisce i risultati nello stesso ordine degli argomenti.

## 18. Errori comuni

- **Scrivere tutto in una funzione:** rende difficile testare e sostituire parti.
- **Catturare ogni eccezione:** nasconde errori inattesi.
- **Usare async per calcolo CPU:** non porta parallelismo automatico.
- **Chiamare provider nei test unitari:** rende test lenti, costosi e instabili.
- **Confondere type hint e validazione:** servono a momenti diversi.
- **Creare il provider dentro il servizio:** rende la dipendenza difficile da cambiare.

## 19. Domande di autoverifica

**Che cosa fa una funzione?**  
Raggruppa un comportamento, riceve parametri e può restituire un risultato.

**Che differenza c'è fra lista e dizionario?**  
La lista usa posizioni ordinate; il dizionario usa chiavi.

**Quando useresti Pydantic?**  
Quando dati esterni devono rispettare campi, tipi e vincoli.

**Perché il servizio dipende da `Generator`?**  
Per separare la logica dal provider concreto e poter usare fake nei test.

**Che cosa significa `await`?**  
Sospende la coroutine finché l'operazione asincrona termina, lasciando lavorare
l'event loop.

## 20. Prossimo passo

Quando esempi e test sono chiari, leggi la [guida avanzata Python
production-grade](GUIDA.md). Lì troverai deadline, retry, idempotenza, concorrenza e
osservabilità.
