# Helpers for building and uploading the package.
# Update the version number in c81utils/__init__.py, then run make.

all:
	make dist
	@echo "Now run 'make upload' to upload"

dist:
	python3 -m build
	twine check dist/*

upload_test:
	twine upload --repository testpypi dist/*

upload: dist/
	twine upload dist/*

test:
	python3 -m pytest

clean:
	rm -rf build c81utils.egg-info __pycache__ dist .pytest_cache
