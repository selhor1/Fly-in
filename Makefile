install:
	pip install -r requirements.txt

run:
	@python3 main.py $(FILE)

debug:
	@python3 -m pdb main.py $(FILE)

clean:
	@rm -rf __pycache__
	@rm -rf .mypy_cache

lint:
	python3 -m flake8 .
	python3 -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
