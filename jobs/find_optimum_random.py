import logging
import numpy as np
from stock.optimize.random_search import rs
import stock.trade.report
import stock.strategy.ema

logger = logging.getLogger("jobs.find_optimum_grid")

start = '2016-07-01'
end = '2017-06-30'
def sample_loss(param):
    strategy = stock.strategy.ema.EmaStrategy(start, end,
        **param)
    strategy.run()
    report = stock.trade.report.Report()
    result = report.get_summary()
    if result.max_drawdown == 0.0:
        return 0.0
    else:
        return result.profit / result.max_drawdown

slows = range(5, 7, 1)
fasts = range(3, 5, 1)
targets = np.arange(1, 1.2, 0.01)
param_grid = {"slow": slows, "fast": fasts, "target": targets}
result = rs.search(sample_loss=sample_loss,
    param_grid=param_grid)
result.sort(key=lambda x: x[0], reverse=True)
logger.info(result)
