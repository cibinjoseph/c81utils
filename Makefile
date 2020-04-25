all:
	python3 setup.py sdist bdist_wheel
	twine check dist/*

clean:
	rm -rf build c81utils.egg-info __pycache__ dist
