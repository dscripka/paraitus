from setuptools import setup, find_packages

setup(
    name='paraitus',
    version='0.1',
    description='A simple, cross-platform, instant access interface for calling LLM APIs.',
    author='David Scripka',
    author_email='david.scripka@gmail.com',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        "pynput>=1.7.3,<2.0",
        "sv-ttk>=2.6.0,<3.0"
    ],
    entry_points={
        'console_scripts': [
            'paraitus=paraitus.start:main'
        ]
    }
)