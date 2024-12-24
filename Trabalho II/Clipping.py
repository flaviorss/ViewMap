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


class TipoVertice(Enum):
    POLIGONO = 0
    INT_SAIDA = 1
    INT_ENTRADA = 2


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
        window = Recorte(Ponto(-1, -1), Ponto(1, 1))
        done = False
        reta.visivel = False
        codOut = 0
        p = Ponto(0, 0)
        codA = CohenSutherland.define_codigo(reta.p1, window)
        codB = CohenSutherland.define_codigo(reta.p2, window)

        while not done:
            if (codA | codB) == 0:
                reta.visivel = done = True
            elif (codA & codB) != 0:
                done = True
            else:
                if (codA != 0):
                    codOut = codA
                else:
                    codOut = codB

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
                        p.x = reta.p1.x + (window.max.y - reta.p1.y) / m
                    elif codOut & 0x04:
                        p.y = window.min.y
                        p.x = reta.p1.x + (window.min.y - reta.p1.y) / m
                    elif codOut & 0x02:
                        p.x = window.max.x
                        p.y = reta.p1.y + m * (window.max.x - reta.p1.x)
                    elif codOut & 0x01:
                        p.x = window.min.x
                        p.y = reta.p1.y + m * (window.min.x - reta.p1.x)

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

        # if reta.visivel and u1 < u2:
        if 0 <= u1 <= 1 and 0 <= u2 <= 1:
            Q1 = Ponto(reta.p1.x + deltaX * u1, reta.p1.y + deltaY * u1)
            Q2 = Ponto(reta.p1.x + deltaX * u2, reta.p1.y + deltaY * u2)
            reta.p1 = Q1
            reta.p2 = Q2
        else:
            reta.visivel = False


