from SeparationBarrier import Israeli, Palestinian, SeparationBarrierModel
from SeparationBarrierGrid import SeparationBarrierGrid

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid


ISRAELI_COLOR = "#0000FF"
PALESTINIAN_COLOR = "#FF0000"
VIOLENT_COLOR = "#000000"

def israeli_palestinian_portrayl(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle",
                 "x": agent.pos[0], "y": agent.pos[1],
                 "Filled": "true"}

    if type(agent) is Israeli:
        color = VIOLENT_COLOR if agent.violent else ISRAELI_COLOR
        portrayal["Color"] = color
        size = 1.0 if agent.violent else 0.5
        portrayal["r"] = portrayal["w"] = portrayal["h"] = size
        portrayal["Layer"] = 0
        portrayal["Shape"] = "rect"

    elif type(agent) is Palestinian:
        portrayal["Color"] = PALESTINIAN_COLOR
        size = 1.0 if agent.victim else 0.5
        portrayal["r"] = size
        portrayal["Layer"] = 1
    return portrayal

canvas_element = SeparationBarrierGrid(israeli_palestinian_portrayl, 50, 50, 800, 800)
server = ModularServer(SeparationBarrierModel, [canvas_element],
                      "Israeli-Palestinian Separation Barrier",
                      height=50,
                      width=50,
                      israeli_density=0.3,
                      settlement_density = 0.3,
                      palestinian_density = 0.2,
                      settlers_violence_rate = 0.01
                      )
server.launch()
