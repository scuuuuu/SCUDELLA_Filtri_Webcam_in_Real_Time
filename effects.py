#effects.py
#contiene gli effetti che usano il rilevamento facce
#o che confrontano frame consecutivi (ghost, motion).
#
#ogni funzione:
#  riceve il frame come primo parametro
#  restituisce il frame modificato
#  non modifica l'originale, lavora su una copia
#  ha un commento in cima che spiega cosa fa

import cv2
import numpy as np
import os


# --------------------------------------------------------------------------
#caricamento classificatori e immagini degli accessori
# --------------------------------------------------------------------------

#classificatore per rilevare i volti frontali
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

#classificatore per rilevare gli occhi
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

#cartella dove si trovano i png degli accessori
ASSETS_DIR = "assets"


def _load_asset(nome_file):
    #carica un png dalla cartella assets mantenendo il canale trasparenza (alpha).
    #restituisce none se il file non esiste, senza bloccare il programma.

    percorso = os.path.join(ASSETS_DIR, nome_file)

    if not os.path.exists(percorso):
        return None

    #imread_unchanged carica anche il canale alpha se presente
    immagine = cv2.imread(percorso, cv2.IMREAD_UNCHANGED)

    return immagine


#carica le immagini degli accessori all'avvio
hat_img      = _load_asset("hat.png")
glasses_img  = _load_asset("glasses.png")
beard_img    = _load_asset("beard.png")
gilberto_img = _load_asset("gilberto.png")

#dizionario degli accessori attivi, modificato da main.py tramite i tasti
accessories = {
    "hat":     False,
    "glasses": False,
    "beard":   False,
    "mirror":  False,
}


# --------------------------------------------------------------------------
#funzione di sovrapposizione png con trasparenza
# --------------------------------------------------------------------------

def overlay(frame, img, x, y, w, h):
    #sovrappone un png (con o senza alpha) sul frame alla posizione (x,y) con dimensione (w,h).
    #se l'immagine esce dai bordi del frame, la parte fuori viene tagliata automaticamente.

    if img is None:
        return frame
    if w <= 0 or h <= 0:
        return frame

    altezza_frame   = frame.shape[0]
    larghezza_frame = frame.shape[1]

    #calcola le coordinate della zona di destinazione, tagliate ai bordi del frame
    x1 = x
    if x1 < 0:
        x1 = 0

    y1 = y
    if y1 < 0:
        y1 = 0

    x2 = x + w
    if x2 > larghezza_frame:
        x2 = larghezza_frame

    y2 = y + h
    if y2 > altezza_frame:
        y2 = altezza_frame

    if x1 >= x2 or y1 >= y2:
        return frame

    #ridimensiona l'immagine alla dimensione richiesta
    img_rid = cv2.resize(img, (w, h))

    #calcola la parte dell'immagine che rientra nel frame
    ix1 = x1 - x
    iy1 = y1 - y
    ix2 = ix1 + (x2 - x1)
    iy2 = iy1 + (y2 - y1)

    roi   = frame[y1:y2, x1:x2]
    parte = img_rid[iy1:iy2, ix1:ix2]

    if parte.shape[2] == 4:
        #usa il canale alpha per mescolare accessorio e sfondo
        alpha        = parte[:, :, 3:4].astype(np.float32) / 255.0
        colore_parte = parte[:, :, 0:3].astype(np.float32)
        colore_roi   = roi.astype(np.float32)

        #pixel finale = accessorio * alpha + sfondo * (1 - alpha)
        miscelato = colore_parte * alpha + colore_roi * (1.0 - alpha)
        roi[:]    = miscelato.astype(np.uint8)

    else:
        #nessun alpha: sovrascrittura diretta
        roi[:] = parte[:, :, 0:3]

    frame[y1:y2, x1:x2] = roi

    return frame


# --------------------------------------------------------------------------
#rilevamento volti
# --------------------------------------------------------------------------

def detect_faces(frame):
    #rileva i volti nel frame con haar cascade e disegna un rettangolo verde attorno a ognuno.
    #restituisce il frame annotato e la lista dei rettangoli (x, y, w, h).

    out  = frame.copy()
    gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)

    #scalefactor=1.1 riduce l'immagine del 10% a ogni passata
    #minneighbors=4 richiede almeno 4 rilevamenti sovrapposti prima di confermare
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

    i = 0
    while i < len(faces):
        x = faces[i][0]
        y = faces[i][1]
        w = faces[i][2]
        h = faces[i][3]
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
        i = i + 1

    return out, faces


# --------------------------------------------------------------------------
#sfondo sfocato
# --------------------------------------------------------------------------

