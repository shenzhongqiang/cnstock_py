import numpy as np
from sklearn.model_selection import ParameterGrid

def search(sample_loss, param_grid, percent=0.3):
    params = ParameterGrid(param_grid)
    result = []
    num = len(params)
    size = int(num*percent)
    rand_ids = np.random.randint(num, size=size)
    for i in rand_ids:
        param = params[i]
        loss = sample_loss(param)
        result.append([param, loss])
    return result

