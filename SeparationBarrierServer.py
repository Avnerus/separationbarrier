from SeparationBarrier import IsraelRear, Settler, Palestinian, Barrier, SeparationBarrierModel
from SeparationBarrierGrid import SeparationBarrierGrid

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid


ISRAELI_COLOR = "#0000FF"
PALESTINIAN_COLOR = "#FF0000"
VIOLENT_COLOR = "#000000"
BARRIER_COLOR = "#BDBDBD"
ISRAEL_REAR_COLOR ="#00EEFF"

def israeli_palestinian_portrayl(agent):
    if agent is None:
        return


    portrayal = {"Shape": "circle",
                 "Filled": "true"}

    if type(agent) is Settler:
        color = VIOLENT_COLOR if agent.violent else ISRAELI_COLOR
        portrayal["Color"] = color
        size = 1.0 if agent.violent or agent.victim else 0.5
        portrayal["r"] = portrayal["w"] = portrayal["h"] = size
        portrayal["Layer"] = 0
        portrayal["Shape"] = "rect"

    elif type(agent) is Palestinian:
        color = VIOLENT_COLOR if agent.violent else PALESTINIAN_COLOR
        portrayal["Color"] = color
        size = 1.0 if agent.victim or agent.violent else 0.5
        portrayal["r"] = size
        portrayal["Layer"] = 1

    elif type(agent) is Barrier:
        color = BARRIER_COLOR
        portrayal["Color"] = color
        size = 1.0 
        portrayal["r"] = portrayal["w"] = portrayal["h"] = size
        portrayal["Layer"] = 2
        portrayal["Shape"] = "rect"

    elif type(agent) is IsraelRear:
        color = ISRAEL_REAR_COLOR
        portrayal["Color"] = color
        size = 1.0 
        portrayal["r"] = portrayal["w"] = portrayal["h"] = size
        portrayal["Layer"] = 3
        portrayal["Shape"] = "rect"

    return portrayal

canvas_element = SeparationBarrierGrid(israeli_palestinian_portrayl, 40, 40, 600, 600)
server = ModularServer(SeparationBarrierModel, [canvas_element],
                      "Israeli-Palestinian Separation Barrier",
                      height=40,
                      width=40,
                      settlement_density = 0.3,
                      palestinian_density = 0.3,
                      settlers_violence_rate = 0.01
                      )
server.launch()
