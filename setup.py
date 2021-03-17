import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name='cyclic-toposort',
    version='1.0.0',
    author='Paul Pauls',
    author_email='mail@paulpauls.de',
    description='A sorting algorithm for directed cyclic graphs that results in a sorting with minimal cyclic edges',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/PaulPauls/cyclic-toposort",
    packages=setuptools.find_packages(),
    include_package_data=True,
    py_modules=['cyclic_toposort'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>= 3.0',
)
