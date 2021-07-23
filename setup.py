import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wepycon", # Replace with your own username
    version="0.0.1",
    author="Sven Kleinert",
    author_email="kleinert@iqo.uni-hannover.de",
    description="laser beam profiler employing home build beam cameras",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.iqo.uni-hannover.de/morgner/wepycon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "opencv-python>=4.5",
        #"pyside2>=5.14.1", #toggle if you want to use pyside2 instead of PyQt5
        "PyQt5>=5.12.3",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "pyvisa-py>=0.5.0",
        "git+https://github.com/python-zwoasi/python-zwoasi#egg=python-zwoasi-0.1.0",

    ],
    entry_points={
        "console_scripts":[ "wePycon = wepycon.main:main" ]
    },

    python_requires='>=3.6',
)