def background_blur(frame, faces):
    #sfoca tutto il frame tranne la zona del viso rilevato.
    #se non c'e nessun viso, l'intero frame e sfocato.

    #sfocatura forte su tutto il frame
    frame_sfocato = cv2.GaussianBlur(frame.copy(), (51, 51), 0)

    if len(faces) == 0:
        return frame_sfocato

    out = frame_sfocato.copy()

    i = 0
    while i < len(faces):
        x = faces[i][0]
        y = faces[i][1]
        w = faces[i][2]
        h = faces[i][3]

        #aggiunge un margine del 15% attorno alla faccia per non tagliare i capelli
        pad = int(0.15 * max(w, h))

        x1 = x - pad
        if x1 < 0:
            x1 = 0

        y1 = y - pad
        if y1 < 0:
            y1 = 0

        x2 = x + w + pad
        if x2 > frame.shape[1]:
            x2 = frame.shape[1]

        y2 = y + h + pad
        if y2 > frame.shape[0]:
            y2 = frame.shape[0]

        #copia la zona nitida dal frame originale
        out[y1:y2, x1:x2] = frame[y1:y2, x1:x2]

        i = i + 1

    return out


# --------------------------------------------------------------------------
#accessori (cappello, occhiali, barba)
# --------------------------------------------------------------------------

def apply_accessories(frame, faces):
    #sovrappone gli accessori attivi su ogni volto rilevato.
    #le posizioni sono calcolate in proporzione al rettangolo della faccia.

    i = 0
    while i < len(faces):
        x = faces[i][0]
        y = faces[i][1]
        w = faces[i][2]
        h = faces[i][3]

        #cappello: posizionato sopra la faccia, un po' piu largo
        if accessories["hat"] == True:
            hat_x = x - int(w * 0.1)
            hat_y = y - int(h * 0.75)
            hat_w = int(w * 1.2)
            hat_h = int(h * 0.75)
            overlay(frame, hat_img, hat_x, hat_y, hat_w, hat_h)

        #occhiali: al 25% dall'alto della faccia
        if accessories["glasses"] == True:
            occ_x = x
            occ_y = y + int(h * 0.25)
            occ_w = w
            occ_h = int(h * 0.25)
            overlay(frame, glasses_img, occ_x, occ_y, occ_w, occ_h)

        #barba: nella meta inferiore della faccia
        if accessories["beard"] == True:
            barba_x = x
            barba_y = y + int(h * 0.55)
            barba_w = w
            barba_h = int(h * 0.45)
            overlay(frame, beard_img, barba_x, barba_y, barba_w, barba_h)

        i = i + 1

    return frame


# --------------------------------------------------------------------------
#filtro gilberto
# --------------------------------------------------------------------------

def gilberto_filter(frame, faces):
    #sovrappone gilberto.png esattamente sul rettangolo di ogni volto rilevato.
    #se il file non e presente nella cartella assets, non fa nulla.

    if gilberto_img is None:
        return frame

    out = frame.copy()

    i = 0
    while i < len(faces):
        x = faces[i][0]
        y = faces[i][1]
        w = faces[i][2]
        h = faces[i][3]

        gilb = cv2.resize(gilberto_img, (w, h))

        if gilb.shape[2] == 4:
            alpha          = gilb[:, :, 3:4].astype(np.float32) / 255.0
            colore_gilb    = gilb[:, :, 0:3].astype(np.float32)
            roi            = out[y:y+h, x:x+w].astype(np.float32)
            miscelato      = colore_gilb * alpha + roi * (1.0 - alpha)
            out[y:y+h, x:x+w] = miscelato.astype(np.uint8)
        else:
            out[y:y+h, x:x+w] = gilb[:, :, 0:3]

        i = i + 1

    return out


# --------------------------------------------------------------------------
#etichetta testo sopra i volti
# --------------------------------------------------------------------------

def draw_label(frame, faces, testo):
    #scrive un'etichetta di testo sopra ogni volto rilevato.
    #il testo e configurabile dal chiamante.

    out = frame.copy()

    i = 0
    while i < len(faces):
        x = faces[i][0]
        y = faces[i][1]

        cv2.putText(out, testo, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        i = i + 1

    return out


# --------------------------------------------------------------------------
#rilevamento movimento
# --------------------------------------------------------------------------

def motion_detection(frame, prev):
    #confronta il frame corrente con il precedente e illumina le zone cambiate.
    #se non esiste ancora un frame precedente, restituisce il frame invariato.

    if prev is None:
        return frame.copy(), frame.copy()

    #differenza assoluta pixel per pixel tra i due frame
    diff      = cv2.absdiff(frame, prev)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    #soglia binaria: i pixel con differenza > 25 diventano bianchi
    soglia        = 25
    valore_max    = 255
    _, maschera   = cv2.threshold(gray_diff, soglia, valore_max, cv2.THRESH_BINARY)
    maschera_bgr  = cv2.cvtColor(maschera, cv2.COLOR_GRAY2BGR)

    #sovrappone la maschera al frame con peso 0.3
    result = cv2.addWeighted(frame, 0.7, maschera_bgr, 0.3, 0)

    return result, frame.copy()


# --------------------------------------------------------------------------
#effetto fantasma
# --------------------------------------------------------------------------

def ghost_effect(frame, prev):
    #sovrappone il frame corrente al precedente per creare una scia semitrasparente.
    #il frame corrente ha peso 0.75, il precedente 0.25.

    if prev is None:
        return frame.copy()

    result = cv2.addWeighted(frame, 0.75, prev, 0.25, 0)

    return result