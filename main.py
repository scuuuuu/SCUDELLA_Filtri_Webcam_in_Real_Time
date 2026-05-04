import cv2

cap = cv2.VideoCapture(0)

mode = 0

def get_mode_name(mode):
    return {
        0: "Normale",
        1: "Bianco e Nero",
        2: "Negativo",
        3: "Termico",
        4: "Soffuso",
        5: "Blurred"
    }.get(mode, "Sconosciuto")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Applica effetti
    if mode == 1:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif mode == 2:
        frame = cv2.bitwise_not(frame)
    elif mode == 3:
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
    elif mode == 4:
        frame = cv2.GaussianBlur(frame, (15, 15), 0)
    elif mode == 5:
        frame = cv2.GaussianBlur(frame, (35, 35), 0)

    # Se è grayscale → torna a BGR per scrivere testo
    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    h, w = frame.shape[:2]

    # Testo modalità (in basso)
    text = f"Modalita: {get_mode_name(mode)}"
    cv2.putText(frame, text, (10, h - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2, cv2.LINE_AA)

    # Legenda comandi (ancora più in basso)
    legenda = "1:B/N  2:Neg  3:Termico  4:Soffuso  5:Blur  0:Normale  q:Esci"
    cv2.putText(frame, legenda, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow('Webcam', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('1'):
        mode = 1
    elif key == ord('2'):
        mode = 2
    elif key == ord('3'):
        mode = 3
    elif key == ord('4'):
        mode = 4
    elif key == ord('5'):
        mode = 5
    elif key == ord('0'):
        mode = 0

cap.release()
cv2.destroyAllWindows()