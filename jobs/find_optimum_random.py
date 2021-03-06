import traceback
import logging
import numpy as np
from stock.optimize.random_search import rs
import stock.trade.report
import stock.strategy.volup

logger = logging.getLogger("jobs.find_optimum_grid")

start = '2016-07-01'
end = '2017-06-30'
def sample_loss(param):
    try:
        strategy = stock.strategy.volup.VolupStrategy(start, end,
            **param)
        result = strategy.run()
        if result.max_drawdown == 0.0:
            return 0.0
        else:
            return result.profit / result.max_drawdown
    except Exception, e:
        print str(e)
        traceback.print_exc()

uppers = np.arange(0.03, 0.09, 0.03)
vol_quants =np.arange(0.85, 0.95, 0.03)
targets = np.arange(0.05, 0.15, 0.03)
increase_thrds = np.arange(0.05, 0.10, 0.02)
param_grid = {
    "upper": uppers,
    "vol_quant": vol_quants,
    "target": targets,
    "increase_thrd": increase_thrds
}
result = rs.search(sample_loss=sample_loss,
    param_grid=param_grid)
result.sort(key=lambda x: x[1], reverse=True)
logger.info(result)
