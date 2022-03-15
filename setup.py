from importlib.metadata import entry_points
from setuptools import setup
from dockerps import __version__

setup(
    name="dockerps",
    version=__version__,
    short_description="dockerps",
    long_description="dockerps",
    packages=[
        "dockerps",
    ],
    include_package_data=True,
    package_data={'': ['*.yml']},
    entry_points={
        "console_scripts":[
            "dockerps=dockerps:__main__"
            ]
    },
    url='https://github.com/JeanMaximilienCadic/dockerps.git',
    license='MIT',
    author='CADIC Jean-Maximilien',
    python_requires='>=3.8',
    install_requires=[r.rsplit()[0] for r in open("requirements.txt")],
    author_email='contact@cadic.jp',
    description='dockerps',
    platforms="linux_debian_10_x86_64",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)
