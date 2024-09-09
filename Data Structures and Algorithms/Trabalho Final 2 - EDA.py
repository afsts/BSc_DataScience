#Trabalho sobre a Rede de Metro de Londres
#Afonso Santos- 111431
#Afonso Lourenço- 111487

import networkx as nx
import csv
import matplotlib.pyplot as plt
import folium
import sys
sys.setrecursionlimit(3000)  # Aumenta o limite para 3000 ou outro valor adequado
import random




class LondonNetworkGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.connectionslist=[]
        self.stationslist=[]
        self.line_counter = 1
        self.graphedges={}
        self.distances = {}
        self.visited = set()
        self.previous = {}

    def stations(self, file_path):
        with open(file_path) as stations1:
            stations2 = csv.reader(stations1, delimiter=',')
            next(stations2)  

            for line in stations2:
                if not line:
                    continue  # Saltar linhas vazias
                self.stationslist.append(line)
                id=line[0]
                latitude=float(line[1])
                longitude=float(line[2])
                name=line[3]
                display_name=line[4]
                zone=line[5]
                total_lines=line[6]
                rail=line[7]
                self.graph.add_node(id,latitude=latitude,longitude=longitude,name=name,display_name=display_name,zone=zone,total_lines=total_lines,rail=rail)
            


    def connections(self, file_path):
        with open(file_path) as connections1:
            connections2 = csv.reader(connections1, delimiter=',')
            next(connections2)  
            for line in connections2:
                if not line:
                    continue  
                self.connectionslist.append(line)
                Line=line[0]
                FromStationId=line[1]
                ToStationId=line[2]
                Distance=float(line[3])
                OffPeakRunningTime=float(line[4])
                AMpeakRunningTime=float(line[5])
                InterpeakRunningtime=float(line[6])
                line_id = f"{Line}_{self.line_counter}"  #Adicionar o identificador da linha
                self.graph.add_edge(FromStationId,ToStationId,line=line_id,lenght=Distance,weight=OffPeakRunningTime, ampeak=AMpeakRunningTime, interpeak=InterpeakRunningtime)
                self.line_counter += 1
    
    def n_stations(self):
        return self.graph.number_of_nodes()

    def n_stations_zone(self):
        zones = {}
        for node, data in self.graph.nodes(data=True):
            zone = float(data['zone'])  
            int_zone = int(zone)  #Arredondar para o número inteiro abaixo
            upper_zone = int_zone + 1 #Considerar o número acima

            if int_zone in zones:
                zones[int_zone] += 1
            else:
                zones[int_zone] = 1

            if zone > int_zone:  #Verificar se a zona é um valor decimal
                if upper_zone in zones:
                    zones[upper_zone] += 1
                else:
                    zones[upper_zone] = 1

        return zones

    def n_edges(self):
        return self.graph.number_of_edges() #Equivale ao numero de troços sem contar os repetidos 

    def n_edges_line(self):
        lines = {}
        for connection in self.connectionslist:
            line = int(connection[0])
            if line in lines:
                lines[line] += 1
            else:
                lines[line] = 1
        return lines


    def mean_degree(self):
        degrees = [degree for _, degree in self.graph.degree()]
        return sum(degrees) / len(degrees)

    def mean_weight(self, weight):
        weights = [data[weight] for _, _, data in self.graph.edges(data=True) if weight in data]
        return sum(weights) / len(weights)

    def visualizeNet(self):
        # Visualização usando NetworkX
        nx.draw(self.graph, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500)
        plt.show()

    def visualizeFol(self):
        # Visualização usando Folium
        m = folium.Map(location=[0, 0], zoom_start=2)
        for node, data in self.graph.nodes(data=True):
            folium.Marker(location=[data['latitude'], data['longitude']], popup=node).add_to(m)
        for source, target, data in self.graph.edges(data=True):
            folium.PolyLine(locations=[(self.graph.nodes[source]['latitude'], self.graph.nodes[source]['longitude']),
                                       (self.graph.nodes[target]['latitude'], self.graph.nodes[target]['longitude'])],
                            color='red', weight=2, popup=data['line']).add_to(m)
            
        m.save('graph.html')

    def visualizeMat(self):
        # Visualização usando Matplotlib
        fig, ax = plt.subplots()

        for node, data in self.graph.nodes(data=True):
            ax.plot(data['longitude'], data['latitude'], 'ko')
            ax.text(data['longitude'] + 0.001, data['latitude'] + 0.001, data['display_name'])

        for source, target, data in self.graph.edges(data=True):
            x_values = [self.graph.nodes[source]['longitude'], self.graph.nodes[target]['longitude']]
            y_values = [self.graph.nodes[source]['latitude'], self.graph.nodes[target]['latitude']]
            ax.plot(x_values, y_values, 'k-')

        ax.set_aspect('equal')
        plt.title('London Underground')
        plt.show()


