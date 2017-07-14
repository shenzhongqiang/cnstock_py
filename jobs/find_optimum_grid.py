import logging
import numpy as np
from stock.optimize.grid_search import gs
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

slows = range(5, 16, 1)
fasts = range(3, 12, 1)
param_grid = {"slow": slows, "fast": fasts}
result = gs.search(sample_loss=sample_loss,
    param_grid=param_grid)
result.sort(key=lambda x: x[1], reverse=True)
logger.info(result)
