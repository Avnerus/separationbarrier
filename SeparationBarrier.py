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
            model.violence_count += 1
            victim.receive_violence(self, model)

        if len(self.empty_neighbors) > 0 and random.random() < self.model.settlers_growth_rate:
            #print("Another settler!!")
            self.model.add_settler(random.choice(self.empty_neighbors))


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
        model.set_barrier(self.pos, palestinian.pos)


class Barrier(Agent):

    def __init__(self, unique_id, pos, model):

        super(Barrier, self).__init__(unique_id, model)
        self.unique_id = unique_id
        self.pos = pos
        self.breed = "Barrier"

    def step(self, model):
        return 

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
        self.suicide = False
        self.victim = False
        self.anger = 0
        self.freedom = 0


    def step(self, model):
        """
        Inspect local vision and arrest a random active agent. Move if
        applicable.
        """
        self.reset_state()
    
        self.anger_decay()
        self.update_neighbors(model)
        self.update_level_of_freedom(model)



        self.violence_probability = (1 - math.exp(-1.5* ((1-self.freedom) * 0.01  + self.anger * 2))) * (1-self.blockage)
        self.suicide_bombing_probability = self.violence_probability * model.suicide_rate
        #print("Freedom: ", self.freedom, "Anger: ", self.anger, " Blocakge ", self.blockage)
        #print("Violence probability ", self.violence_probability, " Suicide: ", self.suicide_bombing_probability)
            
        chance = random.random()

        if (chance < self.suicide_bombing_probability):
#            print ("Sucicide bomb!!", self.suicide_bombing_probability, chance)
            self.suicide = True
            self.anger = 0
            model.violence_count += 5
        elif (chance < self.violence_probability):
            # Look for settler neighbours
            settlers_in_vision = [x for x in self.neighbors if x.breed == 'Settler']
            if len(settlers_in_vision) > 0:
                #print("Violent Palestinian!", self.violence_probability)
                # Violent settler. Choose a random palestinian
                victim = random.choice(settlers_in_vision)
                self.anger = 0
                self.violent = True
                model.violence_count += 1
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
        barriers = 0
        for x in self.neighbors:
            if x.breed == "Settler" or x.breed == "Barrier":
                counter += 1
            if x.breed == "Barrier":
                barriers += 1

        self.freedom = 1 - (counter / len(self.neighborhood))
        self.blockage = barriers / len(self.neighborhood)
        #print("Level of freedom = 1 - (%d / %d = %f)" % (counter,len(self.neighborhood),self.freedom))
        #print("Level of Barrier =  (%d / %d = %f)" % (barriers,len(self.neighborhood),self.blockage))


    def reset_state(self):
        self.violent = False
        self.victim = False
        self.suicide = False

    def anger_decay(self):
        self.anger = max(0, self.anger - 0.01)

    def receive_violence(self, settler, model):
        self.victim = True
        self.anger += 0.1

