# Lezione passo-passo: il primo sistema di machine learning

## Cosa saprai fare alla fine

Saprai:

1. spiegare che cosa sono machine learning, modello, feature e label;
2. dividere dati in training e test;
3. costruire una baseline;
4. addestrare un classificatore;
5. leggere accuracy, precision e recall;
6. riconoscere leakage e overfitting;
7. usare una pipeline per evitare differenze fra training e produzione;
8. salvare e riutilizzare un modello.

## Cosa devi sapere prima

Completa [Python passo-passo](../01-python-production/LEZIONE.md). Devi conoscere
variabili, liste, dizionari, funzioni e test.

## 1. Il problema

Immagina di voler individuare clienti a rischio di abbandono, chiamato **churn**.
Per ogni cliente conosci:

- da quanti mesi usa il prodotto;
- importo mensile;
- numero di ticket di supporto;
- paese;
- se ha abbandonato nei 30 giorni successivi.

Vogliamo usare clienti passati per stimare il rischio di un nuovo cliente.

## 2. AI, machine learning e modello

**Intelligenza artificiale (AI)** è un nome ampio per sistemi che svolgono compiti
associati all'intelligenza: comprendere testo, riconoscere immagini, pianificare.

**Machine learning (ML)** è un modo di costruire alcuni sistemi AI: invece di scrivere
manualmente ogni regola, mostriamo esempi a un algoritmo.

Una regola manuale:

```python
if support_tickets > 5:
    risk = "high"
```

Un modello ML impara dai dati quanto contano ticket, anzianità, importo e paese.

Un **modello** è una funzione con parametri appresi. Riceve input e produce uno score o
una previsione.

```text
feature del cliente -> modello -> probabilità di churn
```

## 3. Dataset, righe e colonne

Un **dataset** è una collezione organizzata di esempi.

| customer_id | tenure_months | monthly_amount | support_tickets | country | churned |
|---|---:|---:|---:|---|---:|
| c-001 | 2 | 49 | 6 | IT | 1 |
| c-002 | 30 | 39 | 0 | IT | 0 |
| c-003 | 5 | 99 | 4 | FR | 1 |

- una riga è un'**osservazione** o **sample**;
- una colonna usata per prevedere è una **feature**;
- il valore da prevedere è **target** o **label**;
- `1` significa churn; `0` significa non churn.

Il modello deve ricevere solo informazioni disponibili nel momento in cui effettuiamo
la previsione.

## 4. Training e inference

**Training**, o addestramento, è la fase in cui l'algoritmo osserva esempi e modifica i
parametri per ridurre gli errori.

**Inference** è la fase in cui usiamo il modello già addestrato su nuovi dati.

Analogia:

- training: studiare esercizi con soluzione;
- inference: risolvere un esercizio nuovo;
- test: verificare la risposta senza aver visto prima quell'esercizio.

Un modello che ricorda soltanto gli esempi di training non è utile. Deve
**generalizzare**, cioè funzionare su casi nuovi ma simili al problema reale.

## 5. Perché dividere i dati

Se addestriamo e valutiamo sugli stessi clienti, il risultato è troppo ottimistico.
Dividiamo:

- **training set:** usato per imparare;
- **validation set:** usato per scegliere modello e impostazioni;
- **test set:** usato alla fine per una stima indipendente.

Nel primo esempio useremo solo train/test per semplicità. Nel progetto reale
aggiungeremo validation.

```python
from sklearn.model_selection import train_test_split

train_x, test_x, train_y, test_y = train_test_split(
    features,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels,
)
```

- `test_size=0.25`: 25% degli esempi finisce nel test;
- `random_state=42`: rende la divisione ripetibile;
- `stratify=labels`: conserva proporzioni simili di churn nei due gruppi.

Con dati temporali non useremo una divisione casuale: addestreremo sul passato e
testeremo sul futuro.

## 6. Baseline

Una **baseline** è una soluzione semplice da battere.

Se il 70% dei clienti non abbandona, predire sempre "non churn" ottiene 70% accuracy.
Un modello complesso con 69% non aggiunge valore.

```python
majority_prediction = train_y.mode()[0]
baseline_predictions = [majority_prediction] * len(test_y)
```

La baseline non deve essere stupida: rappresenta il minimo realistico disponibile.

## 7. Il primo modello

Useremo la **regressione logistica**, un modello di classificazione. Nonostante il nome
"regressione", produce una probabilità fra 0 e 1 per una classe.

