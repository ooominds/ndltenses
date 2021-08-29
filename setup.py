
from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ndl_tense",
    version="0.0.1",
    license = 'MIT',
    author="Tekevwe Kwakpovwe",
    author_email="t.kwakpovwe@gmail.com",
    description="A package for training NDL models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    download_url= "https://github.com/ooominds/ndltenses/archive/refs/tags/test_2.tar.gz",
    keywords=["NDL", "Tense", "NLP"],
    install_requires=[            # I get to this in a second
          'numpy',
          'h5py',
          'ntpath',
          'pandas',
          'pyndl',
          'sklearn',
          'keras',
          'xarray',
          'matplotlib',
    ],
    #project_urls={
    #    "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    #},
    #classifiers=[
    #    "Programming Language :: Python :: 3",
    #    "License :: OSI Approved :: MIT License",
    #    "Operating System :: OS Independent",
    #],
    packages=["ndl_tense"],
    python_requires=">=3.6",
)
