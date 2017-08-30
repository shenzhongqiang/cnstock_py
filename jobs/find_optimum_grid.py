import traceback
import logging
import numpy as np
from stock.optimize.grid_search import gs
import stock.trade.report
import stock.strategy.gap_thrd

logger = logging.getLogger("jobs.find_optimum_grid")

start = '2016-07-01'
end = '2017-07-01'
def sample_loss(param):
    try:
        strategy = stock.strategy.gap_thrd.GapStrategy(start, end,
            **param)
        result = strategy.run()
        if result.max_drawdown == 0.0:
            return 0.0
        else:
            return result.profit / result.max_drawdown
    except Exception, e:
        print str(e)
        traceback.print_exc()

thrd = np.arange(0.001, 0.006, 0.001)
pred_thrd = np.arange(0.01, 0.05, 0.005)
param_grid = {
    "thrd": thrd,
    "pred_thrd": pred_thrd
}
result = gs.search(sample_loss=sample_loss,
    param_grid=param_grid)
result.sort(key=lambda x: x[1], reverse=True)
logger.info(result)
