import os
import string
import tkinter as tk
import xml.etree.ElementTree as ET
from Formas import *
from Clipping import *
from tkinter import filedialog, simpledialog, messagebox

def ler_window(arquivo) -> Recorte:
    root = ET.parse(arquivo).getroot()
    window = root.find("window")
    if window is None:
        return None
    wmin = window.find("wmin")
    wmax = window.find("wmax")
    return Recorte(Ponto(float(wmin.attrib["x"]), float(wmin.attrib["y"])),
                   Ponto(float(wmax.attrib["x"]), float(wmax.attrib["y"])))


def ler_view_port(arquivo) -> Recorte:
    root = ET.parse(arquivo).getroot()
    viewport = root.find("viewport")
    if viewport is None:
        return None
    vpmin = viewport.find("vpmin")
    vpmax = viewport.find("vpmax")
    return Recorte(Ponto(float(vpmin.attrib["x"]), float(vpmin.attrib["y"])),
                   Ponto(float(vpmax.attrib["x"]), float(vpmax.attrib["y"])))


def ler_formas(arquivo) -> list[Forma]:
    root = ET.parse(arquivo).getroot()
    formas = []
    for child in root:
        match child.tag:
            case "ponto":
                formas.append(Ponto(float(child.attrib["x"]), float(child.attrib["y"]), child.attrib["cor"]))
            case "reta":
                cor = child.attrib["cor"]
                pontos: list[Ponto] = []
                for ponto in child:
                    pontos.append(Ponto(float(ponto.attrib["x"]), float(ponto.attrib["y"])))
                formas.append(Reta(pontos[0], pontos[1], cor))
            case "poligono":
                cor = child.attrib["cor"]
                pontos: list[Ponto] = []
                for ponto in child:
                    pontos.append(Ponto(float(ponto.attrib["x"]), float(ponto.attrib["y"])))
                formas.append(Poligono(pontos, cor))
    return formas



