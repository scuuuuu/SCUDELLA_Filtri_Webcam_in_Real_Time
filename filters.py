#filters.py
#contiene tutti i filtri visivi applicabili al frame della webcam.
#
#ogni funzione:
#  riceve il frame come primo parametro
#  restituisce il frame modificato
#  non modifica l'originale, lavora su una copia
#  ha un commento in cima che spiega cosa fa

import cv2
import numpy as np


def grayscale(frame):
    #converte il frame in bianco e nero.
    #riconverte a 3 canali per mantenerlo compatibile con il resto.

    gray   = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.cvtColor(gray,  cv2.COLOR_GRAY2BGR)

    return result


def negative(frame):
    #inverte i colori del frame: ogni pixel p diventa 255 - p.
    #produce l'effetto del negativo fotografico.

    copia  = frame.copy()
    result = cv2.bitwise_not(copia)

    return result


def mirror(frame):
    #specchia il frame orizzontalmente.
    #utile come modalita selfie.

    copia  = frame.copy()
    result = cv2.flip(copia, 1)

    return result


def thermal(frame):
    #applica una colormap termica al frame.
    #i toni blu sono le zone scure, quelli rossi le zone chiare.

    #la colormap vuole un'immagine a un canale solo
    gray   = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    return result


def sepia(frame):
    #applica il filtro seppia per un effetto vintage caldo.
    #mescola i canali r, g, b con i coefficienti classici del filtro seppia.

    #float32 per evitare che i valori vadano fuori range durante i calcoli
    img = frame.copy().astype(np.float32)

    b_orig = img[:, :, 0]
    g_orig = img[:, :, 1]
    r_orig = img[:, :, 2]

    r_nuovo = r_orig * 0.393 + g_orig * 0.769 + b_orig * 0.189
    g_nuovo = r_orig * 0.349 + g_orig * 0.686 + b_orig * 0.168
    b_nuovo = r_orig * 0.272 + g_orig * 0.534 + b_orig * 0.131

    #clip limita i valori tra 0 e 255 per evitare overflow
    r_clip = np.clip(r_nuovo, 0, 255)
    g_clip = np.clip(g_nuovo, 0, 255)
    b_clip = np.clip(b_nuovo, 0, 255)

    result = np.zeros_like(frame, dtype=np.uint8)
    result[:, :, 0] = b_clip.astype(np.uint8)
    result[:, :, 1] = g_clip.astype(np.uint8)
    result[:, :, 2] = r_clip.astype(np.uint8)

    return result


def blur_soft(frame):
    #sfocatura leggera con un filtro gaussiano piccolo.

    copia  = frame.copy()
    result = cv2.GaussianBlur(copia, (15, 15), 0)

    return result


def blur_strong(frame):
    #sfocatura molto forte, effetto quasi astratto.

    copia  = frame.copy()
    result = cv2.GaussianBlur(copia, (35, 35), 0)

    return result


def pixelate(frame):
    #effetto pixel art: riduce il frame al 10% e lo riporta alla dimensione originale.
    #l'interpolazione nearest non liscia i pixel, producendo grandi blocchi colorati.

    height = frame.shape[0]
    width  = frame.shape[1]

    small_w = int(width  * 0.1)
    small_h = int(height * 0.1)

    if small_w < 1:
        small_w = 1
    if small_h < 1:
        small_h = 1

    #rimpicciolisce con interpolazione lineare, poi ingrandisce con nearest
    small  = cv2.resize(frame.copy(), (small_w, small_h), interpolation=cv2.INTER_LINEAR)
    result = cv2.resize(small,        (width, height),    interpolation=cv2.INTER_NEAREST)

    return result


def cartoon(frame):
    #effetto fumetto: appiattisce i colori e aggiunge contorni neri.
    #1) due passate di filtro bilaterale per rendere i colori piatti
    #2) canny rileva i bordi sul frame originale
    #3) i bordi vengono sottratti dall'immagine appiattita -> linee nere

    img = frame.copy()

    #filtro bilaterale: smussa senza cancellare i bordi, due passate per effetto piu marcato
    img = cv2.bilateralFilter(img, 9, 75, 75)
    img = cv2.bilateralFilter(img, 9, 75, 75)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #medianblur riduce il rumore prima di cercare i bordi
    gray = cv2.medianBlur(gray, 7)

    edges     = cv2.Canny(gray, 50, 150)
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    #subtract: dove i bordi sono bianchi, il risultato diventa nero
    result = cv2.subtract(img, edges_bgr)

    return result


def vignette(frame):
    #scurisce i bordi del frame con una maschera a forma di ellisse sfumata.
    #il centro resta luminoso, i bordi diventano sempre piu scuri.

    img = frame.copy()
    h   = img.shape[0]
    w   = img.shape[1]

    #due gaussiane 1d (verticale e orizzontale), il loro prodotto fa la maschera 2d
    ky = cv2.getGaussianKernel(h, h * 0.5)
    kx = cv2.getGaussianKernel(w, w * 0.5)

    maschera = ky * kx.T
    maschera = maschera / maschera.max()

    img[:, :, 0] = (img[:, :, 0] * maschera).astype(np.uint8)
    img[:, :, 1] = (img[:, :, 1] * maschera).astype(np.uint8)
    img[:, :, 2] = (img[:, :, 2] * maschera).astype(np.uint8)

    return img


def solarize(frame):
    #solarizzazione fotografica: i pixel piu chiari di 128 vengono invertiti.
    #produce un effetto psichedelico tipico delle foto sovraesposte.

    img    = frame.copy()
    result = np.where(img > 128, 255 - img, img).astype(np.uint8)

    return result


def motion_blur(frame):
    #simula il mosso orizzontale con un filtro direzionale.
    #il filtro fa la media di 15 pixel consecutivi sulla stessa riga.

    SIZE = 15

    img = frame.copy()

    #matrice di zeri con una sola riga centrale piena di 1/SIZE
    kernel = np.zeros((SIZE, SIZE))
    kernel[SIZE // 2, :] = 1.0 / SIZE

    result = cv2.filter2D(img, -1, kernel)

    return result