from __future__ import annotations
from typing import Text
import discord


class Vertex:
    def __init__(self, name) -> None:
        self.name = name
        self.edges = []
        self.harga = None
        self.path = []
        self.choosen = False

class Edge:
    def __init__(self, start: Vertex, end: Vertex, weight = -1) -> None:
        self.start = start
        self.end = end
        self.weight = weight

class Graph:
    def __init__(self) -> None:
        self.vertices = {}
    def showGraph(self):
        for _, ver in self.vertices.items():
            print(ver.name, " : \t", end="")
            print(f"{'|'.join([f'{edge.start.name} {edge.end.name} {edge.weight}' for edge in ver.edges])}".replace("|", "\n\t"))
            print()
    
async def djikstraGenerator(client, ctx, util, inputs):
    try:
        print(inputs)
        uInputs = inputs.split("\n")
        if util in ["help", "-h", "--help", "-help"]:
            await ctx.send(
"""
```cmd
info:
generator step by step untuk djikstra
baris pertama  : banyak vertex
baris kedua    : nama nama vertex
baris ketiga   : banyak edge
n baris edge
baris terakhir : dari vertex apa ke vertex apa
```
"""
        )
            return

        graphN = Graph()

        await ctx.send("cheat Djikstra ez table")
        nV = int(uInputs[0])
        verName = uInputs[1]
        verName = [chr(a) for a in range(65, 65+nV)] if len(verName) == 0 else verName.split(" ")

        for a in verName:
            graphN.vertices[a] = Vertex(a)

        nE = int(uInputs[2])
        # print("masukan berat sisi dengan format `simpul1` `simpul2` `weight` (asumsi indirect graph)")
        # print(f"simpul yang valid [{' '.join(verName)}]")

        for i in range(nE):
            temp = uInputs[3 + i].split(" ")
            temp[2] = int(temp[2])
            graphN.vertices[temp[0]].edges.append(Edge(graphN.vertices[temp[0]], graphN.vertices[temp[1]], temp[2]))
            graphN.vertices[temp[1]].edges.append(Edge(graphN.vertices[temp[1]], graphN.vertices[temp[0]], temp[2]))

        # print("Your graph:")
        # graphN.showGraph()

        # print("mau dari simpul mana ke simpul mana ? pilih dengan format `simpul awal` `simpul akhir`")
        # print(f"pilihan valid : [{' '.join([a for a, b in graphN.vertices.items() if len(b.edges) != 0])}]")
        awal, akhir = uInputs[-2].split(" ")

        #Djikstra algo ez gg ikz
        choosenOne = graphN.vertices[awal]

        choosenOne.harga = 0
        choosenOne.path = [choosenOne]

        inWork = [a for _, a in graphN.vertices.items() if not a.choosen]

        choosenOne.choosen = True

        message ="Tabel: \n"
        message += "V\t" +  "\t".join([a.name for a in inWork]) + "\n"
        while inWork:

            for ver in inWork: # iterate vertex yang belom kepilih
                verEdges = [a for a in choosenOne.edges if a.end == ver] # ambil semua edge yang berawal di choosenOne dan berakhir di ver
                if len(verEdges): # kalo ternyata dari choosenOne ada jalan ke vertex ini
                    tempHarga = verEdges[0].weight # untuk sekarang asumsi cuma ada 1 edge
                    if ver.harga == None or ver.harga > choosenOne.harga + tempHarga: # cek ada jalan dan apakh lebih murah
                        ver.harga = choosenOne.harga + tempHarga
                        ver.path = choosenOne.path + [ver]


            printAbleRes = []
            for _, a in graphN.vertices.items():
                if a.choosen:
                    printAbleRes.append(".")
                    continue
                elif a.path:
                    # print(a.path)
                    printAbleRes.append(f"{a.harga},{a.path[-2].name}")
                else:
                    printAbleRes.append("INF")
            message += choosenOne.name + "\t" + "\t".join(printAbleRes) + "\n"

            choosenOne.choosen = True

            tempInWork = inWork.copy()
            inWork = []
            temp = choosenOne
            choosenOne = None
            for a in tempInWork:
                
                if a == temp:
                    continue
                inWork.append(a)
                if choosenOne == None or a.harga != None and a.harga < choosenOne.harga:
                    choosenOne = a

        message += "\n" + f"jarak terpendek dari {awal} ke {akhir} adalah " + str(graphN.vertices[akhir].harga) +  f", dengan path : {'-'.join([a.name for a in graphN.vertices[akhir].path])}"
        f = open("djiksTemp.bat", "w");
        f.write(message)
        f.close()
        attachment = discord.File("djiksTemp.bat")
        await ctx.send("enjoy~", file=attachment)


    except Exception as e:
        await ctx.send(e)

