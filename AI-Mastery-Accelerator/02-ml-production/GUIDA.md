# Guida completa: machine learning end-to-end

## 1. Lessico fondamentale

- **Machine learning supervisionato:** apprende una funzione da esempi con risposta
  nota.
- **Osservazione o sample:** una riga del dataset.
- **Feature (`X`):** informazione disponibile al momento della previsione.
- **Target o label (`y`):** valore da prevedere.
- **Training:** stima dei parametri del modello sui dati.
- **Inference:** uso del modello addestrato su nuovi input.
- **Iperparametro:** scelta esterna al training, come profondità di un albero.
- **Generalizzazione:** capacità di funzionare su dati non visti.

Esempio churn: una riga rappresenta un cliente a una data; le feature descrivono ciò
che era noto allora; il target indica se ha abbandonato nei successivi 30 giorni.

La definizione temporale evita di usare informazioni future per predire il passato.

## 2. Formulare correttamente il problema

Prima di scegliere il modello:

1. qual è l'unità di previsione?
2. quando viene prodotta la previsione?
3. qual è l'orizzonte temporale?
4. quale azione segue la previsione?
5. quando diventa disponibile la label?
6. quanto costa ogni tipo di errore?

Una metrica tecnica è utile solo se rappresenta l'azione. Se il team può contattare
100 clienti, serve ordinare bene i 100 casi, non massimizzare genericamente accuracy.

## 3. Split: train, validation e test

- **train set:** dati usati per stimare parametri;
- **validation set:** dati usati per scegliere modello, feature e threshold;
- **test set:** stima finale su dati non usati nelle decisioni.

### Quale split scegliere

| Situazione | Split |
|---|---|
| righe indipendenti senza ordine | casuale stratificato |
| previsione del futuro | temporale |
| più righe per cliente/paziente | per gruppo |
| pochi dati | cross-validation compatibile col dominio |

**Stratificato** significa mantenere approssimativamente la proporzione delle classi.
**Cross-validation** ripete train/validation su più suddivisioni e aggrega i risultati.

### Leakage

Il **data leakage** avviene quando il training usa informazione non disponibile al
momento reale della previsione. Produce metriche offline irrealistiche.

Esempi:

- feature `cancellation_reason` per predire cancellazione;
- scaler adattato su train e test insieme;
- stesso cliente in train e test;
- aggregazione che include eventi successivi alla prediction time;
- selezione feature guardando il test.

Checklist per ogni feature:

```text
Da quale evento deriva?
Quando viene scritta?
Può essere corretta retroattivamente?
Era disponibile entro la prediction time?
La trasformazione è fittata solo sul train?
```

## 4. Classificazione e matrice di confusione

Per una classe positiva:

| | Predetto positivo | Predetto negativo |
|---|---:|---:|
| Reale positivo | TP, vero positivo | FN, falso negativo |
| Reale negativo | FP, falso positivo | TN, vero negativo |

- `precision = TP / (TP + FP)`: quante predizioni positive sono corrette;
- `recall = TP / (TP + FN)`: quanti positivi reali trovi;
- `specificity = TN / (TN + FP)`: quanti negativi riconosci;
- `F1`: media armonica di precision e recall;
- `accuracy = (TP + TN) / totale`.

Con 1% di frodi, predire sempre "non frode" dà 99% accuracy ma zero recall.

### ROC-AUC e PR-AUC

Una curva valuta tutti i threshold:

- **ROC-AUC:** confronto fra true-positive rate e false-positive rate; può apparire
  ottimistica con classi molto sbilanciate.
- **PR-AUC:** area sotto precision-recall; evidenzia la qualità sulla classe positiva.

Non sostituiscono il threshold operativo, che va scelto in base a capacità e costi.

### Metriche probabilistiche

- **log-loss:** penalizza fortemente probabilità molto sicure ma sbagliate;
- **Brier score:** media di `(probabilità - label)²`, utile anche per calibrazione;
- **MAP (Mean Average Precision):** metrica di ranking che media la precisione alle
  posizioni rilevanti su più query.

Non scegliere una metrica per abitudine: collega score, decisione e costo.

## 5. Regressione

- **MAE (Mean Absolute Error):** media di `|y - prediction|`; interpretabile nelle
  unità del target e meno sensibile agli outlier.
- **RMSE (Root Mean Squared Error):** penalizza maggiormente errori grandi.
- **R²:** quota di varianza spiegata rispetto alla media; non misura da solo utilità.

Osserva anche distribuzione degli errori, bias per segmento e quantili. Due modelli con
stesso MAE possono avere rischi molto diversi.

## 6. Probabilità, calibrazione e threshold

Un classificatore è **calibrato** se, tra i casi stimati al 70%, circa il 70% è
positivo. Ranking buono e calibrazione buona sono proprietà diverse.

Scegli il threshold minimizzando un costo definito:

```python
import numpy as np

def choose_threshold(
    probabilities: np.ndarray,
    labels: np.ndarray,
    *,
    false_negative_cost: float,
    false_positive_cost: float,
) -> tuple[float, float]:
    best_threshold, best_cost = 0.5, float("inf")
    for threshold in np.linspace(0, 1, 201):
        predicted = probabilities >= threshold
        false_negatives = np.sum((labels == 1) & ~predicted)
        false_positives = np.sum((labels == 0) & predicted)
        cost = (
            false_negative_cost * false_negatives
            + false_positive_cost * false_positives
        )
        if cost < best_cost:
            best_threshold, best_cost = float(threshold), float(cost)
    return best_threshold, best_cost
```

Scegli il threshold sulla validation, poi misura una volta sul test. Se costi o
prevalenza cambiano, il threshold va rivalutato.

## 7. Preprocessing senza skew

Una `Pipeline` di scikit-learn applica la stessa sequenza in train e inference:

