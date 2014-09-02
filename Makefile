PYTHONPATH=.
NOSECMD='nosetests'

.PHONY: test download_symbols get_history

test:
	$(NOSECMD) -sv test/

download_symbols:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_symbols.py

get_history:
	PYTHONPATH=$(PYTHONPATH) python jobs/get_history.py
