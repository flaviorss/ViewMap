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

class ClippingPonto():
    def ponto_contido_recorte(ponto: Ponto):
        window = Recorte(Ponto(-1, -1), Ponto(1, 1))
        if window.min.x <= ponto.x <= window.max.x and window.min.y <= ponto.y <= window.max.y:
            ponto.visivel = True
        else:
            ponto.visivel = False

class CohenSutherland():

    def define_codigo(ponto: Ponto, window: Recorte) -> int:
        codigo = 0
        if ponto.x > window.max.x:
            codigo += 2
        elif ponto.x < window.min.x:
            codigo += 1

        if ponto.y > window.max.y:
            codigo |= 8
        elif ponto.y < window.min.y:
            codigo |= 4

        return codigo

    def clipping_reta(reta: Segmento):
        window = Recorte(Ponto(-1,-1),Ponto(1,1))
        done = False
        reta.visivel = False
        codOut = 0
        p = Ponto(0,0)
        codA = CohenSutherland.define_codigo(reta.p1, window)
        codB = CohenSutherland.define_codigo(reta.p2, window)

        while not done:
            if(codA | codB) == 0:
                reta.visivel = done  = True
            elif (codA & codB) != 0:
                done = True
            else:
                if (codA != 0): codOut = codA
                else: codOut = codB

                if reta.p1.x == reta.p2.x:
                    if codOut & 0x08:
                        p.y = window.max.y
                    else:
                        p.y = window.min.y
                    p.x = reta.p1.x
                elif reta.p1.y == reta.p2.y:
                    if codOut & 0x01:
                        p.x = window.min.x
                    else:
                        p.x = window.max.x
                    p.y = reta.p1.y
                else:
                    m = (reta.p2.y - reta.p1.y) / (reta.p2.x - reta.p1.x)
                    if codOut & 0x08:
                        p.y = window.max.y
                        p.x = reta.p1.x + (window.max.y - reta.p1.y)/m
                    elif codOut & 0x04:
                        p.y = window.min.y
                        p.x = reta.p1.x + (window.min.y - reta.p1.y)/m
                    elif codOut & 0x02:
                        p.x = window.max.x
                        p.y = reta.p1.y + m*(window.max.x - reta.p1.x)
                    elif codOut & 0x01:
                        p.x = window.min.x
                        p.y = reta.p1.y + m*(window.min.x - reta.p1.x)

                if codOut == codA:
                    reta.p1 = Ponto(p.x, p.y)
                    codA = CohenSutherland.define_codigo(reta.p1, window)
                else:
                    reta.p2 = Ponto(p.x, p.y)
                    codB = CohenSutherland.define_codigo(reta.p2, window)


class LiangBarsky():

    def clipping_reta(reta: Segmento):
        window = Recorte(Ponto(-1, -1), Ponto(1, 1))
        reta.visivel = True
        p = [0] * 4
        q = [0] * 4
        r = [0] * 4
        u1 = 0
        u2 = 1
        deltaX = reta.p2.x - reta.p1.x
        deltaY = reta.p2.y - reta.p1.y

        p[0] = -deltaX
        p[1] = deltaX
        p[2] = -deltaY
        p[3] = deltaY

        q[0] = reta.p1.x - window.min.x
        q[1] = window.max.x - reta.p1.x
        q[2] = reta.p1.y - window.min.y
        q[3] = window.max.y - reta.p1.y

        for i in range(4):
            if p[i] != 0:
                r[i] = q[i] / p[i]
                if p[i] < 0 and r[i] > u1:
                    u1 = r[i]
                elif p[i] > 0 and r[i] < u2:
                    u2 = r[i]
            elif q[i] < 0:
                reta.visivel = False

        #if reta.visivel and u1 < u2:
        if 0 <= u1 <= 1 and 0 <= u2 <= 1:
            Q1 = Ponto(reta.p1.x + deltaX * u1, reta.p1.y + deltaY * u1)
            Q2 = Ponto(reta.p1.x + deltaX * u2, reta.p1.y + deltaY * u2)
            reta.p1 = Q1
            reta.p2 = Q2
        else:
            reta.visivel = False


class WeilerAtherton():

    @staticmethod
    def clipping_poligono(poligono: Poligono, window: Recorte) -> list[Poligono]:
        novos_poligonos = list[Poligono]

        arestas_window = [
            Segmento(window.min, Ponto(window.max.x, window.min.y)),  # Aresta inferior
            Segmento(Ponto(window.max.x, window.min.y), window.max),  # Aresta direita
            Segmento(window.max, Ponto(window.min.x, window.max.y)),  # Aresta superior
            Segmento(Ponto(window.min.x, window.max.y), window.min)  # Aresta esquerda
        ]

        for i in range(len(poligono.pontos)):
            p1 = poligono.pontos[i]
            p2 = poligono.pontos[(i + 1) % len(poligono.pontos)]  # Próximo ponto (fechando o polígono)
            reta_poligono = Segmento(p1, p2)
            print(f"Aresta do polígono: ({p1.x}, {p1.y}) -> ({p2.x}, {p2.y})")
            for aresta in arestas_window:
                inter = intersecta(reta_poligono, aresta)
                if inter:
                    ponto = ponto_interseccao(reta_poligono.p1, reta_poligono.p2, aresta.p1, aresta.p2)
                    print(f"  Interseção com a janela: ({ponto.x:.2f}, {ponto.y:.2f})")

        return novos_poligonos


def produto_vetorial(a: Ponto, b: Ponto, c: Ponto):
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

def posicao_ponto(seg: Segmento, c: Ponto) -> PosPonto:
    produto = produto_vetorial(seg.p1, seg.p2, c)
    if produto == 0:
        return PosPonto.SOBRE
    elif produto < 0:
        return PosPonto.ESQUERDA
    else:
        return PosPonto.DIREITA

def intersecta(segA: Segmento, segB: Segmento)-> bool:
    a1 = posicao_ponto(segB, segA.p1)
    a2 = posicao_ponto(segB, segA.p2)
    b1 = posicao_ponto(Segmento(segA.p1, segA.p2), segB.p1)
    b2 = posicao_ponto(Segmento(segA.p1, segA.p2), segB.p2)
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

def ponto_no_intervalo(segA: Segmento, c: Ponto)->bool:
    if ((segA.p1.x <= c.x <= segA.p2.x) or (segA.p1.x >= c.x >= segA.p2.x)) and ((segA.p1.y <= c.y <= segA.p2.y) or (
            segA.p1.y >= c.y >= segA.p2.y)):
        return True
    else:
        return False

def y_min_segmento(seg: Segmento):
    if seg.p1.y <= seg.p2.y:
        return seg.p1.y
    else:
        return seg.p2.y

def dentro_poli(poli: Poligono, alvo: Ponto):
    qtdInterseccoes = 0
    segAlvo = Segmento(alvo, Ponto(x_min_poli(poli) - 1, alvo.y))
    for i in range(len(poli.pontos)):
        segPoli = Segmento(poli.pontos[i], poli.pontos[(i + 1) % len(poli.pontos)])
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