from .model import Model

class PredatorPrey(Model):
    # define the parameters
    b = 1.0        # prey growth rate
    p = 1.0        # how much of the prey the predators kill
    r = 1.0        # growth rate of predators
    d = 1.0        # death rate of predators with no prey
    dt = 0.01      # size of time step
    noise = 0.1    # amount of randomness
    x = 1.0        # prey population
    y = 0.1        # predator population
    
    # move forward in time
    def step(self):
        # taken from http://www.scholarpedia.org/article/Predator-prey_model
        
        # change to prey population
        f = self.b - self.p*self.y + self.rng.normal(0, self.noise)  
        
        # change to predator population
        g = self.r*self.x - self.d + self.rng.normal(0, self.noise)
        
        self.x = self.x + self.x*f*self.dt
        self.y = self.y + self.y*g*self.dt
        
        # don't go to negative numbers
        if self.x<0: self.x = 0
        if self.y<0: self.y = 0
        
    # report data out of the model    
    #   this is the data that could be graphed or shown in some other system
    def info(self):
        return dict(prey=self.x, predator=self.y)