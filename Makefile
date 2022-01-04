all: test symbols history realtime upper_shadow
PYTHONPATH=.
NOSECMD='nosetests'

.PHONY: all

test:
	$(NOSECMD) -sv test/

symbol:
	$(info get symbol)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --symbol

realtime: symbol
	$(info get realtime)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --realtime

history: symbol
	$(info get history)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --hist

tick: realtime
	$(info get tick)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/get_tick.py

conceptindustry:
	$(info get concept and industry)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --concept
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --industry

kaipan:
	$(info get kaipan)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/get_kaipan.py
