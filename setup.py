from setuptools import setup

version = '0.1'

setup(
    name='c81utils',
    version=version,
    description='Library for working with C81 airfoil data',
    long_description='\n'.join([
        open('README.rst').read(),
        open('CHANGES.rst').read()
    ])
    keywords='c81',
    author='Cibin Joseph',
    author_email='cibinjoseph92@gmail.com',
    url='http://pypi.python.org/pypi/c81utils',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering'
    ],
    python_requires='>=3',
    include_package_data=True,
    zip_safe=True,
    install_requires=['numpy', 'scipy'],
    py_modules=['c81utils'],
    test_suite='test_c81utils.main'
)
