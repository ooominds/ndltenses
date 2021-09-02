
from setuptools import setup, Extension

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ndl_tense",
    version="0.0.2",
    license = 'MIT',
    author="Tekevwe Kwakpovwe",
    author_email="t.kwakpovwe@gmail.com",
    description="A package for training NDL models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    download_url= "https://github.com/ooominds/ndltenses/archive/refs/tags/test_1.tar.gz",
    keywords=["NDL", "Tense", "NLP"],
    install_requires=[
          'numpy',
          'h5py',
          'pandas',
          'pyndl',
          'sklearn',
          'keras',
          'xarray',
          'matplotlib',
          'nltk'
    ],
    #project_urls={
    #    "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    #},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["ndl_tense"],
)
