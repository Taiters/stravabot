BLACK=black -l 120 -t py36 app.py infx lambda
format:
	isort app.py infx lambda
	${BLACK}

lint:
	${BLACK} --check
	flake8 app.py lambda/ infx/

mypy:
	mypy -m app -p infx
	mypy lambda

unit:
	pytest tests/
	STRAVABOT_ENV=test pytest lambda/tests/unit

integration
	STRAVABOT_ENV=test pytest lambda/tests/integration

test: lint mypy unit