class WeilerAtherton():

    @staticmethod
    def clipping_poligono(poligono: Poligono, window: Recorte):
        novos_poligonos = []

        qtd_vertices_entrada = 0
        pontos_poli_int = []
        pontos_poli_sinal = []
        pontos_poli_usado = []

        pontos_win_int = []
        pontos_win_sinal = []

        intersecoes = []
        intersecoes_sinal = []

        p1 = Ponto(window.min.x, window.min.y)
        p2 = Ponto(window.min.x + window.get_largura(), window.min.y)
        p3 = Ponto(window.max.x, window.max.y)
        p4 = Ponto(window.min.x, window.min.y + window.get_altura())

        poli_win = Poligono([p1, p2, p3, p4])

        arestas_window = [
            Segmento(window.min, Ponto(window.max.x, window.min.y)),  # Aresta inferior
            Segmento(Ponto(window.max.x, window.min.y), window.max),  # Aresta direita
            Segmento(window.max, Ponto(window.min.x, window.max.y)),  # Aresta superior
            Segmento(Ponto(window.min.x, window.max.y), window.min)  # Aresta esquerda
        ]

        for i in range(len(poligono.pontos)):
            pontos_poli_int.append(poligono.pontos[i])
            pontos_poli_sinal.append(TipoVertice.POLIGONO)
            pontos_poli_usado.append(False)

            p1 = poligono.pontos[i]
            p2 = poligono.pontos[(i + 1) % len(poligono.pontos)]  # Próximo ponto (fechando o polígono)
            reta_poligono = Segmento(p1, p2)

            for aresta in arestas_window:
                inter = intersecta(reta_poligono, aresta)
                if inter:
                    ponto = ponto_interseccao(reta_poligono.p1, reta_poligono.p2, aresta.p1, aresta.p2)
                    intersecoes.append(ponto)
                    pontos_poli_int.append(ponto)
                    pontos_poli_usado.append(False)
                    if dentro_poli(poli_win, reta_poligono.p1) == Pos.DENTRO:
                        pontos_poli_sinal.append(TipoVertice.INT_SAIDA)
                        intersecoes_sinal.append(TipoVertice.INT_SAIDA)
                    else:
                        tipo_vertice = TipoVertice.INT_ENTRADA
                        if pontos_poli_sinal[len(pontos_poli_sinal) - 1] == tipo_vertice:

                            deslocamento_int1 = reta_poligono.deslocamento_em_ponto(pontos_poli_int[len(pontos_poli_sinal) - 1])
                            deslocamento_int2 = reta_poligono.deslocamento_em_ponto(ponto)
                            if reta_poligono.comparar_deslocamentos(deslocamento_int1, deslocamento_int2):
                                pontos_poli_sinal.append(TipoVertice.INT_SAIDA)
                                intersecoes_sinal.append(TipoVertice.INT_SAIDA)
                            else:
                                ordem_errada1 = pontos_poli_int.pop()
                                ordem_errada2 = pontos_poli_int.pop()
                                pontos_poli_int.append(ordem_errada1)
                                pontos_poli_int.append(ordem_errada2)
                                pontos_poli_sinal.pop()
                                pontos_poli_sinal.append(tipo_vertice)
                                pontos_poli_sinal.append(TipoVertice.INT_SAIDA)
                                intersecoes.pop()
                                intersecoes.pop()
                                intersecoes.append(ordem_errada1)
                                intersecoes.append(ordem_errada2)
                                intersecoes_sinal.pop()
                                intersecoes_sinal.append(tipo_vertice)
                                intersecoes_sinal.append(TipoVertice.INT_SAIDA)
                        else:
                            pontos_poli_sinal.append(TipoVertice.INT_ENTRADA)
                            intersecoes_sinal.append(TipoVertice.INT_ENTRADA)
                    qtd_vertices_entrada += 1

        for i in range(len(poli_win.pontos)):
            pontos_win_int.append(poli_win.pontos[i])
            pontos_win_sinal.append(TipoVertice.POLIGONO)
            seg_win = Segmento(poli_win.pontos[i], poli_win.pontos[(i + 1) % len(poli_win.pontos)])
            for j in range(len(intersecoes)):
                if posicao_ponto(seg_win, intersecoes[j]) == PosPonto.SOBRE:
                    pontos_win_int.append(intersecoes[j])
                    pontos_win_sinal.append(intersecoes_sinal[j])

        if qtd_vertices_entrada == 0:
            novos_poligonos.append(Poligono(poligono.pontos, poligono.cor))
            if dentro_poli(poli_win, poligono.pontos[0]) == Pos.DENTRO:
                novos_poligonos[0].visivel = True # totalmente dentro
            else:
                novos_poligonos[0].visivel = False # totalmente dentro
        else:
            cont = 0
            while True:
                indice_poli = 0
                indice_win = 0
                pontos_novo_poli = []
                olhando_poli = True
                if qtd_vertices_entrada == 0:
                    break
                for i in range(len(pontos_poli_int)):
                    if pontos_poli_sinal[i] == TipoVertice.INT_ENTRADA and pontos_poli_usado[i] == False:
                        indice_poli = i
                        pontos_novo_poli.append(pontos_poli_int[indice_poli])
                        pontos_poli_usado[indice_poli] = True
                        indice_poli = i + 1
                        qtd_vertices_entrada -= 1
                while True:
                    cont += 1
                    assert cont < 100
                    if olhando_poli:
                        if pontos_poli_int[indice_poli % len(pontos_poli_int)] == pontos_novo_poli[0]:
                            break  # caso que volta para o msm ponto inicial fechando o poligono
                        elif pontos_poli_sinal[indice_poli % len(pontos_poli_sinal)] == TipoVertice.INT_SAIDA:
                            olhando_poli = False
                            for i in range(len(pontos_win_int)):
                                if pontos_win_int[i].x == pontos_poli_int[indice_poli % len(pontos_poli_int)].x and pontos_win_int[i].y == pontos_poli_int[indice_poli % len(pontos_poli_int)].y:
                                    indice_win = i + 1
                                    break
                            pontos_novo_poli.append(pontos_poli_int[indice_poli % len(pontos_poli_int)])
                            pontos_poli_usado[indice_poli % len(pontos_poli_int)] = True
                        else:
                            pontos_novo_poli.append(pontos_poli_int[indice_poli % len(pontos_poli_int)])
                            pontos_poli_usado[indice_poli % len(pontos_poli_int)] = True
                        indice_poli += 1
                    else:
                        if pontos_win_sinal[indice_win % len(pontos_poli_int)] == TipoVertice.INT_ENTRADA:
                            olhando_poli = True
                            for i in range(len(pontos_poli_int)):
                                if pontos_poli_int[i].x == pontos_win_int[indice_win % len(pontos_win_int)].x and pontos_poli_int[i].y == pontos_win_int[indice_win % len(pontos_win_int)].y:
                                    indice_poli = i
                                    break
                        else:
                            pontos_novo_poli.append(pontos_win_int[indice_win % len(pontos_poli_sinal)])
                        indice_win += 1
                break
            novos_poligonos.append(Poligono(pontos_novo_poli, poligono.cor))
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


def intersecta(segA: Segmento, segB: Segmento) -> bool:
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


def x_min_poli(poli: Poligono):
    xMin = poli.pontos[0].x
    for i in range(len(poli.pontos)):
        if poli.pontos[i].x < xMin:
            xMin = poli.pontos[i].x
    return xMin


def ponto_no_intervalo(segA: Segmento, c: Ponto) -> bool:
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
        elif intersecta(segPoli,
                        segAlvo):  # 2º caso, quando ao segmento alvo intersecta o segmento do poligono e ponto do segmento do poligono com o menor y nao esta sobre o segmento alvo
            if not ((posicao_ponto(segAlvo, segPoli.p1) == PosPonto.SOBRE and y_min_segmento(
                    segPoli) == segPoli.p1.y) or (
                            posicao_ponto(segAlvo, segPoli.p2) == PosPonto.SOBRE and y_min_segmento(
                            segPoli) == segPoli.p2.y)):
                qtdInterseccoes += 1
    if qtdInterseccoes % 2 == 0:
        return Pos.FORA
    else:
        return Pos.DENTRO
