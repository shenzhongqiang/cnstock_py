all: test symbols history realtime upper_shadow
PYTHONPATH=.
NOSECMD='nosetests'

.PHONY: all

test:
	$(NOSECMD) -sv test/

symbol:
	$(info get symbol)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --symbol

realtime:
	$(info get realtime)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --realtime

history: symbol
	$(info get history)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/download.py --hist

pairs: history
	$(info get pairs)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/related.py --pairs

drift: pairs
	$(info get drift)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/related.py --pairs-drift

zhangting: realtime
	$(info get zhangting)
	PYTHONPATH=$(PYTHONPATH) .venv/bin/python jobs/related.py --zhangting

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
