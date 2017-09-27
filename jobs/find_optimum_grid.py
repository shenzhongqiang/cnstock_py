import traceback
import logging
import numpy as np
from stock.optimize.grid_search import gs
import stock.trade.report
import stock.strategy.subnew2

logger = logging.getLogger("jobs.find_optimum_grid")

start = '2010-01-01'
end = '2017-07-01'
def sample_loss(param):
    try:
        strategy = stock.strategy.subnew2.SubnewStrategy(start, end, params=param)
        result = strategy.run()
        if result.max_drawdown == 0.0:
            return 0.0
        else:
            return result.profit / result.max_drawdown
    except Exception, e:
        print str(e)
        traceback.print_exc()

a = np.arange(0.05, 0.15, 0.05)
b = np.arange(0.1, 0.2, 0.1)
c = np.arange(0.01, 0.02, 0.01)
param_grid = {
    "sl_ratio": a,
    "tp_ratio": b,
    "open_gap": c
}
result = gs.search(sample_loss=sample_loss,
    param_grid=param_grid, n_jobs=1)
result.sort(key=lambda x: x[1], reverse=True)
logger.info(result)
