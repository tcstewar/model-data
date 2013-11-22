import numpy as np

class Model:
    def __init__(self, seed):
        self.rng = np.random.RandomState(seed)
    
    def step(self):
        pass
        
    def info(self):
        return {}
        
        
        