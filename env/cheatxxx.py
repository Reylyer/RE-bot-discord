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
#         await ctx.send(
# """untuk merapihkan ini ganti setiap `'    '` dengan `\\t`  
# one line python code:
# ```py
# print('''paste here'''.replace("\t", "\\t"))
# ```
# atau lihat dari attachment langsung
# enjoy~

# """, file=attachment
#         )

    except Exception as e:
        await ctx.send(e)
        