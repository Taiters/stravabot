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

test: lint mypy unit

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r lambda/requirements.txt
	pip install boto3
	npm install -g aws-cdk@1.109.0