######## PARTE 2


    def calculate_nearest_station(self, point): #Dado um ponto(x,y), procura a estação mais proxima
        nearest_station = None #Iniciar a estação em None
        min_distance = float('inf') #Iniciar a distancia minima em infinito
        for node, data in self.graph.nodes(data=True): #Do grafo em NetworkX, vai guardar os valores 'node' e data'
            station_point = (data['latitude'], data['longitude']) #Criará um ponto com as respectivas coordenadas da estação em analise
            distance = self.calculate_distance(point, station_point) #Invoca a função calculate_distance() para calcular a distancia desse dado ponto até à respectiva estação
            if distance < min_distance: #Verifica se esse valor (distancia entre o ponto dado e a estação) é o minimo 
                nearest_station = node #Caso se verifique, guarda qual a estação
                min_distance = distance #Caso se verifique, guarda qual a distância
        return nearest_station

    def calculate_distance(self, point1, point2):#Dados 2 pontos distintos (x,y), calcula a respectiva distancia euclidiana entre ambos
        x1, y1 = point1
        x2, y2 = point2
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return distance

    def shortest_path(self, start_station, end_station,time=None):# Aplicar o algoritmo de Dijkstra para encontrar o caminho mais curto
        if time==None:
            shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight='lenght') #Notação respectiva ao dijkstra_path() da biblioteca NetworkX
            return shortest_path
        elif 7<int(time[0])<=10:
            shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight='ampeak')
            return shortest_path
        elif 10<int(time[0])<=16:
            shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight='interpeak')
            return shortest_path
        else:
            shortest_path = nx.dijkstra_path(self.graph, start_station, end_station, weight='weight')
            return shortest_path
        

    def dijkstra(self, start_node): #Aplicação do algoritmo Dijkstra, que recebe o nó inicial
        self.weight = {} #Cria um dicionário vazio chamado weight para armazenar os pesos dos nós.
        self.visited = set() #Cria um conjunto vazio  para armazenar os nós visitados.
        self.previous = {} #Cria um dicionário vazio  para armazenar os nós anteriores no caminho mais curto.
        self.weight = {node: float('inf') for node in self.graphedges} # Inicializa todos os pesos dos nós como infinito.
        self.weight[start_node] = 0 # Define o peso do nó inicial como 0.
        self.previous = {node: None for node in self.graphedges} #Define todos os nós anteriores como None.

        while self.visited != set(self.graphedges): #Enquanto houver nós não visitados no grafo:
            min_weight = float('inf') # Define o menor peso como infinito.
            min_node = None # Define o nó com o menor peso como None.
            for node in self.graphedges:
                if node not in self.visited and self.weight[node] < min_weight: # Se o nó não foi visitado e tem um peso menor que o menor peso atual:
                    min_weight = self.weight[node] # Atualiza o menor peso com o peso do nó.
                    min_node = node # Atualiza o nó com o menor peso.

            self.visited.add(min_node)# Guardar os nós  visitados com menor peso



            for neighbor, weights in self.graphedges[min_node].items():
                for weight in weights: #Como existem linhas paralelas, corre utilizando peso a peso (quando existem)
                    new_weight = self.weight[min_node] + weight# Calcula o novo peso somando o peso do nó atual com o peso do vizinho.
                    if new_weight < self.weight[neighbor]: # Se o novo peso for menor que o peso anterior do vizinho:
                        self.weight[neighbor] = new_weight # Atualiza o peso do vizinho com o novo peso.
                        self.previous[neighbor] = min_node # Define o nó atual como o nó anterior do vizinho.

    
    def shortest_path_dijkstra(self, start_station, end_station,time=None):#Criar qual o caminho mais rapido ou perto, dadas as estações de partida e chegada e possivelmente um tempo
        self.graphedges={} #Cria um dicionario vazio
        if time is None:#Se não for dado um tempo, é calculado o percurso que contem a distancia minima
            #Criar-se-á um dicionário apenas com os dados relevantes para o caso
            for line in self.connectionslist:
                if line[1] not in self.graphedges: 
                    self.graphedges[line[1]] = {}  #Neste caso, contendo apenas o nó de partida, de chegada e o valor respectivo à distância entre os dois nós
                if line[2] not in self.graphedges[line[1]]:
                    self.graphedges[line[1]][line[2]] = []  #Neste caso, existindo (ou ainda não) o nó de partida, de chegada (linhas paralelas), acrescenta o valor respectivo à distância entre os dois nós 
                self.graphedges[line[1]][line[2]].append(float(line[3])) 

            self.dijkstra(start_station) #Corre o Algoritmo Dijkstra acima definido

            path = [] #Cria uma lista vazia (inicialmente) que guarda o percurso mais curto
            current_node = end_station #Define como nó atual o da estação de chegada
            while current_node is not None: #Corre até não existirem nós disponiveis
                path.insert(0, current_node) #Coloca no inicio da lista o nó atual
                current_node = self.previous[current_node]  #Coloca o nó atual como sendo o anterior ao mesmo (dado que ele está a correr da estação de chegada até à estação de partida)
            return path

        elif 7 < int(time[0]) <= 10:#Dado um tempo, é calculado o percurso que contem o percurso mais rapido em horário AM PEAK
            for line in self.connectionslist:
                if line[1] not in self.graphedges:
                    self.graphedges[line[1]] = {}  
                if line[2] not in self.graphedges[line[1]]:
                    self.graphedges[line[1]][line[2]] = []  
                self.graphedges[line[1]][line[2]].append(float(line[5])) 

            self.dijkstra(start_station)

            path = []
            current_node = end_station
            while current_node is not None:
                path.insert(0, current_node)
                current_node = self.previous[current_node]
            return path

        elif 10 < int(time[0]) <= 16:#Dado um tempo, é calculado o percurso que contem o percurso mais rapido em horário INTER PEAK
            for line in self.connectionslist:
                if line[1] not in self.graphedges:
                    self.graphedges[line[1]] = {}  
                if line[2] not in self.graphedges[line[1]]:
                    self.graphedges[line[1]][line[2]] = []  
                self.graphedges[line[1]][line[2]].append(float(line[6])) 

            self.dijkstra(start_station)

            path = []
            current_node = end_station
            while current_node is not None:
                path.insert(0, current_node)
                current_node = self.previous[current_node]
            return path

        else:#Dado um tempo, que não corresponde nem ao INTER PEAK, nem ao AM PEAK é calculado o percurso que contem o percurso mais rapido em horário OFF PEAK
            for line in self.connectionslist:
                if line[1] not in self.graphedges:
                    self.graphedges[line[1]] = {}  
                if line[2] not in self.graphedges[line[1]]:
                    self.graphedges[line[1]][line[2]] = []  
                self.graphedges[line[1]][line[2]].append(float(line[4])) 

            self.dijkstra(start_station)

            path = []
            current_node = end_station
            while current_node is not None:
                path.insert(0, current_node)
                current_node = self.previous[current_node]
            return path
        
    
    def draw_path(self, random_points1,time=None): #Recebe os dois pontos ((x1,y1),(x2,y2)) e possivelmente um tempo e desenha um grafo real com o caminho e os pontos marcados
        start_station = self.calculate_nearest_station(random_points1[0]) #Corre a função calculate_nearest_station() utilizando o primeiro ponto
        end_station = self.calculate_nearest_station(random_points1[1]) #Corre a função calculate_nearest_station() utilizando o segundo ponto
        path = self.shortest_path(start_station, end_station, time) #Corre a função shortest_path() utilizando as estações acima calculadas, guardando a lista retomada

        m = folium.Map(location=[0, 0], zoom_start=2) #Cria um mapa grafo vazio em Folium 

        folium.Marker(location=[random_points1[0][0],random_points1[0][1]], icon=folium.Icon(color='red')).add_to(m) #Marca as cordenadas do ponto primeiro no mapa
        folium.Marker(location=[random_points1[1][0],random_points1[1][1]], icon=folium.Icon(color='red')).add_to(m) #Marca as cordenadas do ponto segundo no mapa

        for node, data in self.graph.nodes(data=True): #Adiciona ao mapa grafo todas as estações: para isso, vai buscar todos os nós do grafo original (definido acima), as respectivas coordenadas 
            folium.Marker(location=[data['latitude'], data['longitude']], popup=node).add_to(m)

        for source, target, data in self.graph.edges(data=True): #Adiciona ao mapa grafo todas as conecções: para isso, vai buscar todos os edge do grafo original (definido acima), as respectivas coordenadas 
            folium.PolyLine(locations=[(self.graph.nodes[source]['latitude'], self.graph.nodes[source]['longitude']),
                                   (self.graph.nodes[target]['latitude'], self.graph.nodes[target]['longitude'])],
                        color='red', weight=2, popup=data['line']).add_to(m)

        for i in range(len(path) - 1): #Dada a lista path, marca todas as arestas do caminho otimo
            source = path[i]
            target = path[i + 1]
            data = self.graph.edges[source, target] # Obtém os dados da aresta no grafo original.

            folium.PolyLine(locations=[(self.graph.nodes[source]['latitude'], self.graph.nodes[source]['longitude']),
                                   (self.graph.nodes[target]['latitude'], self.graph.nodes[target]['longitude'])],
                        color='green', weight=5, popup=data['line']).add_to(m)

        m.save('graph_with_path.html') #Salva o mapa em um arquivo HTML

