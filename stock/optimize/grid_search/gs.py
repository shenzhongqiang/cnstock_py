from sklearn.model_selection import ParameterGrid

def search(sample_loss, param_grid):
    params = ParameterGrid(param_grid)
    result = []
    for param in params:
        loss = sample_loss(param)
        result.append([param, loss])
    return result