In forma intuitiva:

```text
somma pesata delle feature -> trasformazione -> probabilità
```

Ogni peso indica quanto una feature spinge lo score verso churn o non churn. La
relazione appresa è relativamente semplice, perciò è una buona baseline ML.

## 8. Preparare dati diversi

Le feature numeriche e testuali richiedono trasformazioni diverse.

### Feature numeriche

`tenure_months` e `monthly_amount` sono numeri. Possiamo:

- riempire valori mancanti con la mediana;
- standardizzare, cioè portare scale diverse a un ordine confrontabile.

### Feature categoriche

`country` contiene categorie. Il modello matematico richiede numeri, quindi usiamo
**one-hot encoding**:

```text
country=IT -> country_IT=1, country_FR=0
country=FR -> country_IT=0, country_FR=1
```

Una **pipeline** lega trasformazioni e modello in un unico oggetto. Così training e
inference eseguono gli stessi passaggi.

## 9. Programma completo

Il file `examples\ml_basics.py`:

1. genera dati sintetici, cioè inventati per il laboratorio;
2. crea train e test;
3. addestra baseline e modello;
4. stampa metriche;
5. prova un nuovo cliente.

Esegui dalla cartella `AI-Mastery-Accelerator`:

```powershell
python examples\ml_basics.py
```

Output simile:

```text
Baseline accuracy: 0.69
Model accuracy:    0.80
Model precision:   0.65
Model recall:      0.74
New customer churn probability: 0.99
```

I valori possono cambiare leggermente fra versioni. Non devi ottenere un numero
"magico": devi capire come viene calcolato.

## 10. Matrice di confusione

Per una classe positiva, come churn:

| Caso | Significato |
|---|---|
| vero positivo (TP) | prevedi churn e il cliente abbandona |
| falso positivo (FP) | prevedi churn ma il cliente resta |
| falso negativo (FN) | prevedi non churn ma il cliente abbandona |
| vero negativo (TN) | prevedi non churn e il cliente resta |

### Accuracy

```text
(TP + TN) / tutti i casi
```

Quota totale di previsioni corrette. Può ingannare quando una classe è rara.

### Precision

```text
TP / (TP + FP)
```

Fra i clienti segnalati a rischio, quanti abbandonano davvero?

### Recall

```text
TP / (TP + FN)
```

Fra tutti quelli che abbandonano, quanti ne troviamo?

Se contattare un cliente costa molto, precision può essere importante. Se perdere un
cliente è molto costoso, potresti privilegiare recall. La scelta dipende dall'azione.

## 11. Probabilità e threshold

Il modello produce una probabilità, per esempio `0.73`. Per trasformarla in sì/no
serve una soglia, chiamata **threshold**:

```python
prediction = probability >= 0.5
```

Abbassare la soglia trova più positivi ma aumenta i falsi allarmi. Non usare 0.5 per
abitudine: scegli la soglia sui dati di validation in base al costo degli errori e
alla capacità del team di agire.

Esempio:

```text
costo falso negativo = 5
costo falso positivo = 1
costo totale = 5 * FN + 1 * FP
```

## 12. Leakage

Il **data leakage** avviene quando il training usa informazione che nella realtà non
sarebbe disponibile al momento della previsione.

Esempio sbagliato:

```text
feature: cancellation_reason
target: il cliente abbandonerà?
```

Il motivo di cancellazione esiste solo dopo l'abbandono. Il modello sembra bravissimo
nel test, ma non può funzionare prima dell'evento.

Altri leakage:

- lo stesso cliente in train e test;
- normalizzazione calcolata su tutto il dataset;
- statistiche che includono eventi futuri;
- uso ripetuto del test per scegliere il modello.

## 13. Overfitting e underfitting

**Overfitting**: il modello impara dettagli del train che non si ripetono. Risultato:
train molto buono, test peggiore.

**Underfitting**: il modello è troppo semplice o i dati non contengono segnale.
Risultato: prestazioni scarse anche sul train.

Prima di aumentare complessità:

1. controlla label;
2. cerca leakage;
3. confronta train/test;
4. analizza errori;
5. migliora dati e feature.

Il tuning non ripara dati sbagliati.

## 14. Salvare il modello

Dopo il training puoi serializzare l'intera pipeline:

```python
import joblib

joblib.dump(pipeline, "model.joblib")
loaded_pipeline = joblib.load("model.joblib")
```

