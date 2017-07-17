import numpy as np
from multiprocessing import Pool
from sklearn.model_selection import ParameterGrid

def search(sample_loss, param_grid, percent=0.3):
    params = ParameterGrid(param_grid)
    num = len(params)
    size = int(num*percent)

    pool = Pool(20)
    rand_ids = np.random.randint(num, size=size)
    async_res = []
    for i in rand_ids:
        param = params[i]
        res = pool.apply_async(sample_loss, (param,))
        async_res.append({"param": param, "res": res})

    result = []
    for i in range(len(async_res)):
        res = async_res[i]["res"]
        param = async_res[i]["param"]
        loss = res.get()
        result.append([param, loss])
    return result