class Graph2:
    def __init__(self, vert):
        self.v = vert
        self.edges = []
        self.track = []
        self.visitedvert = []
        self.matrix = []

        self.vertices = []
        self.hashMap = {}

        '''
        self.matrix
        [
            [["a", "b", w1], ["a", "c", w2]],
            .
            .
            .
            [["n", "a", w1], ["n", "b", w2]]
        ]

        self.vertices
        [
            Vertex_Object1,
            Vertex_Object2,
            Vertex_Object3
        ]
        
        self.adjency_matrix
        [
            [0, 2, 3, 0],
            [2, 0, 3, 1],
            [2, 1, 0, 3],
            [1, 3, 0, 0]
        ]
        '''
    
    def add_edge(self, u, v, weight):
        # print([a.__dict__ for a in self.vertices])
        sVert = [a for a in self.vertices if a.name == u] # WWKWKKWKW PADET ANJING
        if sVert:
            start = sVert[0]
        else:
            start = Vertex(u)
            self.vertices.append(start)
        eVert = [a for a in self.vertices if a.name == v]
        if eVert:
            end = eVert[0]
        else:
            end = Vertex(v)
            self.vertices.append(end)
        nEdge = Edge(start, end, weight)
        mEdge = Edge(end, start, weight)
        self.edges.append(nEdge)
        self.edges.append(mEdge)
        start.edges.append(nEdge)
        end.edges.append(mEdge)

    
    def make_hashMap(self):
        self.hashMap = {}
        for a in self.vertices:
            self.hashMap[a.name] = a

    def make_adjency_matrix(self):
        self.make_hashMap()
        self.adjency_matrix = [[0 for _ in range(self.v)] for _ in range(self.v)]
        # print(self.adjency_matrix)

        for edge in self.edges:
            self.adjency_matrix[ord(edge.start.name) - 65][ord(edge.end.name) - 65] = edge.weight

    def make_matrix(self):
        awalList = sorted(set([a.start.name for a in self.edges]))
        for awal in awalList:
            self.matrix.append([[i.start.name, i.end.name, i.weight] for i in self.edges if i.start.name == awal])
    
    def append_edge(self, u, v, weight):
        if not self.matrix:
            for a in self.matrix: # [["awal", "akhir", berat], ["awal", "akhir", berat]]
                if len(a[0]) != 0:
                    if a[0][0] == u:
                        a.append([u, v, weight])
                        break
        else:
            self.matrix.append([[u, v, weight]])

def cyclePurger(edgesList: list[Edge], visitedVertices: list[Vertex]) -> list[Edge]:
    for i in range(len(edgesList) -1, -1, -1):
        if edgesList[i].start in visitedVertices and edgesList[i].end in visitedVertices:
            del edgesList[i]
    # for i, edge in enumerate(edgesList):
    #     if edge.start in visitedVertices and edge.end in visitedVertices:
    #         del edgesList[i]
    return edgesList
        
def primPlusPlus(grap: Graph):
    edgesCopy = grap.edges.copy()
    visitedVert = []
    # ambil edges dengan bobot paling kecil
    edgesCopy.sort(key= lambda x: x.weight)
    edgesCopy = edgesCopy[::2]
    # print([b.__dict__ for b in edgesCopy])

    cheapEdge = edgesCopy[0]
    tots = cheapEdge.weight
    visitedVert = list(dict.fromkeys(visitedVert + [cheapEdge.start] + [cheapEdge.end]))
    del edgesCopy[0]
    text = f"```cmd\ni:\n\nPilihan ke 1: {cheapEdge.start.name} {cheapEdge.end.name} {cheapEdge.weight}\n"
    i = 2
    while len(edgesCopy) > 1:
        validEdges = [a for a in edgesCopy if a.start in visitedVert or a.end in visitedVert]
        text += "valid choice:\n" + "\n".join([f"{edge.start.name} {edge.end.name} {edge.weight}" for edge in sorted(validEdges, key= lambda x: x.weight)]) + "\n"
        cheapEdge = validEdges[0]
        tots += cheapEdge.weight
        visitedVert = list(dict.fromkeys(visitedVert + [cheapEdge.start] + [cheapEdge.end]))
        text += f"Pilihan ke {i}: {cheapEdge.start.name} {cheapEdge.end.name} {cheapEdge.weight}\n"

        del edgesCopy[edgesCopy.index(cheapEdge)]
        edgesCopy = cyclePurger(edgesCopy, visitedVert)
        i += 1
    text += f"Harga total untuk MST adalah {tots}```"
    return text

