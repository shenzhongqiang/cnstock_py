PYTHONPATH=.
NOSECMD='nosetests'

.PHONY: test download_symbols get_history get_realtime

init:
	@if test ! -d html; then mkdir html; fi
test:
	$(NOSECMD) -sv test/

download_symbols:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_symbols.py

get_history:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_history.py

get_realtime:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_realtime.py

filter_realtime: init
	PYTHONPATH=$(PYTHONPATH) python jobs/filter_realtime.py

filter_backtest: init
	PYTHONPATH=$(PYTHONPATH) python jobs/filter_backtest.py
