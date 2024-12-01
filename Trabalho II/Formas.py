import string
from abc import ABC, abstractmethod

COORDENADAS_ORIGINAIS = "coord_original"
COORDENADAS_ALTERADAS = "coord_alterada"


class Forma(ABC):
    def __init__(self, visibilidade: bool):
        self.visivel = visibilidade

    @abstractmethod
    def desenhar(self, canvas, viewport, window, coordenadas): pass


class Ponto(Forma):
    def __init__(self, x: float, y: float, cor: string = "black"):
        super().__init__(False)
        self.cor = cor
        self.x = x
        self.y = y
        self.x_alterado = x
        self.y_alterado = y

    def desenhar(self, canvas, viewport, window, coordenadas: string):
        if coordenadas == COORDENADAS_ORIGINAIS:
            aux = transformada_viewport(Ponto(self.x, self.y), window, viewport)
            canvas.create_oval(aux.x - 1, aux.y - 1, aux.x + 1, aux.y + 1, fill=self.cor)
        elif coordenadas == COORDENADAS_ALTERADAS:
            if self.visivel:
                aux = transformada_viewport(Ponto(self.x_alterado, self.y_alterado), window, viewport)
                canvas.create_oval(aux.x - 1, aux.y - 1, aux.x + 1, aux.y + 1, fill=self.cor)
            else:
                print("Ponto não desenhado")
        else:
            print("Erro")


class Reta(Forma):
    def __init__(self, ponto1: Ponto, ponto2: Ponto, cor: string = "blue"):
        super().__init__(True)
        self.cor = cor
        self.p1 = ponto1
        self.p2 = ponto2

    def desenhar(self, canvas, viewport, window, coordenadas):
        if coordenadas == COORDENADAS_ORIGINAIS:
            aux_p1 = transformada_viewport(self.p1, window, viewport)
            aux_p2 = transformada_viewport(self.p2, window, viewport)
            canvas.create_line(aux_p1.x, aux_p1.y, aux_p2.x, aux_p2.y, fill=self.cor)
        elif coordenadas == COORDENADAS_ALTERADAS:
            if self.visivel:
                aux_p1 = transformada_viewport(Ponto(self.p1.x_alterado, self.p1.y_alterado), window, viewport)
                aux_p2 = transformada_viewport(Ponto(self.p2.x_alterado, self.p2.y_alterado), window, viewport)
                canvas.create_line(aux_p1.x, aux_p1.y, aux_p2.x, aux_p2.y, fill=self.cor)
            else:
                print("Reta não desenhada")
        else:
            print("Erro.")


class Poligono(Forma):
    def __init__(self, pontos: list[Ponto], cor: string = "red"):
        super().__init__(True)
        self.cor = cor
        self.pontos = pontos

    def desenhar(self, canvas, viewport, window, coordenadas):
        coords = []
        if coordenadas == COORDENADAS_ORIGINAIS:
            for ponto in self.pontos:
                aux_ponto = transformada_viewport(ponto, window, viewport)
                coords.append(aux_ponto.x)
                coords.append(aux_ponto.y)
            canvas.create_polygon(coords, fill="", outline=self.cor, width=1)
        elif coordenadas == COORDENADAS_ALTERADAS:
            if self.visivel:
                for ponto in self.pontos:
                    aux_ponto = transformada_viewport(Ponto(ponto.x_alterado, ponto.y_alterado), window, viewport)
                    coords.append(aux_ponto.x)
                    coords.append(aux_ponto.y)
                canvas.create_polygon(coords, fill="", outline=self.cor, width=1)
            else:
                print("Poligono não desenhado")
        else:
            print("Erro")


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
