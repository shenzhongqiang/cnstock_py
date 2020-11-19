all: test symbols history realtime upper_shadow
PYTHONPATH=.
NOSECMD='nosetests'

.PHONY: all

test:
	$(NOSECMD) -sv test/

symbols:
	$(info get symbols)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/get_symbols.py

realtime: symbols
	$(info get realtime)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/get_realtime.py

history: realtime
	$(info get history)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/get_history.py

tick: realtime
	$(info get tick)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/get_tick.py

upper_shadow: history
	$(info get upper shadow)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python stock/quant/upper_shadow.py

opengap: realtime tick
	$(info get opengap)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/filter_opengap.py

afterclose: realtime tick
	$(info get afterclose)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/filter_afterclose.py

hot_concept: history
	$(info get hot concept)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python stock/quant/hot_concept.py

kaipan:
	$(info get kaipan)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/get_kaipan.py