class Visualizador:
    window: Recorte
    viewport: Recorte
    window_minimapa: Recorte
    viewport_minimapa: Recorte
    formas: list[Forma]
    nome_arquivo: string
    algClippingReta: string = "Cohen"

    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Objetos 2D")

        # Configurar o menu
        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir", command=self.abrir_arquivo)
        file_menu.add_command(label="Salvar", command=self.salvar_dados)

        # Frame principal para conter canvas e minimapa
        self.frame_principal = tk.Frame(root)
        self.frame_principal.pack(fill="both", expand=True)

        # Canvas da Viewport principal
        self.canvas = tk.Canvas(self.frame_principal, width=800, height=600, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Canvas da Minimap principal
        self.canvas_minimap = tk.Canvas(self.frame_principal, width=160, height=120, bg="lightgrey")
        self.canvas_minimap.pack(side="right", padx=10, pady=10)
        self.viewport_minimapa = Recorte(Ponto(0, 0), Ponto(160, 120))

        self.root.bind("<Up>", lambda event: self.mover_window(0, 1))
        self.root.bind("<Down>", lambda event: self.mover_window(0, -1))
        self.root.bind("<Left>", lambda event: self.mover_window(-1, 0))
        self.root.bind("<Right>", lambda event: self.mover_window(1, 0))

        self.root.bind("<Control-z>", lambda event: self.zoom_window(1.1)) # fator de scala + 10%
        self.root.bind("<Control-x>", lambda event: self.zoom_window(0.9)) # fator de scala - 10%

    def mover_window(self, deslocamento_x: float, deslocamento_y: float):
        transalacao(self.window.min, deslocamento_x, deslocamento_y)
        transalacao(self.window.max, deslocamento_x, deslocamento_y)
        self.desenhar_viewport()
        self.desenhar_minimapa()

    def zoom_window(self, fator_escala: float):
        ponto_medio_window = get_ponto_medio([self.window.min, self.window.max])
        transalacao(self.window.min, -ponto_medio_window.x, -ponto_medio_window.y)
        transalacao(self.window.max, -ponto_medio_window.x, -ponto_medio_window.y)

        escala(self.window.min, fator_escala)
        escala(self.window.max, fator_escala)

        transalacao(self.window.min, +ponto_medio_window.x, +ponto_medio_window.y)
        transalacao(self.window.max, +ponto_medio_window.x, +ponto_medio_window.y)

        self.desenhar_viewport()
        self.desenhar_minimapa()

    def abrir_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(
            initialdir=os.getcwd(),  # Diretório atual
            title="Selecione um arquivo XML",
            filetypes=(("Arquivos XML", "*.xml"), ("Todos os arquivos", "*.*"))
        )

        #Caixa de seleção do clipping de reta
        opcao = simpledialog.askstring(
            "Escolha de Opção",
            "Algoritmo de clipping de reta:\n1. Cohen-Sutherland\n2. Liang-Barsky"
        )
        if opcao == "1":
            messagebox.showinfo("Algoritmo Selecionado", "Cohen-Sutherland")
            self.algClippingReta = "Cohen"
        elif opcao == "2":
            messagebox.showinfo("Algoritmo Selecionado", "Liang-Barsky")
            self.algClippingReta = "Liang"
        else:
            messagebox.showwarning("Aviso", "Nenhuma opção válida selecionada.\nPor padrão o algoritmo utilizado sera o de Cohen-Sutherland")

        self.nome_arquivo = caminho_arquivo
        if caminho_arquivo:
            self.carregar_arquivo(caminho_arquivo)
        pass

    def carregar_arquivo(self, caminho):
        self.window = ler_window(caminho)
        self.viewport = ler_view_port(caminho)
        self.formas = ler_formas(caminho)
        self.window_minimapa = self.criar_recorte_window_minimapa(escala=1)
        self.desenhar_minimapa()
        self.desenhar_viewport()
        pass

    def criar_recorte_window_minimapa(self, escala) -> Recorte:
        p_min = Ponto((self.window.min.x - self.window.get_largura() * escala),
                      (self.window.min.y - self.window.get_altura() * escala))
        p_max = Ponto((self.window.max.x + self.window.get_largura() * escala),
                      (self.window.max.y + self.window.get_altura() * escala))
        return Recorte(p_min, p_max)

    def criar_caixa_minimapa(self) -> Poligono:
        p1 = Ponto(self.window.min.x, self.window.min.y)
        p2 = Ponto(self.window.min.x + self.window.get_largura(), self.window.min.y)
        p3 = Ponto(self.window.max.x, self.window.max.y)
        p4 = Ponto(self.window.min.x, self.window.min.y + self.window.get_altura())
        return Poligono([p1, p2, p3, p4], cor="gray")

    def desenhar_viewport(self):
        if hasattr(self, 'canvas'):
            self.canvas.destroy()

        self.canvas = tk.Canvas(self.frame_principal, width=self.viewport.get_largura(),
                                height=self.viewport.get_altura(), bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        for forma in self.formas:
            if isinstance(forma, Ponto):
                ClippingPonto.ponto_contido_recorte(forma, self.window)
                if forma.visivel:
                    forma.desenhar(self.canvas, self.viewport, self.window)
                else:
                    print("Ponto não desenhado")
            else:
                forma.desenhar(self.canvas, self.viewport, self.window)
        pass

    def desenhar_minimapa(self):
        if hasattr(self, 'canvas_minimap'):
            self.canvas_minimap.destroy()

        self.canvas_minimap = tk.Canvas(self.frame_principal, width=160, height=120, bg="lightgrey")
        self.canvas_minimap.pack(side="right", padx=10, pady=10)

        for forma in self.formas:
            forma.desenhar(self.canvas_minimap, self.viewport_minimapa, self.window_minimapa)
        pass
        caixa_minimapa = self.criar_caixa_minimapa()
        caixa_minimapa.desenhar(self.canvas_minimap, self.viewport_minimapa, self.window_minimapa)

    def salvar_dados(self):
        if self.nome_arquivo is None:
            return None
        tree = ET.parse(self.nome_arquivo)
        root = tree.getroot()
        window = root.find("window")
        if window is None:
            return None
        wmin = window.find("wmin")
        wmin.set("x", f"{self.window.min.x}")
        wmin.set("y", f"{self.window.min.y}")
        wmax = window.find("wmax")
        wmax.set("x", f"{self.window.max.x}")
        wmax.set("y", f"{self.window.max.y}")
        tree.write('output.xml')

def transalacao(ponto: Ponto, deslocamento_x: float, deslocamento_y: float):
    ponto.x += deslocamento_x
    ponto.y += deslocamento_y

def escala(ponto: Ponto, fator_escala: float):
    ponto.x *= fator_escala
    ponto.y *= fator_escala

def get_ponto_medio(pontos: list[Ponto]) -> Ponto:
    if len(pontos) < 1:
        return Ponto(0, 0)
    soma_x = 0
    soma_y = 0
    for ponto in pontos:
        soma_x += ponto.x
        soma_y += ponto.y
    return Ponto(soma_x/len(pontos), soma_y/len(pontos))

if __name__ == '__main__':
    root = tk.Tk()
    app = Visualizador(root)
    root.mainloop()