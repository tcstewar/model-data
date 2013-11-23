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

import random
import math
import modex

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
import random
import math
import modex

log = modex.log()

class Person:
    def __init__(self):
        self.friends = []
        self.weight = dict(
            price = weight_high * random.uniform(0.5, 1.5),
            efficiency = weight_med * random.uniform(0.5, 1.5),
            lifetime =  weight_low * random.uniform(0.5, 1.5),
            friends =  weight_med * random.uniform(0.5, 1.5),
            cri =  weight_med * random.uniform(0.5, 1.5),
            output =  weight_low * random.uniform(0.5, 1.5),
            color =  weight_med * random.uniform(0.5, 1.5),
            opinion_type =  weight_med * random.uniform(0.5, 1.5),
            opinion_brand =  weight_low * random.uniform(0.5, 1.5),
            opinion_model =  weight_low * random.uniform(0.5, 1.5),
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
        
        
        is_cfl = random.random() < adopters_of_cfl
        
        count = int(random.uniform(5, 65))
        
        while len(self.luminaires)<count:
            if random.random()< halogen_prob:
                type = 'Halogen'
            else:    
                type = 'Incandescent'
                if is_cfl:
                    if random.random() < cfl_lamps_for_adopters:
                        type = 'CFL'
                        
            if type == 'Incandescent' or type=='CFL':
                options = []
                for lum in lum_distribution:
                    if lum['shape']=='Pear':
                        for i in range(lum['value']):
                            options.append(lum)
                option = random.choice(options)
            elif type == 'Halogen':
                options = []
                for lum in lum_distribution:
                    for i in range(lum['value']):
                        options.append(lum)
                option = random.choice(options)


                        
            
            lamp = lamps.pick(type, option['socket'], option['shape'])
            
            if lamp is not None:
                self.add_lamp(lamp)
                
    def add_lamp(self, lamp):            
        mine = dict()
        mine.update(lamp)
        u = mine['lifetime_uncertainty']
        mine['expected_lifetime'] = mine['lifetime']
        mine['lifetime'] = mine['lifetime']*random.uniform(1.0-u, 1.0+u)
        mine['lifetime'] = mine['lifetime']*random.uniform(0, 1)
        mine['usage'] = random.uniform(0, max_usage_per_week)
       
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
        
        change_socket = random.random()<change_socket_prob
        
        options = []
        for lamp in lamps.lamps:
            if change_socket or (lamp['socket']==socket and lamp['shape']==shape):
                options.append(lamp)
                
        if len(options)==0:
            print 'cannot find', socket, shape
        
        utility = [decision_noise*math.log(1.0/random.random()-1.0)]*len(options)
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
                    u *= lamps.price_scale(options[i]['type'])
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
    def __init__(self, size):
        self.people = [Person() for i in range(size)]
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
    def __init__(self):
        self.lamps = []
        self.steps = 0
        for line in open('lamps.csv', 'U').readlines():
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
        random.shuffle(lamp_list)
        for lamp in lamp_list:
            if lamp['shape']==shape and lamp['socket']==socket and lamp['type']==type:
                return lamp
        return None 
    def step(self):
        self.steps += 1
    def price_scale(self, type):
        return math.exp(-self.steps/float(price_halflife[type]))
                
        
class Intervention:
    def __init__(self, lamps, people):
        self.lamps = lamps
        self.people = people
    
    def step(self):
        pass
        
class BanIntervention(Intervention):
    def __init__(self, lamps, people, type, years):
        Intervention.__init__(self, lamps, people)
        self.type = type
        self.years = years
        self.time = 0
        self.banlamps = [lamp for lamp in self.lamps.lamps if lamp['type']==type]
        self.banlamps.sort(key = lambda x: -x['power']/x['output'])
        self.steps_per_ban = int(years*52/len(self.banlamps))
    
    def step(self):
        self.time += 1
        if self.time%self.steps_per_ban == 0 and len(self.banlamps)>0:
            self.lamps.lamps.remove(self.banlamps[0])
            print 'ban', self.time, self.banlamps[0]
            del self.banlamps[0]

class TaxIntervention(Intervention):
    def __init__(self, lamps, people, type, years, max_amount):
        Intervention.__init__(self, lamps, people)
        self.type = type
        self.years = years
        self.time = 0
        self.max_amount = max_amount
        self.affected = [lamp for lamp in self.lamps.lamps if lamp['type']==type]
        self.dtax = max_amount/(years*52)
        
    def step(self):
        self.time += 1
        if self.time < self.years*52: 
            for lamp in self.affected:
                lamp['price'] += self.dtax
            
class SubsidyIntervention(Intervention):
    def __init__(self, lamps, people, type, years, max_amount):
        Intervention.__init__(self, lamps, people)
        self.type = type
        self.years = years
        self.time = 0
        self.max_amount = max_amount
        self.affected = [lamp for lamp in self.lamps.lamps if lamp['type']==type]
        self.dsubsidy = max_amount/(years*52)
        self.base = [lamp['price'] for lamp in self.affected]
        for lamp in self.affected:
            lamp['price'] *= (1.0-max_amount)
        
    def step(self):
        self.time += 1
        if self.time < self.years*52: 
            for i, lamp in enumerate(self.affected):
                lamp['price'] += self.dsubsidy*self.base[i]
            
            
    
        
lamps = Lamps()
    
people = People(pop_size) 

interventions = [
    #BanIntervention(lamps, people, 'Incandescent', 5),
    #TaxIntervention(lamps, people, 'Incandescent', 5, 200.0),
    #SubsidyIntervention(lamps, people, 'Incandescent', 5, 0.33),
    ]

type_incandescent = []
type_cfl = []
type_halogen = []
type_led = []
time = []
for y in range(years):
    type_incandescent.append(people.get_count(type='Incandescent'))
    type_cfl.append(people.get_count(type='CFL'))    
    type_halogen.append(people.get_count(type='Halogen'))    
    type_led.append(people.get_count(type='LED'))    
    time.append(y)
    for w in range(52):
        people.step()
        lamps.step()
        for interv in interventions:
            interv.step()
    
    log.time = y
    log.count_incandescent = people.get_count(type='Incandescent')
    log.count_cfl = people.get_count(type='CFL')
    log.count_halogen = people.get_count(type='Halogen')
    log.count_led = people.get_count(type='LED')
        
if show_graph:    
    import pylab
    pylab.plot(time, type_incandescent, label='Incandescent')    
    pylab.plot(time, type_cfl, label='CFL') 
    pylab.plot(time, type_halogen, label='Halogen')       
    pylab.plot(time, type_led, label='LED')       
    pylab.legend()
    pylab.show()
    