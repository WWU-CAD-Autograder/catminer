import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="catminer",
    version="1.0",
    author="Jack Wilson",
    description="Data-mining tool for .CAT* (CATIA) files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WWU-CAD-Autograder/catminer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
    ],
    install_requires=['pyvba', 'pywin32'],
    entry_points={
        'console_scripts': ['catminer = catminer.__main__:main']
    },
    python_requires='>=3',
)
