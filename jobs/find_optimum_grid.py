import numpy as np
from stock.optimize.grid_search import gs
import stock.trade.report
import stock.strategy.ema

start = '2017-01-01'
end = '2017-01-30'
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

slows = range(5, 14, 1)
fasts = range(3, 11, 1)
param_grid = {"slow": slows, "fast": fasts}
result = gs.search(sample_loss=sample_loss,
    param_grid=param_grid)
print result
