PYTHONPATH=.
NOSECMD='nosetests'

.PHONY: test download_symbols get_history get_realtime

test:
	$(NOSECMD) -sv test/

download_symbols:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_symbols.py

get_history:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_history.py

get_realtime:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_realtime.py

filter:
	PYTHONPATH=$(PYTHONPATH) python jobs/filter.py
