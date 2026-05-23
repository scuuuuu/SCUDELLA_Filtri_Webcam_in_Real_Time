#main.py
#loop principale dell'applicazione: legge i frame dalla webcam,
#applica filtri ed effetti nell'ordine corretto, gestisce i tasti.

import cv2
import os
import time
from datetime import datetime

import effects
import filters
import ui


#intervallo in secondi tra un cambio filtro e l'altro in modalita automatica
AUTO_INTERVAL = 3.0

#numero di filtri selezionabili con i tasti 0-9
NUM_FILTRI = 10


#apre la webcam predefinita
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("errore: impossibile aprire la webcam.")
    exit(1)

#cartelle di salvataggio screenshot e video
SCREENSHOT_DIR = "screenshots"
VIDEO_DIR = "videos"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


#filtro colore attivo, corrisponde al tasto premuto (0-9)
mode = 0

#tempo dell'ultimo frame, serve per calcolare gli fps
prev_time = 0

#frame precedente usato da ghost e motion detection
#viene salvato dopo i filtri ma prima dell'hud, cosi l'hud non interferisce
prev_frame = None

#flag on/off per ogni effetto toggle
motion_enabled      = False
ghost_enabled       = False
bg_blur_enabled     = False
vignette_enabled    = False
motion_blur_enabled = False

#stato della modalita automatica
auto_mode        = False
last_auto_switch = time.time()

#stato della registrazione video
recording    = False
video_writer = None

#lista campioni fps per la media mobile
fps_campioni     = []
MAX_CAMPIONI_FPS = 10


# --------------------------------------------------------------------------
# loop principale
# --------------------------------------------------------------------------

