BLACK=black -l 120 -t py36 app.py infx lambda
black:
	${BLACK}

lint:
	${BLACK} --check
	flake8 app.py lambda/ infx/

mypy:
	mypy -m app -p infx
	mypy lambda

unit:
	pytest tests/
	pytest lambda/tests

test: lint mypy unit
