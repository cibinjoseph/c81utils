all:
	python3 setup.py sdist bdist_wheel
	twine check dist/*
