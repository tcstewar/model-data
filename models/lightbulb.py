from .model import Model

import math

class Person:
    def __init__(self, model):
        self.friends = []
        self.model = model
        self.weight = dict(
            price = self.model.weight_high * model.rng.uniform(0.5, 1.5),
            efficiency = self.model.weight_med * model.rng.uniform(0.5, 1.5),
            lifetime =  self.model.weight_low * model.rng.uniform(0.5, 1.5),
            friends =  self.model.weight_med * model.rng.uniform(0.5, 1.5),
            cri =  self.model.weight_med * model.rng.uniform(0.5, 1.5),
            output =  self.model.weight_low * model.rng.uniform(0.5, 1.5),
            color =  self.model.weight_med * model.rng.uniform(0.5, 1.5),
            opinion_type =  self.model.weight_med * model.rng.uniform(0.5, 1.5),
            opinion_brand =  self.model.weight_low * model.rng.uniform(0.5, 1.5),
            opinion_model =  self.model.weight_low * model.rng.uniform(0.5, 1.5),
            )
        self.opinions = dict(
            type = dict(),
            brand = dict(),
            model = dict(),
            )
        self.luminaires = []
        self.init_luminaires()
   
    def init_luminaires(self):
        # TODO: fix this distribution to (Bartlett 1993)
        
        
        is_cfl = self.model.rng.rand() < self.model.adopters_of_cfl
        
        count = int(self.model.rng.uniform(5, 65))
        
        while len(self.luminaires)<count:
            if self.model.rng.rand()< self.model.halogen_prob:
                type = 'Halogen'
            else:    
                type = 'Incandescent'
                if is_cfl:
                    if self.model.rng.rand() < self.model.cfl_lamps_for_adopters:
                        type = 'CFL'
                        
            if type == 'Incandescent' or type=='CFL':
                options = []
                for lum in self.model.lum_distribution:
                    if lum['shape']=='Pear':
                        for i in range(lum['value']):
                            options.append(lum)
                option = self.model.rng.choice(options)
            elif type == 'Halogen':
                options = []
                for lum in self.model.lum_distribution:
                    for i in range(lum['value']):
                        options.append(lum)
                option = self.model.rng.choice(options)


                        
            
            lamp = self.model.lamps.pick(type, option['socket'], option['shape'])
            
            if lamp is not None:
                self.add_lamp(lamp)
                
    def add_lamp(self, lamp):            
        mine = dict()
        mine.update(lamp)
        u = mine['lifetime_uncertainty']
        mine['expected_lifetime'] = mine['lifetime']
        mine['lifetime'] = mine['lifetime']*self.model.rng.uniform(1.0-u, 1.0+u)
        mine['lifetime'] = mine['lifetime']*self.model.rng.uniform(0, 1)
        mine['usage'] = self.model.rng.uniform(0, self.model.max_usage_per_week)
       
        self.luminaires.append(mine)
            
    def update_opinion(self, lamp):
        
        ot = self.opinions['type'].get(lamp['type'], 0)
        om = self.opinions['model'].get(lamp['model'], 0)
        ob = self.opinions['brand'].get(lamp['brand'], 0)
        
        positive = lamp['expected_lifetime']<0
        if positive:
            ot += 0.1 if ot>0 else 0.2
            om += 0.1 if om>0 else 0.2
            ob += 0.1 if ob>0 else 0.2
        else:
            ot -= 0.3
            om -= 0.3
            ob -= 0.3

        self.opinions['type'][lamp['type']] = max(-1, min(ot, 1))
        self.opinions['model'][lamp['model']] = max(-1, min(om, 1))
        self.opinions['brand'][lamp['brand']] = max(-1, min(ob, 1))

    def step(self):  # one week
        for lamp in self.luminaires[:]:
            lamp['lifetime'] -= lamp['usage']
            lamp['expected_lifetime'] -= lamp['usage']
            if lamp['lifetime'] < 0:
                self.update_opinion(lamp)
                self.replace(lamp)
    
    def replace(self, lamp):   
        self.luminaires.remove(lamp)
        socket = lamp['socket']
        shape = lamp['shape']
        
        change_socket = self.model.rng.rand()<self.model.change_socket_prob
        
        options = []
        for lamp in self.model.lamps.lamps:
            if change_socket or (lamp['socket']==socket and lamp['shape']==shape):
                options.append(lamp)
                
        if len(options)==0:
            print 'cannot find', socket, shape
        
        utility = [self.model.decision_noise*math.log(1.0/self.model.rng.rand()-1.0)]*len(options)
        for feature in ['price', 'efficiency', 'lifetime', 'cri', 'color', 'output']:            
            values = [opt[feature] for opt in options]
            minv = min(values)
            maxv = max(values)
            midv = (minv + maxv)/2
            for i, v in enumerate(values):
                u = (v-midv)/(maxv-midv) if (maxv!=minv) else 0.5   
                if feature in ['price', 'color']:
                    u = -u
                if feature == 'price':
                    u *= self.model.lamps.price_scale(options[i]['type'])
                utility[i] += u*self.weight[feature]
        for i, option in enumerate(options):
            utility[i] += self.opinions['model'].get(option['model'], 0) * self.weight['opinion_model']
            utility[i] += self.opinions['brand'].get(option['brand'], 0) * self.weight['opinion_brand']
            utility[i] += self.opinions['type'].get(option['type'], 0) * self.weight['opinion_type']
                
        #TODO: neighbour's opinions         
        
        choice = None
        for i, u in enumerate(utility):
            if choice is None or u>choice_u:
                choice = i
                choice_u = u
        
        new_lamp = options[i]
        self.add_lamp(new_lamp)


        
