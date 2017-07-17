from multiprocessing import Pool
from sklearn.model_selection import ParameterGrid

def search(sample_loss, param_grid):
    params = ParameterGrid(param_grid)
    print "Total combinations: %d" % (len(params))
    pool = Pool(20)
    async_res = []
    for param in params:
        res = pool.apply_async(sample_loss, (param,))
        async_res.append({"param": param, "res": res})

    result = []
    for i in range(len(async_res)):
        res = async_res[i]["res"]
        param = async_res[i]["param"]
        loss = res.get()
        result.append([param, loss])
    return result
