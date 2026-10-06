.PHONY: help install test run lint chsh clean docker-build docker-run

help:
	@echo "Targets: install test run lint chsh clean docker-build docker-run"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	uvicorn server:app --host 0.0.0.0 --port 8000 --reload

lint:
	python -m compileall -q mqos/ server.py

chsh:
	@python -c "from mqos import run_chsh; import json; print(json.dumps(run_chsh(shots=1024, force_fresh=True), indent=2))"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache

docker-build:
	docker build -t mqos-tererai:2.1.0 .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env mqos-tererai:2.1.0