class SeparationBarrierModel(Model):
    def __init__(self, height, width, palestinian_density, settlement_density,
                 settlers_violence_rate, settlers_growth_rate, suicide_rate, greed_level,
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
        self.settlers_growth_rate = settlers_growth_rate
        self.suicide_rate = suicide_rate
        self.greed_level = greed_level

        self.total_violence = 0

        self.grid = SingleGrid(height, width, torus=False)

        model_reporters = {
        }
        agent_reporters = {
#           "x": lambda a: a.pos[0],
#           "y": lambda a: a.pos[1],
        }
        self.dc = DataCollector(model_reporters=model_reporters,
                                agent_reporters=agent_reporters)
        self.unique_id = 0

        # Israelis and palestinans split the region in half
        for (contents, x, y) in self.grid.coord_iter():
            if random.random() < self.palestinian_density:
                palestinian = Palestinian(self.unique_id, (x, y), vision=self.palestinian_vision, breed="Palestinian",
                          model=self)
                self.unique_id += 1
                self.grid.position_agent(palestinian, x,y)
                self.schedule.add(palestinian)
            elif ((y > (self.grid.height) * (1-self.settlement_density)) and random.random() < self.settlement_density):
                settler = Settler(self.unique_id, (x, y),
                                  vision=self.settler_vision, model=self, breed="Settler")
                self.unique_id += 1
                self.grid.position_agent(settler, x,y)
                self.schedule.add(settler)

    def add_settler(self, pos):
        settler = Settler(self.unique_id, pos,
                          vision=self.settler_vision, model=self, breed="Settler")
        self.unique_id += 1
        self.grid.position_agent(settler, pos[0], pos[1])
        self.schedule.add(settler)

    def set_barrier(self,victim_pos, violent_pos):
        #print("Set barrier - Greed level", self.greed_level)
        visible_spots = self.grid.get_neighborhood(victim_pos,
                                                        moore=True, radius=self.greed_level + 1)
        furthest_empty  = self.find_furthest_empty_or_palestinian(victim_pos, visible_spots)
        x,y = furthest_empty
        current = self.grid[y][x]
        #print ("Set barrier!!", pos, current)
        free = True
        if (current is not None and current.breed == "Palestinian"):
            #print ("Relocating Palestinian")
           free =  self.relocate_palestinian(current, current.pos)

        if (free):
            barrier = Barrier(-1, furthest_empty, model=self)
            self.grid.position_agent(barrier, x,y)
        
        # Relocate the violent palestinian
        #violent_x, violent_y = violent_pos
        #if violent_pos != furthest_empty:
        #    violent_palestinian = self.grid[violent_y][violent_x]
        #    self.relocate_palestinian(violent_palestinian, furthest_empty)

    def relocate_palestinian(self, palestinian, destination):
        #print ("Relocating Palestinian in ", palestinian.pos, "To somehwhere near ", destination)
        visible_spots = self.grid.get_neighborhood(destination,
                                                        moore=True, radius=palestinian.vision)
        nearest_empty = self.find_nearest_empty(destination, visible_spots)
        #print("First Nearest empty to ", palestinian.pos, " Is ", nearest_empty)
        if (nearest_empty):
            self.grid.move_agent(palestinian, nearest_empty)
        else:
            #print ("Moveing to random empty")
            if (self.grid.exists_empty_cells()):
                self.grid.move_to_empty(palestinian)
            else:
                return False

        return True

    def find_nearest_empty(self, pos, neighborhood):
        nearest_empty = None
        sorted_spots = self.sort_neighborhood_by_distance(pos, neighborhood)
        index = 0
        while (nearest_empty is None and index < len(sorted_spots)):
            if self.grid.is_cell_empty(sorted_spots[index]):
                nearest_empty = sorted_spots[index]
            index += 1

        return nearest_empty

    def find_furthest_empty_or_palestinian(self, pos, neighborhood):
        furthest_empty = None
        sorted_spots = self.sort_neighborhood_by_distance(pos, neighborhood)
        sorted_spots.reverse()
        index = 0
        while (furthest_empty is None and index < len(sorted_spots)):
            spot = sorted_spots[index]
            if self.grid.is_cell_empty(spot) or self.grid[spot[1]][spot[0]].breed == "Palestinian" :
                furthest_empty = sorted_spots[index]
            index += 1

        return furthest_empty



    def sort_neighborhood_by_distance(self, from_pos, neighbor_spots):
        from_x, from_y = from_pos
        return sorted(neighbor_spots, key = lambda spot: self.eucledean_distance(from_x, spot[0], from_y, spot[1], self.grid.width, self.grid.height))


    def eucledean_distance(self, x1,x2,y1,y2,w,h):
        # http://stackoverflow.com/questions/2123947/calculate-distance-between-two-x-y-coordinates
        return math.sqrt(min(abs(x1 - x2), w - abs(x1 - x2)) ** 2 + min(abs(y1 - y2), h - abs(y1-y2)) ** 2)
        

    def step(self):
        """
        Advance the model by one step and collect data.
        """
        self.violence_count = 0
      #  for i in range(100):
        self.schedule.step()
        self.total_violence += self.violence_count
      #  average = self.violence_count / 100
        #print("Violence average %f " % average)
        print("Total Violence: ", self.total_violence)
       # if (average < 0.001):
       #     self.dc.collect(self)
       #     self.running = False
       #     print("Done")
    #if self.iteration > self.max_iters:
    #    self.running = False