while True:

    ret, frame = cap.read()

    #se la webcam smette di funzionare esce dal loop
    if not ret:
        break


    #calcolo fps con media mobile su 10 campioni
    now = time.time()

    if prev_time != 0:
        delta        = now - prev_time
        fps_istantaneo = 1.0 / delta
        fps_campioni.append(fps_istantaneo)

        if len(fps_campioni) > MAX_CAMPIONI_FPS:
            fps_campioni.pop(0)

    prev_time = now

    if len(fps_campioni) > 0:
        fps = sum(fps_campioni) / len(fps_campioni)
    else:
        fps = 0


    #modalita automatica: avanza il filtro ogni AUTO_INTERVAL secondi
    if auto_mode == True:
        if now - last_auto_switch >= AUTO_INTERVAL:
            mode             = (mode + 1) % NUM_FILTRI
            last_auto_switch = now


    #rilevamento volti: restituisce il frame con i rettangoli e la lista delle facce
    frame, faces = effects.detect_faces(frame)


    #sovrappone cappello, occhiali e barba se attivi
    frame = effects.apply_accessories(frame, faces)

    #scrive il nome sopra ogni faccia rilevata
    frame = effects.draw_label(frame, faces, "FILIPPO")


    #effetto movimento: illumina le zone che cambiano tra un frame e l'altro
    if motion_enabled == True:
        frame, _ = effects.motion_detection(frame, prev_frame)


    #effetto fantasma: lascia una scia semitrasparente del frame precedente
    if ghost_enabled == True:
        frame = effects.ghost_effect(frame, prev_frame)


    #sfondo sfocato: sfoca tutto tranne la zona del viso
    if bg_blur_enabled == True:
        frame = effects.background_blur(frame, faces)


    #specchio orizzontale
    if effects.accessories["mirror"] == True:
        frame = filters.mirror(frame)


    #applica il filtro colore selezionato dal tasto
    if mode == 1:
        frame = filters.grayscale(frame)
    elif mode == 2:
        frame = filters.negative(frame)
    elif mode == 3:
        frame = filters.thermal(frame)
    elif mode == 4:
        frame = filters.sepia(frame)
    elif mode == 5:
        frame = filters.blur_soft(frame)
    elif mode == 6:
        frame = filters.blur_strong(frame)
    elif mode == 7:
        frame = filters.cartoon(frame)
    elif mode == 8:
        frame = filters.pixelate(frame)
    elif mode == 9:
        frame = effects.gilberto_filter(frame, faces)


    #vignettatura: scurisce i bordi del frame
    if vignette_enabled == True:
        frame = filters.vignette(frame)


    #motion blur simulato: sfocatura orizzontale che simula il mosso
    if motion_blur_enabled == True:
        frame = filters.motion_blur(frame)


    #salva il frame prima di aggiungere hud e footer
    #cosi ghost e motion non confrontano frame con le scritte sovrimposte
    prev_frame = frame.copy()


    #disegna hud, barra filtri e footer
    nome_filtro = ui.get_mode_name(mode)
    frame = ui.draw_hud(
        frame, nome_filtro, fps, len(faces),
        recording, motion_enabled, ghost_enabled,
        vignette    = vignette_enabled,
        motion_blur = motion_blur_enabled,
        auto_mode   = auto_mode,
        bg_blur     = bg_blur_enabled
    )
    frame = ui.draw_filter_bar(frame, mode)
    frame = ui.draw_footer(frame)


    #scrive il frame nel file video se la registrazione e attiva
    if recording == True and video_writer is not None:
        video_writer.write(frame)


    #mostra il frame a schermo
    cv2.imshow("Webcam Filtri", frame)


    # --------------------------------------------------------------------------
    # gestione tasti
    # --------------------------------------------------------------------------

    key = cv2.waitKey(1) & 0xFF


    #q -> esce
    if key == ord('q'):
        break


    #s -> salva screenshot con data e ora nel nome
    elif key == ord('s'):
        timestamp           = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_file           = "shot_" + timestamp + ".jpg"
        percorso_screenshot = os.path.join(SCREENSHOT_DIR, nome_file)
        cv2.imwrite(percorso_screenshot, frame)
        print("screenshot salvato: " + percorso_screenshot)


    #r -> avvia o ferma la registrazione video
    elif key == ord('r'):

        if recording == False:
            timestamp      = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_file      = "video_" + timestamp + ".mp4"
            percorso_video = os.path.join(VIDEO_DIR, nome_file)
            fourcc         = cv2.VideoWriter_fourcc(*'mp4v')
            altezza_frame  = frame.shape[0]
            larghezza_frame = frame.shape[1]

            video_writer = cv2.VideoWriter(
                percorso_video, fourcc, 20.0, (larghezza_frame, altezza_frame)
            )

            recording = True
            print("registrazione avviata: " + percorso_video)

        else:
            recording = False

            if video_writer is not None:
                video_writer.release()
                video_writer = None

            print("registrazione fermata.")


    #0-9 -> seleziona il filtro colore
    elif key >= ord('0') and key <= ord('9'):
        mode = key - ord('0')

        if auto_mode == True:
            auto_mode = False
            print("modalita automatica disattivata (selezione manuale).")


    #g -> occhiali on/off
    elif key == ord('g'):
        if effects.accessories["glasses"] == True:
            effects.accessories["glasses"] = False
        else:
            effects.accessories["glasses"] = True


    #h -> cappello on/off
    elif key == ord('h'):
        if effects.accessories["hat"] == True:
            effects.accessories["hat"] = False
        else:
            effects.accessories["hat"] = True


    #b -> barba on/off
    elif key == ord('b'):
        if effects.accessories["beard"] == True:
            effects.accessories["beard"] = False
        else:
            effects.accessories["beard"] = True


    #m -> rilevamento movimento on/off
    elif key == ord('m'):
        if motion_enabled == True:
            motion_enabled = False
        else:
            motion_enabled = True


    #n -> effetto fantasma on/off
    elif key == ord('n'):
        if ghost_enabled == True:
            ghost_enabled = False
        else:
            ghost_enabled = True


    #f -> sfondo sfocato on/off
    elif key == ord('f'):
        if bg_blur_enabled == True:
            bg_blur_enabled = False
        else:
            bg_blur_enabled = True


    #x -> specchio on/off
    elif key == ord('x'):
        if effects.accessories["mirror"] == True:
            effects.accessories["mirror"] = False
        else:
            effects.accessories["mirror"] = True


    #v -> vignettatura on/off
    elif key == ord('v'):
        if vignette_enabled == True:
            vignette_enabled = False
        else:
            vignette_enabled = True


    #z -> motion blur on/off
    elif key == ord('z'):
        if motion_blur_enabled == True:
            motion_blur_enabled = False
        else:
            motion_blur_enabled = True


    #a -> modalita automatica on/off
    elif key == ord('a'):
        if auto_mode == True:
            auto_mode = False
            print("modalita automatica disattivata.")
        else:
            auto_mode        = True
            last_auto_switch = time.time()
            print("modalita automatica attivata, intervallo: " + str(AUTO_INTERVAL) + "s")


# --------------------------------------------------------------------------
# cleanup: rilascia tutte le risorse
# --------------------------------------------------------------------------

cap.release()

if video_writer is not None:
    video_writer.release()

cv2.destroyAllWindows()

print("applicazione chiusa.")