```python
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

numeric = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
])
categorical = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("encode", OneHotEncoder(handle_unknown="ignore")),
])
features = ColumnTransformer([
    ("numeric", numeric, ["age", "monthly_amount"]),
    ("categorical", categorical, ["country", "plan"]),
])
pipeline = Pipeline([
    ("features", features),
    ("model", LogisticRegression(class_weight="balanced", max_iter=1_000)),
])
```

**Training-serving skew** significa che trasformazioni o dati differiscono fra
training e produzione. Serializzare l'intera pipeline riduce il rischio.

`class_weight="balanced"` modifica il peso degli errori delle classi e può rendere le
probabilità non calibrate. Se servono probabilità affidabili, misura la calibrazione
su dati held-out e usa `CalibratedClassifierCV`, oppure evita i pesi e incorpora il
costo operativo nella scelta del threshold. Non calibrare sul test finale.

## 8. Baseline, bias e varianza

Parti da una regola e da un modello semplice:

- se nemmeno il modello complesso supera la regola, indaga dati e metrica;
- un modello semplice spiega quali feature portano segnale;
- il confronto quantifica il valore della complessità.

**Underfitting**: modello troppo semplice, errore alto anche sul train.
**Overfitting**: errore train basso, validation molto peggiore.

Interventi:

- underfitting: feature migliori, capacità maggiore, meno regolarizzazione;
- overfitting: più dati, regolarizzazione, modello più semplice, early stopping;
- entrambi: controlla prima qualità dati, label e leakage.

## 9. Tuning corretto

Il tuning cerca iperparametri. Non usare il test durante la ricerca.

1. definisci spazio di ricerca ragionevole;
2. usa cross-validation coerente con tempo/gruppi;
3. scegli metrica primaria e guardrail;
4. registra ogni run;
5. confronta varianza, non solo miglior valore;
6. ritesta il candidato sul test bloccato.

La random search esplora spesso meglio di una griglia quando pochi iperparametri
contano. Il tuning bayesiano usa risultati precedenti per scegliere nuove prove.
L'**early stopping** interrompe il training quando la validation non migliora.

## 10. Riproducibilità e registry

Per ogni modello conserva:

- commit e versione ambiente;
- snapshot/query dei dati;
- schema e feature version;
- split e seed;
- iperparametri;
- metriche globali e per segmento;
- threshold e calibrazione;
- artefatto firmato/checksum;
- stato: candidate, staging, production, archived.

Un **model registry** cataloga versioni e promozioni. Non è solo storage del file.

### Tracking concreto con MLflow

Per il laboratorio installa `pip install -e ".[mlops]"`:

```python
import mlflow
import mlflow.sklearn

with mlflow.start_run(run_name="logistic-baseline"):
    mlflow.log_params({
        "split": "temporal",
        "train_end": "2026-05-31",
        "model": "logistic_regression",
    })
    pipeline.fit(train_x, train_y)
    mlflow.log_metrics({
        "validation_pr_auc": float(validation_pr_auc),
        "validation_cost": float(validation_cost),
    })
    mlflow.sklearn.log_model(pipeline, name="model")
    mlflow.log_artifact("reports/error_analysis.json")
```

MLflow salva run, parametri, metriche e artifact. In un progetto piccolo è accettabile
anche `runs.jsonl` più cartelle con checksum, purché schema e scrittura siano
deterministici. Il registry promuove un artefatto già valutato; non rilancia il
training implicitamente.

## 11. Deploy e monitoring

Modalità:

- **batch:** previsioni periodiche su molte righe;
- **online:** risposta sincrona per richiesta;
- **streaming:** previsione continua su eventi;
- **embedded:** modello distribuito dentro applicazione/device.

Monitora:

- schema, null e range;
- distribuzione feature e prediction;
- latenza, errori e risorse;
- performance quando arrivano label ritardate;
- segmenti e fairness dove rilevante.

**Data drift:** cambia `P(X)`, la distribuzione degli input.
**Label drift:** cambia `P(y)`.
**Concept drift:** cambia la relazione `P(y|X)`.

Il drift non implica automaticamente degrado; genera un'indagine, non sempre retrain.

### Quantificare data drift

Il **PSI (Population Stability Index)** divide una feature in bin e confronta le quote
reference/correnti:

```text
PSI = sum((current_i - reference_i) * ln(current_i / reference_i))
```

La **Jensen-Shannon divergence** confronta due distribuzioni tramite la loro media ed
è simmetrica e limitata. Entrambe dipendono da binning e campione. Non usare soglie
copiate come verità universali: costruisci una baseline su periodi stabili, misura
varianza e collega l'alert a performance e segmento.

## 12. Laboratorio guidato

Costruisci un modello churn:

1. definisci prediction time e orizzonte;
2. crea split temporale e blocca il test;
3. misura baseline;
4. crea pipeline di preprocessing;
5. confronta regressione logistica e gradient boosting;
6. calibra se necessario;
7. scegli threshold su costo;
8. misura segmenti e intervalli bootstrap;
9. salva pipeline, metadata e model card;
10. esponi batch CLI e endpoint;
11. simula drift e rollback.

## 13. Soluzione di riferimento

Il lavoro è completo se sai mostrare:

- nessuna feature futura;
- fit delle trasformazioni solo sul train;
- stessa pipeline in inference;
- test set usato dopo le decisioni;
- threshold motivato dall'azione;
- metriche con baseline e segmenti;
- gestione categorie nuove e valori mancanti;
- versione del modello restituita dall'API;
- monitor che distingue drift da performance;
- strategia di rollback.

**Domanda finale:** se PR-AUC sale ma il costo operativo peggiora, il nuovo modello non
è migliore per il prodotto. Verifica threshold, calibrazione e costo per errore.
