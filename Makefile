install:
	pip install -r requirements.txt

run:
	@python3 main.py map.txt

debug:
	@python3 -m pdb main.py map.txt

clean:
	@rm -rf __pycache__
	@rm -rf .mypy_cache

lint:
	./drone_env/bin/python3 -m flake8 . --exclude=drone_env
	./drone_env/bin/python3 -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude drone_env

lint-strict:
	./drone_env/bin/python3 -m flake8 . --exclude=drone_env
	./drone_env/bin/python3 -m mypy . --strict --exclude drone_env

venv:
	python3 -m venv drone_env
