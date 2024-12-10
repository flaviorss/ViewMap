import string
from abc import ABC, abstractmethod

class Forma(ABC):
    def __init__(self, visibilidade: bool):
        self.visivel = visibilidade

    @abstractmethod
    def desenhar(self, canvas, viewport, window): pass

class Ponto(Forma):
    def __init__(self, x: float, y: float, cor: string = "black"):
        super().__init__(False)
        self.cor = cor
        self.x = x
        self.y = y

    def desenhar(self, canvas, viewport, window):
        aux = transformada_viewport(Ponto(self.x, self.y), window, viewport)
        canvas.create_oval(aux.x - 1, aux.y - 1, aux.x + 1, aux.y + 1, fill=self.cor)


class Segmento(Forma):
    def __init__(self, ponto1: Ponto, ponto2: Ponto, cor: string = "blue"):
        super().__init__(True)
        self.cor = cor
        self.p1 = ponto1
        self.p2 = ponto2

    def desenhar(self, canvas, viewport, window):
        aux_p1 = transformada_viewport(self.p1, window, viewport)
        aux_p2 = transformada_viewport(self.p2, window, viewport)
        canvas.create_line(aux_p1.x, aux_p1.y, aux_p2.x, aux_p2.y, fill=self.cor)

class Poligono(Forma):
    def __init__(self, pontos: list[Ponto], cor: string = "red"):
        super().__init__(True)
        self.cor = cor
        self.pontos = pontos

    def desenhar(self, canvas, viewport, window):
        coords = []
        for ponto in self.pontos:
            aux_ponto = transformada_viewport(ponto, window, viewport)
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


def transformada_viewport(ponto: Ponto, window, viewport):
    x_viewport = ((ponto.x - window.min.x) / (window.max.x - window.min.x)) * (
            viewport.max.x - viewport.min.x)
    y_viewport = (1 - ((ponto.y - window.min.y) / (window.max.y - window.min.y))) * (
            viewport.max.y - viewport.min.y)
    return Ponto(x_viewport, y_viewport)
