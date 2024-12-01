from Formas import *

#Variaveis Globais
INSIDE = 0  #Dentro da janela
LEFT = 1  #Para a esquerda da janela
RIGHT = 2  #Para a direita da janela
BOTTOM = 4  #Abaixo da janela
TOP = 8  #Acima da janela

class ClippingPonto():
    def ponto_contido_recorte(ponto: Ponto, window: Recorte):
        if window.min.x <= ponto.x <= window.max.x and window.min.y <= ponto.y <= window.max.y:
            ponto.visivel = True
        else:
            ponto.visivel = False

class CohenSutherland():

    def define_codigo(ponto: Ponto, window: Recorte)-> int:
        codigo = INSIDE
        if ponto.x < window.min.x:
            codigo += LEFT
        elif ponto.x > window.max.x:
            codigo += RIGHT
        if ponto.y < window.min.y:
            codigo += BOTTOM
        elif ponto.y > window.max.y:
            codigo += TOP

        return codigo

    def clipping_reta(self, reta: Reta,window: Recorte):
        c1 = CohenSutherland.define_codigo(reta.p1, window)
        c2 = CohenSutherland.define_codigo(reta.p2, window)

        while True:
            if c1 == INSIDE and c2 == INSIDE:
                reta.visivel = True
                return Reta(reta.p1, reta.p2)
            elif c1 != 0 and c2 != 0:
                reta.visivel = False
                return None
            else:
                if c1 != INSIDE:
                    outCodigo = c1
                    outPonto = reta.p1
                else:
                    outCodigo = c2
                    outPonto = reta.p2

                x, y = outPonto.x, outPonto.y
                #Calculo da interseção com a janela
                if outCodigo & TOP:
                    x = reta.p1.x + (reta.p2.x - reta.p1.x) * (window.max.y - reta.p1.y) / (reta.p2.y - reta.p1.y)
                    y = window.max.y
                elif outCodigo & BOTTOM:
                    x = reta.p1.x + (reta.p2.x - reta.p1.x) * (window.min.y - reta.p1.y) / (reta.p2.y - reta.p1.y)
                    y = window.min.y
                elif outCodigo & LEFT:
                    y = reta.p1.y + (reta.p2.y - reta.p1.y) * (window.min.x - reta.p1.x) / (reta.p2.x - reta.p1.x)
                    x = window.min.x
                elif outCodigo & RIGHT:
                    y = reta.p1.y + (reta.p2.y - reta.p1.y) * (window.max.x - reta.p1.x) / (reta.p2.x - reta.p1.x)


                if outCodigo == c1:
                    reta.p1 = Ponto(x,y)
                    c1 = CohenSutherland.define_codigo(reta.p1, window)
                else:
                    reta.p2 = Ponto(x, y)
                    c2 = CohenSutherland.define_codigo(reta.p2, window)