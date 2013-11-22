import models

class ModelData:
    def __init__(self):
        pass
        
    def get(self, name, seed, step, info, params):
        model = getattr(models, name)(seed)
        
        for k,v in params.items():
            if not callable(v):
                setattr(model, k, v)
                del params[k]
        
        for i in range(step):
            for k, v in params.items():
                setattr(model, k, v(i))
            model.step()
            
        all_info = model.info()
        return {k:v for k,v in all_info.items() if k in info}
    
    
if __name__ == '__main__':
    import math
    md = ModelData()
    print md.get('PredatorPrey', 1, 10, ['x', 'y'], dict(x=2, y=2, d=lambda t: 2+math.sin(0.01*t)))