# PROGRAMA RECALCULADOR DE CORTE -> COMPENSADOR DE FRESA
# Autor: Marcos Gabriel Gevigier

# Manipulador/Interpretador XML disponível na biblioteca padrão
import xml.etree.ElementTree as ET

class RecaculadorDeFresa:

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
        '''[EN] Checks if the new diameter is smaller than the previous diameter. Return True or False \n
        [PT-BR] Verifica se o novo diâmetro é menor que o diâmetro original do plano. Retorna True ou False'''

        if (newDiameter > self.toolDiameter):
            return False
        else:
            return True

    def manipulate(self, calcDiameter, savePath):

        # Passo 2: TIRAR A DIFERENÇA ENTRE OS DIÂMETROS E DIVIDIR POR DOIS
        compDiameter = (self.toolDiameter - calcDiameter) / 2

        # Passo 3: REESCREVER, NO DOCUMENTO, O NOVO VALOR DE FRESA
        for Pattern in self.root.iter("Pattern"):
            Pattern.set("ToolDiameter", str(calcDiameter))

        # Passo 4: MODIFICAR A COORDENADA DOS PONTOS CONFORME NECESSÁRIO
        # Estabelece um laço de iteração que vasculha cada tag Lineament no documento
        for Lineament in self.root.iter("Lineament"):

            # Atualiza as coordenas X e Y de Lienament com as mesmas regras do Point de Index 1
            New_X = float(Lineament.get("X")) + compDiameter
            New_Y = float(Lineament.get("Y")) + compDiameter

            # Reescreve no documento as novas coordenadas geradas
            Lineament.set("X", f'{New_X:.3f}')
            Lineament.set("Y", f'{New_Y:.3f}')

            # Estabelece um laço de repetição para vasculhar cada tag Point no documento
            for point in Lineament.iter("Point"):
                # Atribui o valor de Index da tag Point à variável ordemIndex
                indexOrder = int(point.get("Index"))

                # Retira as coordenadas X e Y de Point
                xCoord = float(point.get("X"))
                yCoord = float(point.get("Y"))

                # Compensa as coordenadas X e Y de cada Point se baseando no Index (informação atribuída à ordemIndex)
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

                # Reescreve no documento as novas coordenadas geradas para cada Point
                point.set("X", f'{New_X:.3f}')
                point.set("Y", f'{New_Y:.3f}')

            # PASSO 5: ALTERAR TOOLPOINTLIST
            # Identifica o ToolPointList dentro de cada Pattern (iteração anterior) e separa cada ponto por ";"
            cutInfos = Lineament.find("CutInfos")
            toolPointList = cutInfos.get("ToolPointList")
            ptLS = toolPointList.split(";")

            # Cria uma lista vazia para poder reestruturar o ToolPointList (reverter a separação de ";")
            pointListReconstruct = []

            # Itera dentro dos pontos (já separados por ";")
            for toolPoint in ptLS:

                # Separa cada informação do ponto (separados por ",") e atribui as informações a variáveis distintas
                tl_X, tl_Y, cifrao, hashtag = toolPoint.split(",")

                # Verifica qual o ponto "$" e o modifica, conforme o necessário, observando qual o respectivo "#"
                match(cifrao):
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

                # Reestrutura o ponto em lista
                toolPoint = [f'{newTL_X:.3f}',
                             f'{newTL_Y:.3f}', cifrao, hashtag]

                # Transforma o ponto em string (reinserindo a ",")
                pointListReconstruct.append(','.join(toolPoint))

            # Reestrutura (reverte a separação de ";") e define os novos ToolPointList no documento
            cutInfos.set("ToolPointList", ';'.join(pointListReconstruct))

        # Insere uma nota de alteração
        notaAlteracao = ET.Comment("ALERTA!! Este plano teve sua fresa alterada apos sua otimizacao. Sua fresa original era de {0}".format(self.toolDiameter))
        self.root.insert(0, notaAlteracao)

        # Escreve um novo arquivo como output
        self.tree.write(savePath)


if __name__ == "__main__":

    recalculador = RecaculadorDeFresa()
    # recalculador = RecaculadorDeFresa("./XML PARA TESTE/4124^PAINEL EDITAVEL^22641^MDP^BP^BRAN^15MM.XML", "10")
        # Estrutura para se implementar:
        # Input, Espessura da Nova Fresa, Output 