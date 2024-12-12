import math
import os
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, simpledialog, messagebox
from Clipping import *


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
                formas.append(Segmento(pontos[0], pontos[1], cor))
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
    angulo_grau: int
    caixa_minimapa: Poligono
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

        # Frame dos Botões
        self.frame_botoes = tk.Frame(root)
        self.frame_botoes.pack(side="bottom", anchor="center", pady="10")
        # Botões de Movimentação
        self.botao_cima = tk.Button(self.frame_botoes, text="🠕", command=lambda: self.mover_window(0, 1), bd=1, relief="solid", padx=3.5, bg="LightBlue")
        self.botao_cima.grid(row=0, column=1, padx=2, pady=2)
        self.botao_esquerda = tk.Button(self.frame_botoes, text="🠔", command=lambda: self.mover_window(-1, 0), bd=1, relief="solid", bg="LightBlue")
        self.botao_esquerda.grid(row=1, column=0, padx=2, pady=2)
        self.botao_direita = tk.Button(self.frame_botoes, text="➞", command=lambda: self.mover_window(1, 0), bd=1, relief="solid", bg="LightBlue")
        self.botao_direita.grid(row=1, column=2, padx=2, pady=2)
        self.botao_baixo = tk.Button(self.frame_botoes, text="🠗", command=lambda: self.mover_window(0, -1), bd=1, relief="solid", padx=3.5, bg="LightBlue")
        self.botao_baixo.grid(row=2, column=1, padx=2, pady=2)
        # Botões de Zoom
        self.bt_zoom_mais = tk.Button(self.frame_botoes, text="+", command=lambda: self.zoom_window(0.9), bd=1, relief="solid", padx=2.5, bg="LightYellow")
        self.bt_zoom_mais.grid(row=1, column=4, padx=5, pady=2)
        self.bt_zoom_menos = tk.Button(self.frame_botoes, text="-", command=lambda: self.zoom_window(1.1), bd=1, relief="solid", padx=3.5, bg="LightYellow")
        self.bt_zoom_menos.grid(row=1, column=5, padx=3, pady=2)
        # Botões de Rotação
        self.bt_rotacao_dir = tk.Button(self.frame_botoes, text="D", command=lambda: self.rotacionar_window(+10), bd=1, relief="solid", padx=3.5, bg="Salmon")
        self.bt_rotacao_dir.grid(row=1, column=7, padx=3, pady=2)
        self.bt_rotacao_esq = tk.Button(self.frame_botoes, text="E", command=lambda: self.rotacionar_window(-10), bd=1, relief="solid", padx=3.5, bg="Salmon")
        self.bt_rotacao_esq.grid(row=1, column=8, padx=3, pady=2)

        #Teclas para movimentação
        self.root.bind("<Up>", lambda event: self.mover_window(0, 1))
        self.root.bind("<Down>", lambda event: self.mover_window(0, -1))
        self.root.bind("<Left>", lambda event: self.mover_window(-1, 0))
        self.root.bind("<Right>", lambda event: self.mover_window(1, 0))
        self.root.bind("<Control-z>", lambda event: self.zoom_window(1.1))  # fator de scala + 10%
        self.root.bind("<Control-x>", lambda event: self.zoom_window(0.9))  # fator de scala - 10%
        self.angulo_grau = 0
        self.root.bind("<r>", lambda event: self.rotacionar_window(+10))
        self.root.bind("<l>", lambda event: self.rotacionar_window(-10))

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

    def rotacionar_window(self, deslocamento_grau: int):
        self.angulo_grau = (self.angulo_grau + deslocamento_grau) % 360

        self.desenhar_viewport()
        self.desenhar_minimapa()

    def abrir_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(
            initialdir=os.getcwd(),  # Diretório atual
            title="Selecione um arquivo XML",
            filetypes=(("Arquivos XML", "*.xml"), ("Todos os arquivos", "*.*"))
        )

        # Caixa de seleção do clipping de reta
        opcao = simpledialog.askstring(
            "...",
            "Algoritmo de clipping de reta:\n1. Cohen-Sutherland\n2. Liang-Barsky"
        )
        if opcao == "1":
            messagebox.showinfo("Algoritmo Selecionado", "Cohen-Sutherland")
            self.algClippingReta = "Cohen"
        elif opcao == "2":
            messagebox.showinfo("Algoritmo Selecionado", "Liang-Barsky")
            self.algClippingReta = "Liang"
        else:
            messagebox.showwarning("Aviso","Nenhuma opção válida selecionada.\nPor padrão o algoritmo utilizado sera o de Cohen-Sutherland")
            self.algClippingReta = "Cohen"

        self.nome_arquivo = caminho_arquivo
        if caminho_arquivo:
            self.carregar_arquivo(caminho_arquivo)
        pass

    def carregar_arquivo(self, caminho):
        self.window = ler_window(caminho)
        self.viewport = ler_view_port(caminho)
        self.formas = ler_formas(caminho)
        self.window_minimapa = self.criar_recorte_window_minimapa(escala=1)
        self.caixa_minimapa = self.criar_caixa_minimapa()
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
            if isinstance(forma, Poligono):
                WeilerAtherton.clipping_poligono(forma, self.window)
            forma.desenhar(self.canvas, self.viewport, self.window, self.angulo_grau)
        pass

    def desenhar_minimapa(self):
        if hasattr(self, 'canvas_minimap'):
            self.canvas_minimap.destroy()

        self.canvas_minimap = tk.Canvas(self.frame_principal, width=160, height=120, bg="lightgrey")
        self.canvas_minimap.pack(side="right", padx=10, pady=10)

        for forma in self.formas:
            forma.desenhar(self.canvas_minimap, self.viewport_minimapa, self.window_minimapa, 0)
        pass

        self.caixa_minimapa = self.criar_caixa_minimapa()
        self.caixa_minimapa.desenhar(self.canvas_minimap, self.viewport_minimapa, self.window_minimapa, self.angulo_grau)

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

if __name__ == '__main__':
    root = tk.Tk()
    app = Visualizador(root)
    root.mainloop()