async def prim_generator(client, ctx, util, inputs):
    try:
        print(inputs)
        uInputs = inputs.split("\n")
        if util in ["help", "-h", "--help", "-help"]:
            await ctx.send(
"""
```cmd
info:
generator step by step untuk prim
baris pertama  : banyak vertex
baris kedua    : nama nama vertex
baris ketiga   : banyak edge
n baris edge
```
"""
        )
            return
        graphN = Graph2(int(uInputs[0]))
        for i in range(int(uInputs[2])):
            start, end, weight = uInputs[i+3].split(' ')
            graphN.add_edge(start, end, int(weight))
        text = primPlusPlus(graphN)
        await ctx.send(text)
    except Exception as e:
        await ctx.send(e)

def kruskal_algo(grap: Graph2):
    edgesCopy = grap.edges.copy()
    vert_groups = []
    # ambil edges dengan bobot paling kecil
    edgesCopy.sort(key= lambda x: x.weight)
    edgesCopy = edgesCopy[::2]
    # print([b.__dict__ for b in edgesCopy])

    cheapEdge = edgesCopy[0]
    vert_groups.append([cheapEdge.start, cheapEdge.end])
    tots = cheapEdge.weight

    del edgesCopy[0]
    table = "```cmd\ni:\n\n"
    text = f"```cmd\ni:\n\nPilihan ke 1: {cheapEdge.start.name} {cheapEdge.end.name} {cheapEdge.weight}\n"
    i = 2
    while i < grap.v:
            # 0 : new tree
            # 1 : span tree
            # 2 : connect tree or skip
        # print(f"{i}")
        # print([b.__dict__ for b in edgesCopy])
        sig_out = False
        table += f"{edgesCopy[0].start.name} {edgesCopy[0].end.name} {edgesCopy[0].weight}"
        for vert_group in vert_groups:
            for vert in vert_group:
                if edgesCopy[0].start == vert or edgesCopy[0].end == vert:
                    # check creating loop
                    if edgesCopy[0].end in vert_group and edgesCopy[0].start in vert_group:
                        # del edgesCopy[0]
                        # text += f"membuat loop {edgesCopy[0].start.name} {edgesCopy[0].end.name}\n"
                        table += "  X"
                        sig_out = True
                    else: # check ujung ada di vert_group lain
                        sVert = edgesCopy[0].start if vert == edgesCopy[0].end else edgesCopy[0].end
                        sig_inner_out = False
                        for inner_vert_group in [a for a in vert_groups if a != vert_group]:
                            for inner_vert in inner_vert_group:
                                if sVert == inner_vert: # nyambungin group
                                    # text += str([vert.name for vert in vert_group]) + str([vert.name for vert in inner_vert_group])
                                    vert_groups[vert_groups.index(vert_group)] = vert_group + inner_vert_group
                                    del vert_groups[vert_groups.index(inner_vert_group)]
                                    # text += "menyatukan tree "
                                    sig_inner_out = True
                                    break
                            if sig_inner_out:
                                break
                        else: # span
                            vert_group.append(sVert)
                            # text += "menumbuhkan tree "
                        text += f"Pilihan ke {i}: {edgesCopy[0].start.name} {edgesCopy[0].end.name} {edgesCopy[0].weight}\n"
                        tots += edgesCopy[0].weight
                        i += 1
                        sig_out = True
                if sig_out:
                    break
            if sig_out:
                break
        else: # new tree
            # text += "membuat tree baru "
            text += f"Pilihan ke {i}: {edgesCopy[0].start.name} {edgesCopy[0].end.name} {edgesCopy[0].weight}\n"
            vert_groups.append([edgesCopy[0].start, edgesCopy[0].end])
            tots += edgesCopy[0].weight
            i += 1
        del edgesCopy[0]
        table += "\n"
        # text += f'''[{', '.join([f'[{ ", ".join([vert.name for vert in vert_group]) }]' for vert_group in vert_groups])}]\n'''
    table += "\n".join([f"{edge.start.name} {edge.end.name} {edge.weight} X" for edge in edgesCopy]) + "```\n"
    text += f"Harga total untuk MST adalah {tots}```"
    return table + text

