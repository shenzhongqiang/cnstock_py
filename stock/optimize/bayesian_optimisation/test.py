import numpy as np
import gp
import plotters
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from sklearn.datasets import make_classification

data, target = make_classification(n_samples=2500,
    n_features=45,
    n_informative=15,
    n_redundant=5)

def sample_loss(params):
    return cross_val_score(SVC(C=10 ** params[0], gamma=10 ** params[1], random_state=12345),
       X=data, y=target, scoring='roc_auc', cv=3).mean()

lambdas = np.linspace(1, -4, 5)
gammas = np.linspace(1, -4, 4)

# We need the cartesian combination of these two vectors
param_grid = np.array([[C, gamma] for gamma in gammas for C in lambdas])
real_loss = []
for params in param_grid:
    real_loss.append(sample_loss(params))
    print len(real_loss)

# The maximum is at:
print param_grid[np.array(real_loss).argmax(), :]
bounds = np.array([[-4, 1], [-4, 1]])
xp, yp = gp.bayesian_optimisation(n_iters=30,
    sample_loss=sample_loss,
    bounds=bounds,
    n_pre_samples=3,
    random_search=100000)

print xp,yp

