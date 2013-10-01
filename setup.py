from setuptools import setup, find_packages

setup(
    name='madmin',
    version='0.0.1',
    install_requires=['rueckenwind==0.2.0', 'motor==0.1.1', 'PyMongo==2.5.0'],
    packages=find_packages(),
    include_package_data=True,
)
