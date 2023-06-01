# PROGRAMA RECALCULADOR DE CORTE -> COMPENSADOR DE FRESA
# Autor: Marcos Gabriel Gevigier

# Manipulador/Interpretador XML disponível na biblioteca padrão
import xml.etree.ElementTree as ET

from pathlib import Path
from pathlib import PurePath

class toolDiameterCompensator:

    def generateElementTree(self, xmlPath):
        '''[EN] Creates an element tree by the argument "xmlPath" \n
        [PT-BR] Gera a árvore de elementos por meio do argumento "xmlPath"'''

        self.tree = ET.parse(xmlPath)
        self.root = self.tree.getroot()

    def getToolDiameter(self, path):
        '''[EN] Call "generateElementTree" to get the tool diameter from the .xml \n
        [PT-BR] Invoca "generateElementeTree" para retirar o diâmetro da fresa contido no .xml'''

        self.generateElementTree(path)

        self.firstPattern = self.root.find("Patterns/Pattern")
        self.toolDiameter = float(self.firstPattern.get("ToolDiameter"))

        return(self.toolDiameter)

    def identifyViability(self, newDiameter):
        '''[EN] Checks if the new diameter is smaller than the previous diameter and different than zero. Returns a string: "Valid" or "Invalid - Bigger Tool Diameter" or "Invalid - Same Size" \n
        [PT-BR] Verifica se o novo diâmetro é menor que o diâmetro original do plano e diferente de zero. Retorna uma string: "Valid" ou "Invalid - Bigger Tool Diameter" ou "Invalid - Same Size"'''

        if (newDiameter < self.toolDiameter and newDiameter != 0):
            return 'Valid'
        elif (newDiameter > self.toolDiameter):
            return 'Invalid - Bigger Tool Diameter'
        elif (newDiameter == self.toolDiameter):
            return 'Invalid - Same Size'

    def makeBackup(self, sPath):
        '''[EN] Creats a backup file with all the original coordinates in "savePath/LayoutBackup/" \n
        [PT-BR] Cria um arquivo de backup com todas as coordenadas originais em "savePath/LayoutBackup/"
        '''

        create_backup_folder = Path(Path(sPath).parent.absolute(), 'Layout Backup').mkdir(parents = True, exist_ok = True)
        backup_path = PurePath(Path(sPath).parent.absolute(), Path('Layout Backup', 'FRESA_' + str(self.toolDiameter) + '_BKP_' + Path(sPath).name))

        self.tree.write(backup_path)

    def manipulate(self, calcDiameter, savePath):
        '''[EN] Receives the new tool diameter and the save path. Gets the diference between both of diameters and recalculates the coordinates from all the pieces inside the layout, for then export the .xml into the save path \n
        [PT-BR] Recebe o novo diâmetro de fresa e o local para salvar o arquivo. Retira a diferença entre as fresas e recalcula as coordenadas de todas as peças dentro do plano, para então salvar no local passado
        '''

        self.makeBackup(savePath)

        # [EN] Gets the diference between the new diameter and the previous one
        # [PT-BR] Tira a diferença entre o novo diâmetro e o anterior
        compDiameter = (self.toolDiameter - calcDiameter) / 2

        # [EN] Writes the new diameter into the element tree
        # [PT-BR] Reescreve na element tree o novo valor da fresa
        for Pattern in self.root.iter("Pattern"):
            Pattern.set("ToolDiameter", str(calcDiameter))

        # [EN] Modifies pieces coordinates as necessary:
        # [PT-BR] Modifica as coordenadas dos pontos conforme necessário:
        
        # [EN] Iterates for every Lineament tag
        # [PT-BR] Estabelece um laço de iteração que vasculha cada tag Lineament no documento
        for Lineament in self.root.iter("Lineament"):

            # [EN] Uptades X and Y coordinates of Lineament with the same rules of Point's Index 1
            # [PT-BR] Atualiza as coordenas X e Y de Lienament com as mesmas regras do Point de Index 1
            New_X = float(Lineament.get("X")) + compDiameter
            New_Y = float(Lineament.get("Y")) + compDiameter

            Lineament.set("X", f'{New_X:.3f}')
            Lineament.set("Y", f'{New_Y:.3f}')

            # [EN] Iterates for every Point tag
            # [PT-BR] Estabelece um laço de repetição para vasculhar cada tag Point no documento
            for point in Lineament.iter("Point"):
                indexOrder = int(point.get("Index"))

                # [EN] Gets X and Y from Point
                # [PT-BR] Retira as coordenadas X e Y de Point
                xCoord = float(point.get("X"))
                yCoord = float(point.get("Y"))

                # [EN] Compensates X and Y of each Point based on the index number (indexOrder)
                # [PT-BR] Compensa as coordenadas X e Y de cada Point se baseando no Index (informação atribuída à indexOrder)
                match indexOrder:
                    case 1 | 5:
                        New_X = xCoord + compDiameter
                        New_Y = yCoord + compDiameter

                    case 2:
                        New_X = xCoord - compDiameter
                        New_Y = yCoord + compDiameter

                    case 3:
                        New_X = xCoord - compDiameter
                        New_Y = yCoord - compDiameter

                    case 4:
                        New_X = xCoord + compDiameter
                        New_Y = yCoord - compDiameter

                # [EN] Writes the new coordinates into the element tree for each Point
                # [PT-BR] Reescreve no documento as novas coordenadas geradas para cada Point
                point.set("X", f'{New_X:.3f}')
                point.set("Y", f'{New_Y:.3f}')

            # [EN] Identifies ToolPointList inside of each Pattern (previous iteration) and slipt each point by ";"
            # [PT-BR] Identifica o ToolPointList dentro de cada Pattern (iteração anterior) e separa cada ponto por ";"
            cutInfos = Lineament.find("CutInfos")
            toolPointList = cutInfos.get("ToolPointList")
            ptLS = toolPointList.split(";")

            pointListReconstruct = []

            # [EN] Iterates inside of the points (separated by ";")
            # [PT-BR] Itera dentro dos pontos (já separados por ";")
            for toolPoint in ptLS:

                # [EN] Slipt each point (separeted by ";") information into separated variables
                # [PT-BR] Separa cada informação do ponto (separados por ",") e atribui as informações a variáveis distintas
                tl_X, tl_Y, dol_sign, hashtag = toolPoint.split(",")

                # [EN] Identifies which "$" point it's and change it, as necessary, observing the respective "#"
                # [PT-BR] Verifica qual o ponto "$" e o modifica, conforme o necessário, observando qual o respectivo "#"
                match(dol_sign):
                    case "0$":
                        if hashtag == "1#":
                            newTL_X = float(tl_X) + compDiameter
                        elif hashtag == "2#":
                            newTL_X = float(tl_X) - compDiameter

                        newTL_Y = float(tl_Y) - compDiameter

                    case "1$":
                        if hashtag == "1#":
                            newTL_Y = float(tl_Y) + compDiameter
                        elif hashtag == "2#":
                            newTL_Y = float(tl_Y) - compDiameter

                        newTL_X = float(tl_X) - compDiameter

                    case "2$":
                        if hashtag == "1#":
                            newTL_X = float(tl_X) - compDiameter
                        elif hashtag == "2#":
                            newTL_X = float(tl_X) + compDiameter

                        newTL_Y = float(tl_Y) + compDiameter

                    case "3$":
                        if hashtag == "1#":
                            newTL_Y = float(tl_Y) + compDiameter
                        elif hashtag == "2#":
                            newTL_Y = float(tl_Y) - compDiameter

                        newTL_X = float(tl_X) + compDiameter

                # [EN] Restructures the point in a list
                # [PT-BR] Reestrutura o ponto em list
                toolPoint = [f'{newTL_X:.3f}',
                             f'{newTL_Y:.3f}', dol_sign, hashtag]

                pointListReconstruct.append(','.join(toolPoint))

            # [EN] Restructures and define all the new ToolPointList
            # [PT-BR] Reestrutura (reverte a separação de ";") e define os novos ToolPointList no documento
            cutInfos.set("ToolPointList", ';'.join(pointListReconstruct))

        # [EN] Insert a change note
        # [PT-BR] Insere uma nota de alteração
        notaAlteracao = ET.Comment("ALERTA!! Este plano teve sua fresa alterada apos sua otimizacao. Sua fresa original era de {0}".format(self.toolDiameter))
        self.root.insert(0, notaAlteracao)

        # [EN] Export the element tree to the save path
        # [PT-BR] Escreve um novo arquivo como output
        self.tree.write(savePath)