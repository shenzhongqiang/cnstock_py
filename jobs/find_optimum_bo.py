import logging
import numpy as np
from stock.optimize.bayesian_optimisation import gp
import stock.trade.report
import stock.strategy.volup

logger = logging.getLogger("jobs.find_optimum_grid")
start = '2016-06-01'
end = '2017-06-30'
def sample_loss(params):
    strategy = stock.strategy.volup.VolupStrategy(start, end,
        upper=params[0], vol_quant=params[1],
        target=params[2], increase_thrd=params[3])
    strategy.run()
    report = stock.trade.report.Report()
    result = report.get_summary()
    if result.max_drawdown == 0.0:
        return 0.0
    else:
        return result.profit / result.max_drawdown

bounds = np.array([[0.3,0.9], [0.85, 0.95], [0.5, 0.15], [0.5, 0.10]])
xp, yp = gp.bayesian_optimisation(n_iters=30,
    sample_loss=sample_loss,
    bounds=bounds,
    n_pre_samples=3,
    random_search=100000)

logger.info(xp, yp)
