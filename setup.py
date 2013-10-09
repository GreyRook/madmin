from setuptools import setup, find_packages

setup(
    name='madmin',
    description='Web based administration tool for mongodb',
    long_description=""""A tool to view and edit mongodb instances similar to PhpMyAdmin.\n
    MAdmin allows you to manage databases, collections and documents. """,
    version='0.1.1',
    author='Dominik Schacht',
    author_email='domschacht@gmail.com',
    install_requires=['rueckenwind==0.2.0', 'motor==0.1.1', 'PyMongo==2.5.0'],
    packages=find_packages(),
    include_package_data=True,
    classifiers= ['Development Status :: 3 - Alpha',
                  'Intended Audience :: Developers',
                  'Intended Audience :: System Administrators',
                  'License :: OSI Approved :: Apache Software License',
                  'Topic :: Database :: Front-Ends'],
)
