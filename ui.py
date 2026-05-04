import cv2

"""
ui.py
Gestisce tutto ciò che è HUD / testo su schermo
"""

def draw_hud(frame, mode_name, fps, faces_count):
    output = frame.copy()
    h, w = output.shape[:2]

    cv2.putText(output, f"FPS: {int(fps)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    cv2.putText(output, f"Modalita: {mode_name}",
                (10, h - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)

    cv2.putText(output, f"Facce: {faces_count}",
                (10, h - 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 0, 255), 2)

    legenda = "1:B/N 2:Neg 3:Termico 4:Soffuso 5:Blur 6:Cartoon 0:Normale q:Esci"
    cv2.putText(output, legenda,
                (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 1)

    return output