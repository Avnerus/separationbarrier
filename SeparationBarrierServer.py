from SeparationBarrier import Israeli, Palestinian, SeparationBarrierModel
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

ISRAELI_COLOR = "#0000FF"
PALESTINIAN_COLOR = "#00FF00"

def israeli_palestinian_portrayl(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "x": agent.pos[0], "y": agent.pos[1],
                 "Filled": "true"}

    if type(agent) is Israeli:
        color = ISRAELI_COLOR
        portrayal["Color"] = ISRAELI_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0

    elif type(agent) is Palestinian:
        portrayal["Color"] = PALESTINIAN_COLOR
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1
    return portrayal

canvas_element = CanvasGrid(israeli_palestinian_portrayl, 100, 100, 500, 500)
server = ModularServer(SeparationBarrierModel, [canvas_element],
                      "Israeli-Palestinian Separation Barrier",
                      height=100,
                      width=100,
                      israeli_density=0.4,
                      palestinian_density = 0.2,
                      israeli_vision=7,
                      palestinian_vision=7
                      )
server.launch()
