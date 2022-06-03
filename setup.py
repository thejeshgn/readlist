import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="readlist",
    version="0.73",
    author="Thejesh GN",
    author_email="i@thejeshgn.com",
    description="The client for Readlist",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thejeshgn/readlist",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['docopt', 'requests','trafilatura'],
    python_requires='>=3.5',
    entry_points = {
        'console_scripts': ['readlist=src.readlist:main'],
    }
)