###Funções que geram aleatoriamente os pontos e uma hora do dia

def random_points(x1=51.4022, x2=51.7052, y1=-0.6110, y2=0.2510): # Define a função random_points que gera dois pontos aleatórios dentro dos limites dados. Caso não sejam dados, estão predefinidas cordenadas correspondentes a uma figua que ingloba todos os pontos gps do grafo
    start = (random.uniform(x1, x2), random.uniform(y1, y2)) # Gera um ponto aleatório, dentro dos limites, para a coordenada x e y de partida.
    end = (random.uniform(x1, x2), random.uniform(y1, y2)) # Gera um ponto aleatório dentro, dos limite,s para a coordenada x e y de chegada.
    return start, end # Retorna um tuplo contendo os pontos de partida e chegada gerados.

def random_time(): # Define a função random_time que gera uma hora aleatória.
    hour = random.randint(0, 23) # Gera um número inteiro aleatório entre 0 e 23 para representar a hora.
    minute = random.randint(0, 59) # Gera um número inteiro aleatório entre 0 e 59 para representar os minutos.
    second = random.randint(0, 59) # Gera um número inteiro aleatório entre 0 e 59 para representar os segundos.
    return hour, minute, second # Retorna um tuplo contendo a hora, os minutos e os segundos gerados.
    





