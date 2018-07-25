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

test_internet_access:
	@echo starting test access to site via internet 
	PYTHONPATH=rest python2 ./tests/access_test.py "http://spot.selfip.com:65000" "https://spot.selfip.com"

test_intranet_access:
	@echo starting test access to site via intranet
	PYTHONPATH=rest python2 ./tests/access_test.py "http://192.168.0.210" "http://192.168.0.211"

test_intranet0_access:
	@echo starting test access to site via intranet
	PYTHONPATH=rest python2 ./tests/access_test.py "http://192.168.0.210" 

test_all: | test_intranet_access test_internet_access

test:
	py.test tests 

.PHONY: init test





