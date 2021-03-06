HOST=127.0.0.1
TEST_PATH=./
#export PYTHONPATH=src

# initv:
#  	( \
#        source /usr/local/bin/python3.6 activate; \
#        pip install -r requirements.txt; \
#     )

init:
	pip2 install -r requirements.txt 

test_internet:
	@echo starting test access to site via internet 
	PYTHONPATH=rest python2 ./tests/access_test.py "http://spot.selfip.com:65000" "https://spot.selfip.com"

test_intranet:
	@echo starting test access to site via intranet
	PYTHONPATH=rest python2 ./tests/access_test.py "http://192.168.0.210:2080" "http://192.168.0.211:2080"

test_intranet0:
	@echo starting test access to site via intranet
	PYTHONPATH=rest python2 ./tests/access_test.py "http://192.168.0.210:2080" 

test_intranet1:
	@echo starting test access to site via intranet
	PYTHONPATH=rest python2 ./tests/access_test.py "http://192.168.0.211:2080" 

test_localhost8000:
	@echo starting test access to site via intranet localhost
	PYTHONPATH=rest python2 ./tests/access_test.py "http://127.0.0.1:8000" 

test_localhost80:
	@echo starting test access to site via intranet localhost
	PYTHONPATH=rest python2 ./tests/access_test.py "http://127.0.0.1:80" 

test_msk:
	@echo starting test apidata.mos.ru
	PYTHONPATH=rest python2 ./tests/msk_test.py 

test_all: | test_intranet test_internet

test:
	py.test tests 

.PHONY: init test

