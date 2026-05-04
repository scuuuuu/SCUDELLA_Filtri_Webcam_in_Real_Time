import cv2

"""
filters.py
Contiene tutti i filtri visivi. Ogni funzione:
- riceve frame
- restituisce frame modificato
- NON modifica l'input originale
"""

def grayscale(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def negative(frame):
    return cv2.bitwise_not(frame.copy())

def thermal(frame):
    return cv2.applyColorMap(frame, cv2.COLORMAP_JET)

def blur_soft(frame):
    return cv2.GaussianBlur(frame, (15, 15), 0)

def blur_strong(frame):
    return cv2.GaussianBlur(frame, (35, 35), 0)


def cartoon(frame):
    """
    Effetto cartoon:
    - smussa i colori
    - estrae bordi
    - li sovrappone all'immagine
    """

    img = frame.copy()

    # smoothing colori
    for _ in range(2):
        img = cv2.bilateralFilter(img, 9, 75, 75)

    # edge detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    edges = cv2.Canny(gray, 50, 150)

    # inverti bordi per look più pulito
    edges = cv2.bitwise_not(edges)

    # 3 canali
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # combinazione finale
    return cv2.bitwise_and(img, edges)