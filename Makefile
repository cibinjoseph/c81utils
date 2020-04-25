all:
	python3 setup.py sdist bdist_wheel
	twine check dist/*

upload_test:
	twine upload --repository testpypi dist/*

upload:
	twine upload --repository pypi dist/*

clean:
	rm -rf build c81utils.egg-info __pycache__ dist
