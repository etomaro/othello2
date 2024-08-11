from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("ray_calc_next_states_cython.pyx")
)
setup(
    ext_modules=cythonize("env_for_anality_cython.pyx")
)
