import math
import string
from abc import ABC, abstractmethod

import numpy as np


class Forma(ABC):
    def __init__(self, visibilidade: bool):
        self.visivel = visibilidade

    @abstractmethod
    def desenhar(self, canvas, viewport, window, angulo): pass


class Ponto(Forma):
    def __init__(self, x: float, y: float, cor: string = "black"):
        super().__init__(False)
        self.cor = cor
        self.x = x
        self.y = y

    def desenhar(self, canvas, viewport, window, angulo):
        novo_ponto = transformada(Ponto(self.x, self.y), window, viewport, angulo)
        aux = transformada_viewport(Ponto(float(novo_ponto[0, 0]), float(novo_ponto[1, 0])), viewport)
        canvas.create_oval(aux.x - 1, aux.y - 1, aux.x + 1, aux.y + 1, fill=self.cor)


class Segmento(Forma):
    def __init__(self, ponto1: Ponto, ponto2: Ponto, cor: string = "blue"):
        super().__init__(True)
        self.cor = cor
        self.p1 = ponto1
        self.p2 = ponto2

    def desenhar(self, canvas, viewport, window, angulo):
        novo_p1 = transformada(self.p1, window, viewport, angulo)
        novo_p2 = transformada(self.p2, window, viewport, angulo)
        aux_p1 = transformada_viewport(Ponto(float(novo_p1[0, 0]), float(novo_p1[1, 0])), viewport)
        aux_p2 = transformada_viewport(Ponto(float(novo_p2[0, 0]), float(novo_p2[1, 0])), viewport)
        canvas.create_line(aux_p1.x, aux_p1.y, aux_p2.x, aux_p2.y, fill=self.cor)


class Poligono(Forma):
    def __init__(self, pontos: list[Ponto], cor: string = "red"):
        super().__init__(True)
        self.cor = cor
        self.pontos = pontos

    def desenhar(self, canvas, viewport, window, angulo):
        coords = []
        for ponto in self.pontos:
            novo_ponto = transformada(ponto, window, viewport, angulo)
            aux_ponto = transformada_viewport(Ponto(float(novo_ponto[0, 0]), float(novo_ponto[1, 0])), viewport)
            coords.append(aux_ponto.x)
            coords.append(aux_ponto.y)
        canvas.create_polygon(coords, fill="", outline=self.cor, width=1)


class Recorte:
    def __init__(self, ponto_min: Ponto, ponto_max: Ponto):
        self.min = ponto_min
        self.max = ponto_max

    def get_altura(self):
        return self.max.y - self.min.y

    def get_largura(self):
        return self.max.x - self.min.x


def transformada(ponto: Ponto, window: Recorte, viewport: Recorte, angulo: int):
    matriz_transformada = get_matriz_tranformacoes(window, math.radians(angulo))
    return matriz_transformada @ np.array([[ponto.x], [ponto.y], [1]])


def transformada_viewport(ponto: Ponto, viewport):
    x_viewport = ((ponto.x + 1) / (2)) * (
            viewport.max.x - viewport.min.x)
    y_viewport = (1 - ((ponto.y + 1) / (2))) * (
            viewport.max.y - viewport.min.y)
    return Ponto(x_viewport, y_viewport)


def get_ponto_medio(pontos: list[Ponto]) -> Ponto:
    if len(pontos) < 1:
        return Ponto(0, 0)
    soma_x = 0
    soma_y = 0
    for ponto in pontos:
        soma_x += ponto.x
        soma_y += ponto.y
    return Ponto(soma_x / len(pontos), soma_y / len(pontos))


def get_matriz_tranformacoes(window: Recorte, angulo_rad: float):
    largura = window.get_largura()
    altura = window.get_altura()

    centro_window = get_ponto_medio([window.min, window.max])

    escalonamento = np.array([
        [1 / (largura / 2), 0, 0],
        [0, 1 / (altura / 2), 0],
        [0, 0, 1]
    ])

    rotacao = np.array([
        [math.cos(angulo_rad), -math.sin(angulo_rad), 0],
        [math.sin(angulo_rad), math.cos(angulo_rad), 0],
        [0, 0, 1]
    ])

    translacao = np.array([
        [1, 0, -centro_window.x],
        [0, 1, -centro_window.y],
        [0, 0, 1]
    ])

    return escalonamento @ rotacao @ translacao


def transalacao(ponto: Ponto, deslocamento_x: float, deslocamento_y: float):
    ponto.x += deslocamento_x
    ponto.y += deslocamento_y


def escala(ponto: Ponto, fator_escala: float):
    ponto.x *= fator_escala
    ponto.y *= fator_escala
