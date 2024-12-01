from Formas import *

class ClippingPonto():
    def ponto_contido_recorte(ponto: Ponto, window: Recorte):
        if window.min.x <= ponto.x <= window.max.x and window.min.y <= ponto.y <= window.max.y:
            ponto.visivel = True
        else:
            ponto.visivel = False

