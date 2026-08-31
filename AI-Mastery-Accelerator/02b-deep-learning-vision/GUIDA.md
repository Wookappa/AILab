# Guida production-grade: Deep Learning e Computer Vision

## 1. Dalla baseline alla rete neurale

Non iniziare da una CNN perché “le immagini richiedono deep learning”. Definisci:

- unità di previsione;
- classi e casi fuori dominio;
- costo dei falsi positivi e negativi;
- split coerente con l'uso futuro;
- baseline non-AI e modello semplice;
- latenza, memoria, privacy e volume.

Un modello lineare sui pixel o su feature note può essere sufficiente e rende
visibili problemi nei dati prima di investire in GPU.

## 2. Convoluzione in modo operativo

Un kernel `3 x 3` scorre sull'immagine e produce una feature map. I parametri del
kernel vengono condivisi in tutte le posizioni.

```text
input HxW
 -> Conv2d
 -> BatchNorm opzionale
 -> ReLU
 -> pooling o stride
 -> feature map più piccola
```

Parametri importanti:

- `kernel_size`: area osservata;
- `stride`: passo dello spostamento;
- `padding`: bordo aggiunto;
- `channels`: numero di feature map;
- `receptive field`: porzione dell'immagine che influenza un'attivazione.

Reti più profonde costruiscono feature più astratte, ma aumentano costo e rischio di
overfitting.

## 3. Loss, probabilità e class imbalance

Per classificazione multiclasse si usa spesso cross-entropy sui logit. Non applicare
softmax prima di `CrossEntropyLoss`: la loss lo gestisce in modo numericamente
stabile.

Con classi sbilanciate valuta:

- precision, recall e F1 per classe;
- macro-F1;
- matrice di confusione;
- PR curve per problemi binari rari;
- costi specifici degli errori.

Puoi usare pesi di classe, sampling o raccolta dati mirata. Non alterare il test per
farlo sembrare bilanciato se la produzione non lo sarà.

## 4. Esperimenti riproducibili

Versiona insieme:

```text
codice + split + label map + trasformazioni + pesi iniziali
+ seed + optimizer + learning rate + checkpoint + metriche
```

Un esperimento confrontabile cambia una variabile principale. Registra almeno:

- loss train/validation per epoca;
- metriche per classe;
- tempo e risorse;
- commit e configurazione;
- esempi di errore;
- criterio con cui scegli il checkpoint.

**Early stopping** interrompe quando la metrica validation non migliora. Il test non
decide quando fermarsi.

## 5. Transfer learning con ResNet

Con Torchvision i pesi pubblicano anche il preprocessing corretto:

```python
from torch import nn
from torchvision.models import ResNet18_Weights, resnet18

weights = ResNet18_Weights.DEFAULT
model = resnet18(weights=weights)
for parameter in model.parameters():
    parameter.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, number_of_classes)
preprocess = weights.transforms()
```

Prima addestra solo `model.fc`. Se la validation si stabilizza e il dominio è
abbastanza diverso, sblocca gradualmente gli ultimi blocchi con learning rate più
basso.

`requires_grad=False` blocca i pesi ma non impedisce a BatchNorm di aggiornare le
statistiche quando l'intero modello è in modalità training. Durante la prima fase
mantieni il backbone in `eval()` e la nuova testa in `train()`; se il ciclo chiama
`model.train()`, ripristina esplicitamente i layer BatchNorm congelati in `eval()`.

Un dataset organizzato in cartelle si collega al preprocessing dei pesi così:

```python
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

train_dataset = ImageFolder("data/train", transform=preprocess)
train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True,
    num_workers=0,
)
```

Evita di calcolare statistiche di normalizzazione usando validation o test.

## 6. Dataset reale e annotazione

Un dataset utile documenta:

- fonte e licenza;
- consenso e dati personali;
- definizione delle classi;
- istruzioni agli annotatori;
- disaccordo e adjudication;
- duplicati;
- distribuzione per gruppo, dispositivo, sede e tempo;
- esempi esclusi e motivo.

Controlla shortcut learning: il modello può riconoscere sfondo, watermark o
dispositivo invece dell'oggetto.

Per medicale, biometrico o altri domini ad alto impatto servono competenze di dominio,
governance e conformità ulteriori. Un buon benchmark tecnico non autorizza l'uso.

## 7. Robustezza

Valuta segmenti realistici:

- luce e contrasto;
- sfocatura e compressione;
- rotazione e scala;
- dispositivi differenti;
- occlusioni;
- classi rare;
- immagini fuori dominio.

Le augmentation devono rappresentare variazioni ammissibili, non nascondere
insufficienze del dataset.

La calibrazione misura se probabilità dichiarate e frequenze empiriche coincidono.
Per l'astensione scegli una soglia su validation e misura coverage contro qualità.

## 8. Serving

Opzioni comuni:

- PyTorch nativo per flessibilità;
- TorchScript o `torch.compile` secondo ambiente e versione;
- ONNX Runtime per portabilità;
- servizio gestito quando riduce davvero il carico operativo.

Misura sul target reale, non soltanto sul laptop:

```text
decode + preprocessing + coda + inference + postprocessing
```

Il batching migliora throughput ma può aumentare latenza. GPU non significa
automaticamente più veloce per singole immagini o modelli piccoli.

Un endpoint deve rifiutare:

- file troppo grandi;
- formati non ammessi;
- immagini corrotte;
- dimensioni decompressive anomale;
- batch oltre il limite.

Usa decoder aggiornati e tratta gli upload come input non fidato.

## 9. Packaging del modello

Un artefatto distribuibile include o referencia in modo immutabile:

- architettura;
- pesi;
- label map;
- preprocessing;
- soglie;
- versione framework;
- metadati di training;
- eval report.

All'avvio verifica compatibilità e checksum. Una risposta deve includere la versione
del modello nei metadati tecnici o nel trace, non necessariamente nell'interfaccia
utente.

## 10. Monitoring e drift

Senza label immediate puoi monitorare:

- frequenza delle classi predette;
- distribuzione di confidence;
- astensioni;
- proprietà tecniche delle immagini;
- errori di decoding;
- latenza, coda, memoria e GPU;
- distanza delle feature rispetto al training.

Questi segnali non provano un calo di accuracy. Quando arrivano label affidabili,
calcola metriche ritardate per classe e segmento.

Definisci prima:

- soglia di allarme;
- responsabile;
- azione;
- rollback;
- processo di raccolta e revisione dei casi.

## 11. Checklist di design

Prima del deploy sai rispondere:

1. Quale decisione supporta il modello?
2. Qual è la baseline?
3. Lo split impedisce leakage per soggetto o gruppo?
4. Quali classi e casi fuori dominio esistono?
5. Come sono stati controllati label e duplicati?
6. Quali metriche contano per classe?
7. Preprocessing e label map sono versionati?
8. Quali input vengono rifiutati?
9. CPU o GPU è motivata da benchmark?
10. Come rilevi regressione e fai rollback?

## 12. Criterio di padronanza

Non sei pronto perché sai definire una CNN. Sei pronto quando puoi:

- costruire una baseline;
- addestrare e confrontare modelli senza contaminare il test;
- spiegare gli errori con esempi;
- scegliere consapevolmente transfer learning;
- rendere riproducibile il training;
- servire input non fidati in modo controllato;
- monitorare qualità e operatività;
- dichiarare limiti e condizioni di non utilizzo.
