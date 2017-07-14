import logging
import numpy as np
from stock.optimize.random_search import rs
import stock.trade.report
import stock.strategy.volup

logger = logging.getLogger("jobs.find_optimum_grid")

start = '2016-07-01'
end = '2017-06-30'
def sample_loss(param):
    strategy = stock.strategy.volup.VolupStrategy(start, end,
        **param)
    strategy.run()
    report = stock.trade.report.Report()
    result = report.get_summary()
    if result.max_drawdown == 0.0:
        return 0.0
    else:
        return result.profit / result.max_drawdown

uppers = np.arange(0.3, 0.9, 0.1)
vol_quants =np.arange(0.85, 0.95, 0.01)
targets = np.arange(0.05, 0.15, 0.1)
increase_thrds = np.arange(0.05, 0.10, 0.1)
param_grid = {
    "upper": uppers,
    "vol_quant": vol_quants,
    "target": targets,
    "increase_thrd": increase_thrds
}
print param_grid
result = rs.search(sample_loss=sample_loss,
    param_grid=param_grid)
result.sort(key=lambda x: x[1], reverse=True)
logger.info(result)
