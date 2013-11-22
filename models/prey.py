from .model import Model

class PredatorPrey(Model):
    b = 1.0
    p = 1.0
    r = 1.0
    d = 1.0
    dt = 0.01
    noise = 0.1
    x = 1.0
    y = 0.1
    
    def step(self):
        f = self.b - self.p*self.y + self.rng.normal(0, self.noise)
        g = self.r*self.x - self.d + self.rng.normal(0, self.noise)
        self.x = self.x + self.x*f*self.dt
        self.y = self.y + self.y*g*self.dt
        if self.x<0: self.x = 0
        if self.y<0: self.y = 0
        
    def info(self):
        return dict(x=self.x, y=self.y)