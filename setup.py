from setuptools import setup

setup(name='pycbc',
      setup_requires='setupmeta',
      include_package_data=True,
      package_data={'pycbc': ['templates/*']},
      zip_safe=False,
      )
