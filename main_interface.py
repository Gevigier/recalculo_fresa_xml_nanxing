# |=================================================================|
# |            PROGRAMA MANIPULADOR DE PLANO DE CORTE               |
# |                       PARA CNC NANXING                          |
# |                    (COMPENSADOR DE FRESA)                       |
# |                                                                 |
# |                                 Autor: Marcos Gabriel Gevigier  |
# |                                         github.com/Gevigier     |
# |                                                                 |
# | VERSÃO: 0.3.3                                                   |
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
        '''[EN] Inicialization \n
        [PT-BR] Inicialização'''
        show_interface = self.main_interface()

    def selectXML(self, *args):
        '''Seleciona o arquivo .xml do plano de corte e exibe a espessura atual da fresa'''

        self.filename = askopenfilename()
        self.xmlName = Path(self.filename).name

        try:
            self.toolDiameter.set(float(recalc.getToolDiameter(self.filename)))
            self.selected_file.set('PLANO:')
            self.xml_path.set(str(self.filename))
        except:
            pass
    
    def recalculate(self, *args):
        try:
            newTool = float(self.newDiameter.get())

            viability = recalc.identifyViability(newTool)

            if viability == 'Valid':
                    saveLocation = asksaveasfilename(initialfile = self.xmlName, initialdir = "./",title = "Selecione onde deseja salvar",filetypes = (("Arquivos .xml","*.xml"),("Todos os arquivos","*.*")))

                    recalc.manipulate(newTool, saveLocation)
                    messagebox.showinfo(message='CONCLUÍDO. O PLANO FOI AJUSTADO CORRETAMENTE')

            elif viability == 'Invalid - Bigger Tool Diameter':
                messagebox.showinfo(message='ERRO: A FRESA INSERIDA É MAIOR DO QUE A FRESA ATUAL DO PLANO!')

            elif viability == 'Invalid - Same Size':
                messagebox.showinfo(message='ERRO: O DIÂMETRO INSERIDO É O MESMO DO PLANO ATUAL')                  
        
        except ValueError:
            pass

    def main_interface(self):
        self.root = Tk()
        self.root.title("Compensador de Fresa - Nanxing")

        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        lowerframe = ttk.Frame(self.root, padding="3 3 12 12")
        lowerframe.grid(column=0, row=1, sticky=(N, W, E, S))

        self.root.columnconfigure(3, weight=1)
        self.root.rowconfigure(0, weight=1)

        # TEXTOS FIXOS

        ttk.Label(mainframe, text="Recálculo de Fresa para CNC Nanxing").grid(
            column=1, row=1, sticky=W)
        ttk.Label(mainframe, text="Espessura atual:").grid(
            column=1, row=3, sticky=W)
        ttk.Label(mainframe, text="Nova espessura de fresa:").grid(
            column=1, row=4, sticky=W)

        # BOTÕES

        ttk.Button(mainframe, text="Selecionar arquivo de corte", command=self.selectXML).grid(
            column=2, row=2, sticky=W)
        ttk.Button(mainframe, text="Recalcular coordenadas do plano", command=self.recalculate).grid(
            column=3, row=5, sticky=W)

        # TEXTOS VARIÁVEIS

        self.toolDiameter = StringVar()
        self.xml_path = StringVar()
        self.selected_file = StringVar()

        ttk.Label(mainframe, textvariable=self.toolDiameter).grid(column=2, row=3, sticky=(W, E))
        ttk.Label(lowerframe, textvariable=self.selected_file).grid(column=0, row=1, sticky=(W, E))
        ttk.Label(lowerframe, textvariable=self.xml_path).grid(column=1, row=1, sticky=(W, E))

        # ENTRADAS

        self.newDiameter = StringVar()
        new_toolDiameter = ttk.Entry(mainframe, width=7, textvariable=self.newDiameter)
        new_toolDiameter.grid(column=2, row=4, sticky=(W, E))

        # OUTROS

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        new_toolDiameter.focus()
        self.root.bind("<Return>", self.recalculate)

        self.root.mainloop()

if __name__ == "__main__":
    recalcInterface = recalculator_interface()