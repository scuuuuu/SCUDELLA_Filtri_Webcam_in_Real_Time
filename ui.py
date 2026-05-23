#ui.py
#gestisce l'interfaccia grafica sovrapposta al feed webcam.
#
#ogni funzione:
#  riceve il frame come primo parametro
#  restituisce il frame modificato
#  lavora su una copia, non modifica l'originale

import cv2
import numpy as np


#nomi completi dei filtri, l'indice corrisponde al tasto premuto
MODE_NAMES = [
    "Normale",
    "B/N",
    "Negativo",
    "Termico",
    "Seppia",
    "Blur Soft",
    "Blur Forte",
    "Cartoon",
    "Pixel",
    "Gilberto",
]

#etichette nella barra laterale
FILTER_BAR_LABELS = [
    "0  Normale",
    "1  B/N",
    "2  Negativo",
    "3  Termico",
    "4  Seppia",
    "5  Blur Soft",
    "6  Blur Forte",
    "7  Cartoon",
    "8  Pixel",
    "9  Gilberto",
]

#colori usati in tutta l'interfaccia
VERDE   = (60,  220, 60)
BIANCO  = (240, 240, 240)
GRIGIO  = (150, 150, 150)
AZZURRO = (230, 180, 0)
CIANO   = (200, 200, 0)
ROSSO   = (0,   0,   220)
SFONDO  = (12,  12,  18)


def _pannello(out, x1, y1, x2, y2, alpha=0.68):
    #disegna un rettangolo semitrasparente scuro sul frame
    overlay = out.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), SFONDO, -1)
    cv2.addWeighted(overlay, alpha, out, 1.0 - alpha, 0, out)


def _accent(out, x, y1, y2, colore, spessore=3):
    #disegna una linea verticale colorata come bordo decorativo
    cv2.line(out, (x, y1), (x, y2), colore, spessore)


def _separatore(out, y, x1, x2):
    #disegna una linea orizzontale sottile come separatore tra sezioni
    cv2.line(out, (x1, y), (x2, y), (45, 45, 52), 1)


def get_mode_name(mode):
    #restituisce il nome del filtro attivo in base al numero
    if mode >= 0 and mode < len(MODE_NAMES):
        return MODE_NAMES[mode]
    else:
        return "?"


def draw_hud(frame, mode_name, fps, face_count, rec, motion, ghost,
             vignette=False, motion_blur=False, auto_mode=False, bg_blur=False):
    #disegna il pannello informativo in alto a sinistra con fps, filtro e facce

    out = frame.copy()
    h = out.shape[0]
    w = out.shape[1]

    #sfondo del pannello hud
    _pannello(out, 0, 0, 245, 135)

    #linea accent verde sul bordo sinistro
    _accent(out, 3, 0, 135, VERDE)

    #fps in verde, testo grande
    stringa_fps = "FPS  " + str(int(fps))
    cv2.putText(out, stringa_fps, (14, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.68, VERDE, 2)

    _separatore(out, 38, 14, 238)

    #label grigia + nome filtro bianco
    cv2.putText(out, "FILTRO", (14, 57),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, GRIGIO, 1)
    cv2.putText(out, mode_name, (82, 57),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, BIANCO, 2)

    #label grigia + numero facce in azzurro
    cv2.putText(out, "FACCE", (14, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, GRIGIO, 1)
    cv2.putText(out, str(face_count), (82, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, AZZURRO, 2)

    _separatore(out, 88, 14, 238)

    #badge degli effetti attivi, ognuno con il suo colore
    badge_lista = []
    if motion == True:
        badge_lista.append(("MOV",    (50,  200, 100)))
    if ghost == True:
        badge_lista.append(("GHOST",  (180, 80,  220)))
    if vignette == True:
        badge_lista.append(("VIG",    (0,   170, 220)))
    if motion_blur == True:
        badge_lista.append(("MBLUR",  (200, 120, 0)))
    if bg_blur == True:
        badge_lista.append(("BGBLUR", (0,   200, 160)))
    if auto_mode == True:
        badge_lista.append(("AUTO",   CIANO))

    pos_x = 14
    i = 0
    while i < len(badge_lista):
        testo_badge = badge_lista[i][0]
        colore_badge = badge_lista[i][1]
        cv2.putText(out, testo_badge, (pos_x, 112),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, colore_badge, 1)
        #misura la larghezza del testo per posizionare il prossimo badge
        (tw, _), _ = cv2.getTextSize(testo_badge, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
        pos_x = pos_x + tw + 10
        i = i + 1

    #indicatore rec in alto a destra
    if rec == True:
        _pannello(out, w - 95, 5, w - 5, 40)
        _accent(out, w - 95, 5, 40, ROSSO, 2)
        #cerchio rosso con alone piu scuro
        cv2.circle(out, (w - 78, 23), 9,  ROSSO,        -1)
        cv2.circle(out, (w - 78, 23), 12, (0, 0, 100),   1)
        cv2.putText(out, "REC", (w - 64, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, ROSSO, 2)

    #indicatore auto in alto a destra, sotto rec se presente
    if auto_mode == True:
        offset = 48 if rec == True else 5
        _pannello(out, w - 95, offset, w - 5, offset + 34)
        _accent(out, w - 95, offset, offset + 34, CIANO, 2)
        cv2.putText(out, "AUTO", (w - 86, offset + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, CIANO, 2)

    return out


def draw_filter_bar(frame, mode):
    #disegna la lista dei filtri sul lato sinistro, con il filtro attivo evidenziato

    out = frame.copy()

    start_y = 148
    step    = 23
    bar_w   = 118
    bar_h   = len(FILTER_BAR_LABELS) * step + 16

    #sfondo della barra filtri
    _pannello(out, 0, start_y - 10, bar_w, start_y + bar_h)
    _accent(out, 3, start_y - 10, start_y + bar_h, (50, 50, 60), 2)

    i = 0
    while i < len(FILTER_BAR_LABELS):
        etichetta = FILTER_BAR_LABELS[i]
        pos_y = start_y + i * step

        if i == mode:
            #sfondo verde scuro sulla riga attiva
            riga_overlay = out.copy()
            cv2.rectangle(riga_overlay, (3, pos_y - 15), (bar_w, pos_y + 7), (0, 70, 0), -1)
            cv2.addWeighted(riga_overlay, 0.75, out, 0.25, 0, out)
            #freccia e testo in verde brillante
            cv2.putText(out, ">", (6, pos_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, VERDE, 2)
            cv2.putText(out, etichetta, (20, pos_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, VERDE, 2)
        else:
            #testo grigio per i filtri non attivi
            cv2.putText(out, etichetta, (16, pos_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, GRIGIO, 1)

        i = i + 1

    return out


def draw_footer(frame):
    #disegna il footer in fondo al frame su due righe con tutti i tasti

    out = frame.copy()
    h = out.shape[0]
    w = out.shape[1]

    #sfondo footer a due righe
    _pannello(out, 0, h - 46, w, h, alpha=0.78)

    #linea accent verde in cima al footer
    cv2.line(out, (0, h - 46), (w, h - 46), (0, 160, 60), 1)

    #riga superiore: azioni principali
    riga1 = "0-9 filtro     S screenshot     R rec/stop     Q esci"
    cv2.putText(out, riga1, (10, h - 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, BIANCO, 1)

    #riga inferiore: effetti toggle
    riga2 = "G occhiali   H cappello   B barba   V vignetta   Z mblur   A auto   M mov   N ghost   F bgblur   X mirror"
    cv2.putText(out, riga2, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.30, GRIGIO, 1)

    return out