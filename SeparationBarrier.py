import random
import math

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector


class Settler(Agent):
    def __init__(self, unique_id, pos, vision, breed,  model):

        super(Settler, self).__init__(unique_id, model)

        self.unique_id = unique_id
        self.pos = pos
        self.vision = vision
        self.breed = breed
        self.violent = False
        self.victim = False

    def step(self, model):
        self.reset_state()

        self.update_neighbors(model)
        palestinians_in_vision = [x for x in self.neighbors if x.breed == "Palestinian"]
        if len(palestinians_in_vision) > 0 and random.random() < model.settlers_violence_rate:
            # Violent settler. Choose a random palestinian
            victim = random.choice(palestinians_in_vision)
            self.violent = True
            victim.receive_violence(self, model)



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

    def receive_violence(self, palestinian, model):
        self.victim = True
        # Build a barrier
        model.set_barrier(palestinian.pos)


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
class IsraelRear(Agent):

    def __init__(self, unique_id, pos, model):

        super(IsraelRear, self).__init__(unique_id, model)
        self.unique_id = unique_id
        self.pos = pos
        self.breed = "IsraelRear"

    def step(self, model):
        return

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
        self.reset_state()
    
        self.anger_decay()
        self.update_neighbors(model)
        self.update_level_of_freedom(model)

        self.violence_probability = 1 - math.exp(-0.01 * ((1-self.freedom) + self.anger));
        self.suicide_bombing_probability = 1 - math.exp(-0.0001 * ((1-self.freedom) + self.anger));
        chance = random.random()

        if (chance < self.suicide_bombing_probability):
            print ("Sucicide bomb!!")
        #print("Violence probability %f" % self.violence_probability)
        elif (chance < self.violence_probability):
            # Look for settler neighbours
            settlers_in_vision = [x for x in self.neighbors if x.breed == 'Settler']
            if len(settlers_in_vision) > 0:
                print("Violent Palestinian!")
                # Violent settler. Choose a random palestinian
                victim = random.choice(settlers_in_vision)
                self.violent = True
                victim.receive_violence(self, model)


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
            if x.breed == "IsraelRear" or x.breed == "Settler" or x.breed == "Barrier":
                counter += 1

        self.freedom = 1 - (counter / len(self.neighborhood))
        #print("Level of freedom = 1 - (%d / %d = %f)" % (counter,len(self.neighborhood),self.freedom))


    def reset_state(self):
        self.violent = False
        self.victim = False

    def anger_decay(self):
        self.anger = max(0, self.anger - 0.1)

    def receive_violence(self, settler, model):
        self.victim = True
        self.anger += 0.5

class SeparationBarrierModel(Model):
    def __init__(self, height, width, palestinian_density, settlement_density,
                 settlers_violence_rate,
                 settler_vision=1, palestinian_vision=1, 
                 movement=True, max_iters=1000):

        super(SeparationBarrierModel, self).__init__()
        self.height = height
        self.width = width
        self.palestinian_density = palestinian_density
        self.settler_vision = settler_vision
        self.palestinian_vision = palestinian_vision
        self.settlement_density = settlement_density
        self.movement = movement
        self.running = True
        self.max_iters = max_iters
        self.iteration = 0
        self.schedule = RandomActivation(self)
        self.settlers_violence_rate = settlers_violence_rate
        self.grid = SingleGrid(height, width, torus=True)

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
            if y == self.grid.height - 1:
                unique_id += 1
                israel_rear = IsraelRear(unique_id, (x, y), model=self)
                self.grid.position_agent(israel_rear, x,y)
            elif random.random() < self.palestinian_density:
                palestinian = Palestinian(unique_id, (x, y), vision=self.palestinian_vision, breed="Palestinian",
                          model=self)
                unique_id += 1
                self.grid.position_agent(palestinian, x,y)
                self.schedule.add(palestinian)
            elif ((y > (self.grid.height) * (1-self.settlement_density)) and y < (self.grid.height - 1) and random.random() < self.settlement_density):
                settler = Settler(unique_id, (x, y),
                                  vision=self.settler_vision, model=self, breed="Settler")
                unique_id += 1
                self.grid.position_agent(settler, x,y)
                self.schedule.add(settler)

    def set_barrier(self,pos):
        (x,y)  = pos
        current = self.grid[y][x]
        print ("Set barrier!!", pos, current)
        self.grid.move_to_empty(current)
        print ("Moved to empty")
        barrier = Barrier(-1, pos, model=self)
        self.grid.position_agent(barrier, x,y)
        

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