class People:
    def __init__(self, size, model):
        self.model = model
        self.people = [Person(model) for i in range(size)]
        #self.make_friends()
        
    def make_friends1(self):
        edges = 0
        minf = 0
        while minf < 15:
            for j, new in enumerate(self.people):
                for person in self.people[:j]:
                    num = len(person.friends)
                    denom = edges
                    p = float(num)/denom if denom > 0 else 1
                    
                    if random.random()<p:
                        new.friends.append(person)
                        person.friends.append(new)
                        edges += 1
            minf = min([len(p.friends) for p in self.people])            
        #print 'min:', minf, 'edges', edges
        #print [len(p.friends) for p in self.people]
        # TODO: is this legit?  Is this what they meant?

    def make_friends(self):
        count = 15
        edges = 0
        minf = 0
        print 'making scale-free network'
        for j, new in enumerate(self.people):
            if j <= count:
                for person in self.people[:j]:
                    new.friends.append(person)
                    person.friends.append(new)
            elif j>count:
                for i in range(count):
                    links = [len(p.friends) if p not in new.friends else 0 for p in self.people[:j]]
                    total = sum(links)
                    target = random.randrange(total)
                    index = 0
                    while target>0:
                        target -= links[index]
                        index += 1
                    person = self.people[index]    
                    new.friends.append(person)
                    person.friends.append(new)
                    
        minf = min([len(p.friends) for p in self.people])            
        print 'min graph degree:', minf
        print [len(p.friends) for p in self.people]
        
    def step(self):
        for p in self.people:
            p.step()
    
    def get_count(self, type=None):
        count = 0 
        for p in self.people:
            for lum in p.luminaires:
                if type is None or type==lum['type']:
                    count += 1
        return count            
                
class Lamps:
    def __init__(self, model):
        self.lamps = []
        self.model = model
        self.steps = 0
        for line in open('models/lamps.csv', 'U').readlines():
            line = line.strip().split(',')
            lamp = dict(
                type = line[0],
                model = line[1],
                lifetime = float(line[2]),
                lifetime_uncertainty = float(line[3]),
                output = float(line[4]),
                power = float(line[5]),
                cri = float(line[6]),
                color = float(line[7]),
                shape = line[8],
                socket = line[9],
                price = float(line[10]),
                year = int(line[11]),
                )
            lamp['efficiency'] = lamp['output'] / lamp['power']
            lamp['brand'] = lamp['model'].split()[0]
            
            self.lamps.append(lamp)    
    def pick(self, type, socket, shape):
        lamp_list = list(self.lamps)
        self.model.rng.shuffle(lamp_list)
        for lamp in lamp_list:
            if lamp['shape']==shape and lamp['socket']==socket and lamp['type']==type:
                return lamp
        return None 
    def step(self):
        self.steps += 1
    def price_scale(self, type):
        return math.exp(-self.steps/float(self.model.price_halflife[type]))



class Lightbulb(Model):
    # define the parameters
    weight_high = 4
    weight_med = 2
    weight_low = 1
    pop_size = 250
    adopters_of_cfl = 0.6
    cfl_lamps_for_adopters = 0.2
    halogen_prob = 0.2
    change_socket_prob = 0.15
    max_usage_per_week = 20
    decision_noise = 0
    years = 10
    show_graph = True
    price_halflife = {
        'Incandescent': 100*52,
        'CFL': 11*52,
        'Halogen': 50*52,
        'LED': 5*52,
        }
        

    lum_distribution = [
        dict(socket='E27', shape='Pear', value=70),
        dict(socket='E14', shape='Pear', value=7),
        dict(socket='GU10', shape='Reflector', value=15),
        dict(socket='G53', shape='Reflector', value=5),
        dict(socket='R7S', shape='Tubular', value=3),
        dict(socket='G24d2', shape='Reflector', value=0),
        ]    
        

                
        
            
    def __init__(self, seed):
        Model.__init__(self, seed)
        self.lamps = Lamps(self)
    
        self.people = People(self.pop_size, self) 
        
    def step(self):
        self.people.step() # update everyone's life
        self.lamps.step()  # burn out the lightbulbs
        
    def info(self):
        return dict(
            incandescent = self.people.get_count(type='Incandescent'),
            cfl = self.people.get_count(type='CFL'),
            halogen = self.people.get_count(type='Halogen'),
            led = self.people.get_count(type='LED'),
            )
        
