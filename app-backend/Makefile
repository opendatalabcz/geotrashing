VENV=. venv/bin/activate

# Python venv environment
venv/bin/activate: requirements.txt
	test -d venv || python3 -m venv venv
	$(VENV); pip3 install -Ur requirements.txt
	touch venv/bin/activate

venv: $(VENV)

instance:
	mkdir instance

setup: venv instance

deploy: venv
	$(VENV); gunicorn -b ${HOST_IP}:${HOST_PORT} main:app

stop:
	kill $$(cat geotrash_server.pid)

test: venv
	@echo "Running flask locally" 
	@echo 'RUN THIS COMMANDS:'
	$(VENV); FLASK_APP="main.py" FLASK_ENV=development flask run
