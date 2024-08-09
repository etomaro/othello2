from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("ray_calc_next_states_cython.pyx")
)