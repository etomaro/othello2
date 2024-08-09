from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("env_for_anality_cython.pyx")
)