import traceback
import logging
import numpy as np
from stock.optimize.grid_search import gs
import stock.trade.report
import stock.strategy.index_bounce

logger = logging.getLogger("jobs.find_optimum_grid")

start = '2010-01-01'
end = '2017-07-01'
def sample_loss(param):
    try:
        strategy = stock.strategy.index_bounce.IndexStrategy(start, end,
            **param)
        result = strategy.run()
        if result.max_drawdown == 0.0:
            return 0.0
        else:
            return result.profit / result.max_drawdown
    except Exception, e:
        print str(e)
        traceback.print_exc()

sl_ratio = np.arange(0.005, 0.02, 0.001)
tp_ratio = np.arange(0.02, 0.03, 0.001)
param_grid = {
    "sl_ratio": sl_ratio,
    "tp_ratio": tp_ratio,
}
result = gs.search(sample_loss=sample_loss,
    param_grid=param_grid, n_jobs=1)
result.sort(key=lambda x: x[1], reverse=True)
logger.info(result)