async def kruskal_generator(client, ctx, util, inputs):
    try:
        print(inputs)
        uInputs = inputs.split("\n")
        if util in ["help", "-h", "--help", "-help"]:
            await ctx.send(
"""
```cmd
info:
generator step by step untuk kruskal
baris pertama  : banyak vertex
baris kedua    : nama nama vertex
baris ketiga   : banyak edge
n baris edge
```
"""
        )
            return
        graphN = Graph2(int(uInputs[0]))
        for i in range(int(uInputs[2])):
            start, end, weight = uInputs[i+3].split(' ')
            graphN.add_edge(start, end, int(weight))
        text = kruskal_algo(graphN)
        await ctx.send(text)

    except Exception as e:
        await ctx.send(e)

class huffman_tree:
    def __init__(self, val, occurence, left, right) -> None:
        self.val = val
        self.occurence = occurence
        self.left = left
        self.right = right
        self.track = ''

def huffman_algo(unc_text: list):
    def add_text(tree, track=""):
        if tree.left != None:
            tree.track = track
            return f"{track}, {tree.occurence}\n" + add_text(tree.left, track + '0') + add_text(tree.right, track + '1')
        else:
            tree.track = track
            return f"{track}, {tree.val}, {tree.occurence}\n"
    def get_leaf(tree):
        if tree.left != None:
            return get_leaf(tree.left) + get_leaf(tree.right)
        else:
            return [tree]
    sItem = {}
    
    for i in unc_text:
        if i in sItem:
            sItem[i] += 1
        else:
            sItem[i] = 1

    trees = {}
    for k, v in {k: v for k, v in sorted(sItem.items(), key=lambda item: item[1])}.items():
        trees[k] = huffman_tree(k, v, None, None)

    while len(trees.keys()) != 1:
        a, b, *_ = trees.keys()
        trees[a + b] = huffman_tree(a + b, trees[a].occurence + trees[b]. occurence, trees[b], trees[a])
        trees = {k: v for k, v in sorted(trees.items(), key=lambda item: item[1].occurence) if k not in [a, b]}
    root = list(trees.values())[0]
    text = "```cmd\ni:\n\n" + "\n".join(add_text(root).split("\n")) + "\n\n" + "assuming 8 bit\n"
    print([a.__dict__ for a in sorted(get_leaf(root), key = lambda x: len(x.track))])
    text += "\n".join(f"{tree.val}: {tree.occurence}*{len(tree.track)} = {tree.occurence*len(tree.track)}" for tree in sorted(get_leaf(root), key = lambda x: len(x.track)))
    text += f"\nCompressed : {sum([tree.occurence*len(tree.track) for tree in get_leaf(root)])} bits\n"
    text += f"Uncompressed : {sum([tree.occurence*8 for tree in get_leaf(root)])} bits\n"
    text += f"compression rasio = compressed/uncompressed = {round(sum([tree.occurence*len(tree.track) for tree in get_leaf(root)]) / sum([tree.occurence*8 for tree in get_leaf(root)]) * 100, 2)}%```"

    return text

    

async def huffman_generator(client, ctx, util, inputs):
    try:
        print(inputs)
        uInputs = inputs.split("\n")
        if util in ["help", "-h", "--help", "-help"]:
            await ctx.send(
"""
```cmd
info:
type : text | any
kalau text, text saja
kalau any, n baris item
```
"""
        )
            return
        if uInputs[0] == 'text':
            text = huffman_algo(uInputs[1])
        elif uInputs[0] == 'any':
            text = huffman_algo(uInputs[1:-1])
        await ctx.send(text)

    except Exception as e:
        await ctx.send(e)

        