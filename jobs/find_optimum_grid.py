import traceback
import logging
import numpy as np
from stock.optimize.grid_search import gs
import stock.trade.report
import stock.strategy.index_ma
import stock.strategy.index_break_high

logger = logging.getLogger("jobs.find_optimum_grid")

start = '2010-01-01'
end = '2017-07-01'
def sample_loss(param):
    try:
        strategy = stock.strategy.index_break_high.IndexStrategy(start, end,
            **param)
        result = strategy.run()
        if result.max_drawdown == 0.0:
            return 0.0
        else:
            return result.profit / result.max_drawdown
    except Exception, e:
        print str(e)
        traceback.print_exc()

a = range(7, 13, 1)
b = range(7, 13 ,1)
param_grid = {
    "high_days": a,
    "low_days": b,
}
result = gs.search(sample_loss=sample_loss,
    param_grid=param_grid, n_jobs=1)
result.sort(key=lambda x: x[1], reverse=True)
logger.info(result)
