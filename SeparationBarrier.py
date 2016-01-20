import random
import math

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector


class Israeli(Agent):
    def __init__(self, unique_id, pos, vision, breed,  model):

        super(Israeli, self).__init__(unique_id, model)

        self.unique_id = unique_id
        self.pos = pos
        self.vision = vision
        self.breed = breed
        self.violent = False
        self.victim = False

    def step(self, model):
        self.reset_state()

        if self.breed == "Settler":
            self.update_neighbors(model)
            palestinians_in_vision = [x for x in self.neighbors if x.breed == 'Palestinian']
            if len(palestinians_in_vision) > 0 and random.random() < model.settlers_violence_rate:
                # Violent settler. Choose a random palestinian
                victim = random.choice(palestinians_in_vision)
                self.violent = True
                victim.victim = True



    def update_neighbors(self, model):
        """
        Look around and see who my neighbors are
        """
        self.neighborhood = model.grid.get_neighborhood(self.pos,
                                                        moore=True, radius=1)
        self.neighbors = model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [c for c in self.neighborhood if
                                model.grid.is_cell_empty(c)]

    def reset_state(self):
        self.violent = False
        self.victim = False


class Barrier(Agent):

    def __init__(self, unique_id, pos, model):

        super(Barrier, self).__init__(unique_id, model)
        self.unique_id = unique_id
        self.pos = pos
        self.breed = "Barrier"

    def step(self, model):
        """
        Inspect local vision and arrest a random active agent. Move if
        applicable.
        """


class Palestinian(Agent):

    def __init__(self, unique_id, pos, vision, breed, model):

        super(Palestinian, self).__init__(unique_id, model)
        self.unique_id = unique_id
        self.pos = pos
        self.vision = vision
        self.breed = breed
        self.violent = False
        self.victim = False
        self.anger = 0
        self.freedom = 0
        self.attackProbability = 0


    def step(self, model):
        """
        Inspect local vision and arrest a random active agent. Move if
        applicable.
        """
        self.update_neighbors(model)
        self.update_level_of_freedom(model)

        self.violence_probability = 1 - math.exp(-0.01 * ((1-self.freedom) + self.anger));
        #print("Violence probability %f" % self.violence_probability)
        if (random.random() < self.violence_probability):
            print("Violent Palestinian!")
        

        self.reset_state()

    def update_neighbors(self, model):
        """
        Look around and see who my neighbors are.
        """
        self.neighborhood = model.grid.get_neighborhood(self.pos,
                                                        moore=True, radius=1)
        self.neighbors = model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [c for c in self.neighborhood if
                                model.grid.is_cell_empty(c)]

    def update_level_of_freedom(self, model):
        counter = 0
        for x in self.neighbors:
            if x.breed == "Settler" or x.breed == "Barrier":
                counter += 1

        self.freedom = 1 - (counter / len(self.neighborhood))
        #print("Level of freedom = 1 - (%d / %d = %f)" % (counter,len(self.neighborhood),self.freedom))


    def reset_state(self):
        self.violent = False
        self.victim = False

class SeparationBarrierModel(Model):
    def __init__(self, height, width, israeli_density, palestinian_density, settlement_density, 
                 settlers_violence_rate,
                 israeli_vision=1, palestinian_vision=1, 
                 movement=True, max_iters=1000):

        super(SeparationBarrierModel, self).__init__()
        self.height = height
        self.width = width
        self.israeli_density = israeli_density
        self.palestinian_density = palestinian_density
        self.israeli_vision = israeli_vision
        self.palestinian_vision = palestinian_vision
        self.settlement_density = settlement_density
        self.movement = movement
        self.running = True
        self.max_iters = max_iters
        self.iteration = 0
        self.schedule = RandomActivation(self)
        self.settlers_violence_rate = settlers_violence_rate
        self.grid = Grid(height, width, torus=True)

        model_reporters = {
        }
        agent_reporters = {
            "x": lambda a: a.pos[0],
            "y": lambda a: a.pos[1],
        }
        self.dc = DataCollector(model_reporters=model_reporters,
                                agent_reporters=agent_reporters)
        unique_id = 0

        # Israelis and palestinans split the region in half

        for (contents, x, y) in self.grid.coord_iter():
            if (y < self.grid.height / 2):
                if random.random() < self.palestinian_density:
                    palestinian = Palestinian(unique_id, (x, y), vision=self.palestinian_vision, breed="Palestinian",
                              model=self)
                    unique_id += 1
                    self.grid[y][x] = palestinian
                    self.schedule.add(palestinian)
                elif ((y > (self.grid.height / 2) * (1-self.settlement_density)) and random.random() < self.settlement_density):
                    israeli = Israeli(unique_id, (x, y),
                                      vision=self.israeli_vision, model=self, breed="Settler")
                    unique_id += 1
                    self.grid[y][x] = israeli
                    self.schedule.add(israeli)

            elif random.random() < self.israeli_density:
                israeli = Israeli(unique_id, (x, y),
                                  vision=self.israeli_vision, model=self, breed="Citizen")
                unique_id += 1
                self.grid[y][x] = israeli
                self.schedule.add(israeli)

    def step(self):
        """
        Advance the model by one step and collect data.
        """
        if (self.iteration < 10000000):
            self.schedule.step()
            self.dc.collect(self)
            #print("Iteration %d " % self.iteration)
            self.iteration += 1
        #if self.iteration > self.max_iters:
        #    self.running = False