Il file è un **artifact**, cioè un output versionato del processo. Non caricare artifact
non fidati con `joblib`: la deserializzazione può eseguire codice.

Insieme al modello conserva:

- versione del codice;
- dati o snapshot;
- feature;
- metriche;
- threshold;
- librerie;
- data di training.

## 15. Dal notebook alla produzione

Un notebook permette esperimenti interattivi. In produzione servono:

```text
comando di training ripetibile
-> artifact versionato
-> servizio o batch di inference
-> monitoraggio
-> rollback
```

Problemi da osservare:

- input con colonne mancanti;
- categorie mai viste;
- valori fuori intervallo;
- latenza alta;
- distribuzione dati cambiata;
- performance peggiorata quando arrivano nuove label.

## 16. Laboratorio guidato

### Passo 1: esegui e leggi

Esegui `python examples\ml_basics.py`. Trova nel file:

- dove nasce la label;
- dove avviene lo split;
- dove viene creata la pipeline;
- dove viene chiamato `fit`;
- dove viene chiamato `predict`.

### Passo 2: cambia una sola cosa

Cambia `test_size` da `0.25` a `0.40`. Riesegui.

Domanda: le metriche cambiano perché il modello è diverso o perché stai misurando su
un campione diverso? Risposta: entrambe le cose possono cambiare, perché cambia anche
il train. Per confronti seri fissa split e seed.

### Passo 3: crea leakage intenzionale

Aggiungi una feature uguale alla label e osserva l'accuracy. Poi rimuovila. Questo
esperimento mostra perché metriche eccezionali devono generare domande, non entusiasmo
automatico.

### Passo 4: analizza errori

Dentro `main()`, subito dopo `predictions = pipeline.predict(test_x)`, stampa cinque
righe sbagliate:

```python
errors = test_x.copy()
errors["actual"] = test_y
errors["predicted"] = predictions
print(errors[errors["actual"] != errors["predicted"]].head())
```

Cerca caratteristiche comuni. L'**error analysis** raggruppa errori per capirne la
causa.

## 17. Esercizi

### Base

Calcola quanti positivi e negativi sono presenti nel dataset.

### Intermedio

Stampa la matrice di confusione con `confusion_matrix`.

### Avanzato

Prova threshold `0.3`, `0.5` e `0.7`. Per ciascuno calcola precision, recall e
`5 * FN + FP`.

## 18. Soluzioni

### Base

```python
print(labels.value_counts())
```

### Intermedio

```python
from sklearn.metrics import confusion_matrix

print(confusion_matrix(test_y, predictions))
```

L'ordine standard binario è:

```text
[[TN, FP],
 [FN, TP]]
```

### Avanzato

Inserisci questo codice dentro `main()`, dopo aver creato `pipeline`, `test_x`,
`test_y` e `predictions`:

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score

probabilities = pipeline.predict_proba(test_x)[:, 1]
for threshold in [0.3, 0.5, 0.7]:
    predicted = probabilities >= threshold
    tn, fp, fn, tp = confusion_matrix(test_y, predicted).ravel()
    print(
        threshold,
        precision_score(test_y, predicted),
        recall_score(test_y, predicted),
        5 * fn + fp,
    )
```

Scegli la soglia su validation, non sul test finale.

## 19. Errori comuni

- Valutare sugli stessi dati usati per il training.
- Usare accuracy con classi molto sbilanciate.
- Fare preprocessing prima dello split.
- Cambiare molte variabili nello stesso esperimento.
- Considerare probabilità come certezze.
- Salvare soltanto il modello e dimenticare preprocessing/versioni.
- Fare retraining automatico a ogni drift senza verificare performance.

## 20. Domande di autoverifica

**Che differenza c'è fra feature e label?**  
Le feature sono input disponibili; la label è ciò che il modello deve prevedere.

**Perché serve un test set?**  
Per misurare su dati non usati nelle decisioni di training.

**Che cosa deve battere il modello?**  
Una baseline coerente con il problema.

**Precision e recall sono sempre entrambe massime?**  
No. Cambiando threshold spesso una sale e l'altra scende.

**Che cos'è leakage?**  
Informazione indebita o futura che rende la valutazione irrealistica.

**Che cosa va distribuito in produzione?**  
La stessa pipeline di trasformazione e modello, con schema e versione.

## 21. Prossimo passo

Ora puoi leggere la [guida avanzata ML end-to-end](GUIDA.md), che approfondisce
cross-validation, calibrazione, tuning, MLflow, drift e model registry.
