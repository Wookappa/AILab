# 02B - Deep Learning e Computer Vision

**Inizia da qui:** [classificazione di immagini passo-passo](LEZIONE.md).

**Dopo la lezione:** [approfondimento production-grade](GUIDA.md).

## Obiettivo

Creare un classificatore di immagini reale, capire CNN e transfer learning e sapere
quali componenti servono per portarlo in produzione.

## Deliverable

- esempio `vision_basics.py` eseguito;
- confronto con baseline;
- matrice di confusione e analisi di almeno cinque errori;
- tabella di due esperimenti controllati;
- disegno della pipeline di serving;
- opzionale: CNN Fashion-MNIST con PyTorch.

## Checklist finale

- [ ] So spiegare pixel, canale, tensore, batch ed epoca.
- [ ] Distinguo training, inference e transfer learning.
- [ ] Ho usato split indipendenti e so descrivere il leakage per soggetto.
- [ ] Confronto accuracy e metriche per classe con una baseline.
- [ ] Analizzo immagini sbagliate, non soltanto metriche aggregate.
- [ ] Applico augmentation solo al training.
- [ ] Versiono pesi, preprocessing, label map e soglie.
- [ ] Gestisco file corrotti, dimensioni e formati come input non fidati.
- [ ] So motivare CPU, GPU e batching con misure.
- [ ] Ho una strategia per drift, revisione e rollback.

## Domande da colloquio

1. Perché una CNN funziona meglio di un MLP su immagini grandi?
2. Come eviti leakage se hai più foto dello stesso soggetto?
3. Quando useresti transfer learning?
4. Come valuti un classificatore con classi rare?
5. Che cosa deve contenere l'artefatto oltre ai pesi?
6. Come monitori il modello se le label arrivano dopo settimane?
