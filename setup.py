from setuptools import setup, find_packages

setup(
    name='dot20',
    version='0.1.19',
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open('requirements.txt')
    ]
)
