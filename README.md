# Webcam Filtri

Applicazione in tempo reale che legge il feed della webcam e applica filtri visivi, effetti e accessori AR sul volto. Supporta screenshot, registrazione video e modalità automatica di scorrimento filtri.

---

## Requisiti

| Componente | Versione / Dettaglio |
|---|---|
| Sistema operativo | Linux, macOS, Windows, Raspberry Pi OS (64-bit consigliato) |
| Python | 3.9 o superiore |
| Webcam | USB o integrata |
| RAM | 512 MB minimi (1 GB consigliato su Raspberry Pi) |

---

## Installazione

**1. Clona il repository**

```bash
git clone https://github.com/tuo-utente/webcam-filtri.git
cd webcam-filtri
```

**2. Rendi eseguibile lo script di avvio**

```bash
chmod +x run.sh
```

Questo è tutto. Lo script crea automaticamente l'ambiente virtuale e installa le dipendenze al primo avvio.

---

## Come avviare

```bash
./run.sh
```

Al primo avvio l'installazione delle dipendenze richiede qualche minuto. Dai successivi si parte subito.

---

## Tasti disponibili

### Filtri colore (selezionano la modalità attiva)

| Tasto | Filtro |
|---|---|
| `0` | Normale |
| `1` | Bianco e Nero |
| `2` | Negativo |
| `3` | Termico |
| `4` | Seppia |
| `5` | Blur Soft |
| `6` | Blur Forte |
| `7` | Cartoon |
| `8` | Pixelato |
| `9` | Gilberto |

### Effetti toggle (on/off)

| Tasto | Effetto |
|---|---|
| `M` | Rilevamento movimento |
| `N` | Effetto fantasma (scia) |
| `F` | Sfondo sfocato |
| `V` | Vignettatura |
| `Z` | Motion blur |
| `A` | Modalità automatica (cambia filtro ogni 3 s) |

### Accessori AR

| Tasto | Accessorio |
|---|---|
| `G` | Occhiali |
| `H` | Cappello |
| `B` | Barba |
| `X` | Specchio |

### Azioni

| Tasto | Azione |
|---|---|
| `S` | Salva screenshot (cartella `screenshots/`) |
| `R` | Avvia / ferma la registrazione video (cartella `videos/`) |
| `Q` | Esci dall'applicazione |

---

## Struttura del progetto

```
webcam-filtri/
├── main.py          # loop principale
├── effects.py       # rilevamento volti, accessori AR, motion/ghost
├── filters.py       # filtri colore e visivi
├── ui.py            # HUD, barra filtri, footer
├── run.sh           # script di avvio
├── requirements.txt # dipendenze Python
├── assets/          # PNG degli accessori (hat, glasses, beard, gilberto)
├── screenshots/     # screenshot salvati automaticamente
└── videos/          # video registrati automaticamente
```

### Accessori personalizzati

Inserisci nella cartella `assets/` i seguenti file PNG (con trasparenza):

| File | Uso |
|---|---|
| `hat.png` | Cappello |
| `glasses.png` | Occhiali |
| `beard.png` | Barba |
| `gilberto.png` | Filtro Gilberto (modalità 9) |

Se un file manca, l'accessorio corrispondente viene semplicemente ignorato.

---

## Note per Raspberry Pi

**Modello consigliato:** Raspberry Pi 4 (2 GB RAM o più). Il Pi 3 funziona ma con FPS ridotti.

**Webcam:** collega la webcam USB prima di avviare l'app. Per verificare che sia riconosciuta:

```bash
ls /dev/video*
```

Deve comparire almeno `/dev/video0`.

**Prestazioni:** su Raspberry Pi i filtri più pesanti (Cartoon, Blur Forte) abbassano gli FPS. Per migliorare le prestazioni, abbassa la risoluzione della webcam modificando `main.py` dopo `cap = cv2.VideoCapture(0)`:

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

**Display:** se usi il Pi in modalità headless (senza monitor), l'app non può aprire la finestra. Serve un display fisico o una sessione VNC/X11 forwarding attiva.

**Prima installazione lenta:** la compilazione di OpenCV su Pi può richiedere fino a 10 minuti. È normale.