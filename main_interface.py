# |=================================================================|
# |            PROGRAMA MANIPULADOR DE PLANO DE CORTE               |
# |                       PARA CNC NANXING                          |
# |                    (COMPENSADOR DE FRESA)                       |
# |                                                                 |
# |                       -= INTERFACE =-                           |
# |                                                                 |
# |                                 Autor: Marcos Gabriel Gevigier  |
# |                                         github.com/Gevigier     |
# |                                                                 |
# | VERSÃO: 0.3.5                                                   |
# |=================================================================|


# [EN] Libs:
# [PT-BR] Bibliotecas:
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox

from pathlib import Path

# [EN] Other code:
# [PT-BR] Outro código:
from toolRecalculator import toolDiameterCompensator


recalc = toolDiameterCompensator()


class recalculator_interface:

    def __init__(self):
        '''[EN] Class that generates a tkinter window that interact with the user. Asks a cut layout in .xml to modify it, asks too for a new tool diameter and a save location for the resulting file \n
        [PT-BR] Classe que gera uma tela em tkinter que interagem com o usuário. Solicita um plano de corte em .xml para modificar, também solicita um novo tamanho de fresa e um local para se se salvar o arquivo modificado'''
        
        show_interface = self.main_interface()

    def selectXML(self, *args):
        '''[EN] Asks to select a cut layout in .xml and shows the tool diameter of the layout and the it's path \n
        [PT-R] Solicita a selação de um arquivo .xml de plano de corte, exibe a espessura atual da fresa e seu caminho'''

        self.filepath = askopenfilename()
        self.xmlName = Path(self.filepath).name

        try:
            self.toolDiameter.set(float(recalc.getToolDiameter(self.filepath)))
            self.selected_file_text.set('PLANO: ')
            self.xml_path.set(str(self.filepath))
        except:
            pass
    
    def recalculate(self, *args):
        '''[EN] Verifies the viaility of changing the tool diamemter and, if positive, asks  a save path and execute the method responsible to modify the .xml \n
        [PT-BR] Verifica a possibilidade de se trocar o tamanho da fresa e, caso positivo, solicita um local para salvar o arquivo e executa a função responsável por modificar o .xml'''

        try:
            newTool = float(self.newDiameter.get())

            viability = recalc.identifyViability(newTool)

            if viability == 'Valid':
                    saveLocation = asksaveasfilename(initialfile = self.xmlName, initialdir = "./",title = "Selecione onde deseja salvar",filetypes = (("Arquivos .xml","*.xml"),("Todos os arquivos","*.*")))

                    if saveLocation:
                        recalc.manipulate(newTool, saveLocation)
                        messagebox.showinfo(message='CONCLUÍDO. O PLANO FOI AJUSTADO CORRETAMENTE')
                    else:
                        messagebox.showinfo(message='ERRO: HOUVE UM ERRO DESCONHECIDO')

            elif viability == 'Invalid - Bigger Tool Diameter':
                messagebox.showinfo(message='ERRO: A FRESA INSERIDA É MAIOR DO QUE A FRESA ATUAL DO PLANO!')
            elif viability == 'Invalid - Same Size':
                messagebox.showinfo(message='ERRO: O DIÂMETRO INSERIDO É O MESMO DO PLANO ATUAL')                  
        
        except ValueError:
            pass

    def main_interface(self):
        '''[EN] Creates the main window that interacts with the user \n
        [PT-BR] Gera a janela principal que interage com o usuário'''

        # [EN] Frames disposition and content config
        # [PT-BR] Disposição dos quadros e configuração do conteúdo
        self.root = Tk()
        self.root.title("Compensador de Fresa - Nanxing")
        self.root.resizable(False,False)

        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        lowerframe = ttk.Frame(self.root, padding="3 3 12 12")
        lowerframe.grid(column=0, row=1, sticky=(N, W, E, S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # [EN] Fixed texts
        # [PT-BR] Textos fixos
        ttk.Label(mainframe, text="Recálculo de Fresa para CNC Nanxing").grid(
            column=1, row=1, sticky=W)
        ttk.Label(mainframe, text="Espessura atual:").grid(
            column=1, row=3, sticky=W)
        ttk.Label(mainframe, text="Nova espessura de fresa:").grid(
            column=1, row=4, sticky=W)

        # [EN] Buttons
        # [PT-BR] Botões
        ttk.Button(mainframe, text="Selecionar arquivo de corte", command=self.selectXML).grid(
            column=2, row=2, sticky=W)
        ttk.Button(mainframe, text="Recalcular coordenadas do plano", command=self.recalculate).grid(
            column=3, row=5, sticky=W)

        # [EN] Changeable texts
        # [PT-BR] Textos alteráveis
        self.toolDiameter = StringVar()
        self.xml_path = StringVar()
        self.selected_file_text = StringVar()

        ttk.Label(mainframe, textvariable=self.toolDiameter).grid(column=2, row=3, sticky=(W, E))
        ttk.Label(lowerframe, textvariable=self.selected_file_text).grid(column=0, row=1, sticky=(W, E), )
        ttk.Label(lowerframe, textvariable=self.xml_path).grid(column=1, row=1, sticky=(W, E))

        # [EN] User's entry
        # [PT-BR] Entradas de usuário
        self.newDiameter = StringVar()
        new_toolDiameter = ttk.Entry(mainframe, width=7, textvariable=self.newDiameter)
        new_toolDiameter.grid(column=2, row=4, sticky=(W, E))

        # [EN] Widgets and windows config
        # [PT-BR] Configurações de widgetes e janela 
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        new_toolDiameter.focus()
        self.root.bind("<Return>", self.recalculate)

        self.root.mainloop()

if __name__ == "__main__":
    recalcInterface = recalculator_interface()