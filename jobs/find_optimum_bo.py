import logging
import numpy as np
from stock.optimize.bayesian_optimisation import gp
import stock.trade.report
import stock.strategy.ema

logger = logging.getLogger("jobs.find_optimum_grid")
start = '2017-01-01'
end = '2017-01-30'
def sample_loss(params):
    strategy = stock.strategy.ema.EmaStrategy(start, end,
        fast=params[0], slow=params[1])
    strategy.run()
    report = stock.trade.report.Report()
    result = report.get_summary()
    if result.max_drawdown == 0.0:
        return 0.0
    else:
        return result.profit / result.max_drawdown

bounds = np.array([[3,10], [5, 20]])
xp, yp = gp.bayesian_optimisation(n_iters=30,
    sample_loss=sample_loss,
    bounds=bounds,
    n_pre_samples=3,
    random_search=100000)

logger.info(xp, yp)
