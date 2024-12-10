from enum import Enum
from Formas import *

class PosPonto(int, Enum):
    SOBRE = 0
    ESQUERDA = 1
    DIREITA = 3

class Pos(Enum):
    FORA = 0
    DENTRO = 1
    EM_CIMA = 2

# Variaveis Globais
INSIDE = 0  # Dentro da janela
LEFT = 1  # Para a esquerda da janela
RIGHT = 2  # Para a direita da janela
BOTTOM = 4  # Abaixo da janela
TOP = 8  # Acima da janela


class ClippingPonto():
    def ponto_contido_recorte(ponto: Ponto, window: Recorte):
        if window.min.x <= ponto.x <= window.max.x and window.min.y <= ponto.y <= window.max.y:
            ponto.visivel = True
        else:
            ponto.visivel = False


class CohenSutherland():

    def define_codigo(ponto: Ponto, window: Recorte) -> int:
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

    def clipping_reta(self, reta: Reta, window: Recorte):
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
                # Calculo da interseção com a janela
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
                    reta.p1 = Ponto(x, y)
                    c1 = CohenSutherland.define_codigo(reta.p1, window)
                else:
                    reta.p2 = Ponto(x, y)
                    c2 = CohenSutherland.define_codigo(reta.p2, window)


class WeilerAtherton():

    @staticmethod
    def clipping_poligono(poligono: Poligono, window: Recorte) -> list[Poligono]:
        novos_poligonos = list[Poligono]

        arestas_window = [
            Reta(window.min, Ponto(window.max.x, window.min.y)),  # Aresta inferior
            Reta(Ponto(window.max.x, window.min.y), window.max),  # Aresta direita
            Reta(window.max, Ponto(window.min.x, window.max.y)),  # Aresta superior
            Reta(Ponto(window.min.x, window.max.y), window.min)  # Aresta esquerda
        ]

        for i in range(len(poligono.pontos)):
            p1 = poligono.pontos[i]
            p2 = poligono.pontos[(i + 1) % len(poligono.pontos)]  # Próximo ponto (fechando o polígono)
            reta_poligono = Reta(p1, p2)
            print(f"Aresta do polígono: ({p1.x}, {p1.y}) -> ({p2.x}, {p2.y})")
            for aresta in arestas_window:
                inter = intersecta(reta_poligono, aresta)
                if inter:
                    ponto = ponto_interseccao(reta_poligono.p1, reta_poligono.p2, aresta.p1, aresta.p2)
                    print(f"  Interseção com a janela: ({ponto.x:.2f}, {ponto.y:.2f})")

        return novos_poligonos


def produto_vetorial(a: Ponto, b: Ponto, c: Ponto):
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

def posicao_ponto(seg: Reta, c: Ponto) -> PosPonto:
    produto = produto_vetorial(seg.p1, seg.p2, c)
    if produto == 0:
        return PosPonto.SOBRE
    elif produto < 0:
        return PosPonto.ESQUERDA
    else:
        return PosPonto.DIREITA

def intersecta(segA: Reta, segB: Reta)-> bool:
    a1 = posicao_ponto(segB, segA.p1)
    a2 = posicao_ponto(segB, segA.p2)
    b1 = posicao_ponto(Reta(segA.p1, segA.p2), segB.p1)
    b2 = posicao_ponto(Reta(segA.p1, segA.p2), segB.p2)
    res = a1 * a2 + b1 * b2
    if res == 6 or res == 3:
        return True
    else:
        return False

def ponto_interseccao(k, l, m, n):
    det = (n.x - m.x) * (l.y - k.y) - (n.y - m.y) * (l.x - k.x)
    if det == 0:
        return None  # Não há interseção

    s = ((n.x - m.x) * (m.y - k.y) - (n.y - m.y) * (m.x - k.x)) / det
    x = k.x + (l.x - k.x) * s
    y = k.y + (l.y - k.y) * s
    return Ponto(x, y)

def x_min_poli(poli:Poligono):
    xMin = poli.pontos[0].x
    for i in range(len(poli.pontos)):
        if poli.pontos[i].x < xMin:
            xMin = poli.pontos[i].x
    return xMin

def ponto_no_intervalo(segA: Reta, c: Ponto)->bool:
    if ((segA.p1.x <= c.x <= segA.p2.x) or (segA.p1.x >= c.x >= segA.p2.x)) and ((segA.p1.y <= c.y <= segA.p2.y) or (
            segA.p1.y >= c.y >= segA.p2.y)):
        return True
    else:
        return False

def y_min_segmento(seg: Reta):
    if seg.p1.y <= seg.p2.y:
        return seg.p1.y
    else:
        return seg.p2.y

def dentro_poli(poli: Poligono, alvo: Ponto):
    qtdInterseccoes = 0
    segAlvo = Reta(alvo, Ponto(x_min_poli(poli)-1, alvo.y))
    for i in range(len(poli.pontos)):
        segPoli = Reta(poli.pontos[i], poli.pontos[(i+1)%len(poli.pontos)])
        # 1º caso, quando o ponto alvo em cima da fronteira
        if posicao_ponto(segPoli, alvo) == PosPonto.SOBRE and ponto_no_intervalo(segPoli, alvo) == True:
            return Pos.EM_CIMA
        elif intersecta(segPoli, segAlvo): # 2º caso, quando ao segmento alvo intersecta o segmento do poligono e ponto do segmento do poligono com o menor y nao esta sobre o segmento alvo
            if not ((posicao_ponto(segAlvo, segPoli.p1) == PosPonto.SOBRE and y_min_segmento(segPoli) == segPoli.p1.y) or (posicao_ponto(segAlvo, segPoli.p2) == PosPonto.SOBRE and y_min_segmento(segPoli) == segPoli.p2.y)):
                qtdInterseccoes += 1
    if qtdInterseccoes % 2 == 0:
        return Pos.FORA
    else:
        return Pos.DENTRO