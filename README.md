model-data
==========

A system for accessing arbitrary data from an arbitrary model

This is meant as an efficient framework for running computational models and
accessing the resulting data.  The idea is that the user can ask for 
certain data from a model, and the system will reply with that data.  For
example, you can say:

```python
md = ModelData()
print md.get('PredatorPrey, seed=10, step=20, info=['x', 'y'])
```

and the system should return the x and y values from a PredatorPrey model
(as defined in the "models" package) at simulation step 20, using a random 
number seed of 10.  

The important trick here is that the system should do some sort of caching of
information in some form of database.  Right now, the reference implementation
does not store any information at all -- the model is run from scratch for
every call to ```get```.  This is horribly inefficient.

To complicate matters, you can also specify a ```params``` argument.  This is
a dictionary used to adjust the parameters in the model.  These parameters
are generally set at the beginning of the model run, but if any of the 
specified parameters are callable, then they are called with the current step
number to give a particular value of that parameter at that moment.  That is,
parameters can change during a model run.  

For example, the following will set ```x=1``` and ```y=2``` at the beginning
of the model run:

```python
md = ModelData()
print md.get('PredatorPrey, seed=10, step=20, info=['x', 'y'], 
             params=dict(x=1, y=2)
```

And the following will do the same, but will also have r be 1 for the first
20 time steps and 2 after that:

```python
md = ModelData()

def r(step):
    if step<20: return 1
    else: return 2
print md.get('PredatorPrey, seed=10, step=20, info=['x', 'y'], 
             params=dict(x=1, y=2, r=r)
```


The goal of this project is to improve the existing implementation to
efficiently support these sorts of calls.  In addition, we would also like
to support the following:

 - specify a list of seeds (and get data back for all of them)
 
 ```python
print md.get('PredatorPrey, seed=[1, 9, 10, 11], step=20, info=['x','y'])
 ```
 
 - specify a list of steps 
 
 ```python
print md.get('PredatorPrey, seed=10, steps=[0, 5, 10, 15, 20], info=['x','y'])
 ```
 
 - both of the above at the same time
 
 Ideally, this sort of use could take advantage of parallel computing, running
 the different seeds on different cores or machines, since they are independent.
 
 In an efficient implementation, note that Models can be kept around (they
 should even be serializable).  This means that there may be situations where
 if someone changes a parameter setting after time step 100, the system might
 still have a version of the model kept around that's sitting at time step 80
 that could be run instead, rather than starting a new model from the
 beginning.  This is likely to be a common usage scenario:
 
 ```python
 print md.get('PredatorPrey, seed=10, step=200, info=['x','y'],
              params=dict(r=1))
 print md.get('PredatorPrey, seed=10, step=200, info=['x','y'],
              params=dict(r=lambda step: 1 if step<100 else 2))
 ``` 
 