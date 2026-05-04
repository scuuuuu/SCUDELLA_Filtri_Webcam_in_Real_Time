import cv2
import time

import filters
import effects
import ui

cap = cv2.VideoCapture(0)#apre la webcam

mode = 0    #filtro attuale
prev_time = 0   #per calcolo fps

def get_mode_name(mode):
    #ritorna dizionario, se modalita non presente ritorna sconosciuto
    return {
        0: "Normale",
        1: "Bianco e Nero",
        2: "Negativo",
        3: "Termico",
        4: "Soffuso",
        5: "Blur",
        6: "Cartoon"
    }.get(mode, "Sconosciuto")

while True:
    ret, frame = cap.read() #legge frame dalla webcam
    if not ret:
        break   #esce dal loop se non riesce a leggerlo

    current_time = time.time()  #tempo attuale in secondi
    fps = 1 / (current_time - prev_time) if prev_time != 0 else 0   #serve a gestire se il primo frame è 0
    prev_time = current_time   #aggiorna il tempo precedente

    #face detection
    frame, faces = effects.detect_faces(frame)

    #filtri
    if mode == 1:
        frame = filters.grayscale(frame)
    elif mode == 2:
        frame = filters.negative(frame)
    elif mode == 3:
        frame = filters.thermal(frame)
    elif mode == 4:
        frame = filters.blur_soft(frame)
    elif mode == 5:
        frame = filters.blur_strong(frame)
    elif mode == 6:
        frame = filters.cartoon(frame)
    #ui
    frame = ui.draw_hud(frame, get_mode_name(mode), fps, len(faces))
    cv2.imshow("Webcam", frame)  #mostra finestra video
    key = cv2.waitKey(1) #legge il tasto che viene premuto

    if key == ord('q'):
        break
    if ord('0') <= key <= ord('6'):  #se tasto premuto è tra 0 e 6, in codice ascii del carattere
        #converte il codice ASCII in numero
        #esempio: '3' → 51 ASCII → 51 - 48 = 3
        mode = key - ord('0')

cap.release()  #rilascia la cam
cv2.destroyAllWindows()   #chiude finestre opencv