from importlib.metadata import entry_points
from setuptools import setup
from dockerich import __version__

setup(
    name="dockerich",
    version=__version__,
    short_description="dockerich",
    long_description="dockerich",
    packages=[
        "dockerich",
    ],
    include_package_data=True,
    package_data={'': ['*.yml']},
    entry_points={
        "console_scripts":[
            "dockerich=dockerich:__main__"
            ]
    },
    url='https://github.com/JeanMaximilienCadic/dockerich.git',
    license='MIT',
    author='CADIC Jean-Maximilien',
    python_requires='>=3.8',
    install_requires=[r.rsplit()[0] for r in open("requirements.txt")],
    author_email='contact@cadic.jp',
    description='dockerich',
    platforms="linux_debian_10_x86_64",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)
