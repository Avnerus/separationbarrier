from mesa.visualization.modules import CanvasGrid


class SeparationBarrierGrid(CanvasGrid):
    package_includes = ["GridDraw.js"]
    local_includes = ["SeparationBarrierGrid.js"]

    def __init__(self, portrayal_method, grid_height, grid_width,
                 canvas_height=500, canvas_width=500):
        super(SeparationBarrierGrid, self).__init__(portrayal_method, grid_height, grid_width, canvas_height, canvas_width)

    def render(self, model):
        rendered_model =  super(SeparationBarrierGrid, self).render(model)
        rendered_model["totalViolence"] = model.total_violence
        return rendered_model
