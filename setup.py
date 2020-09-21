import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    author="Jack Wilson",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Win32 (MS Windows)",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
    ],
    description="Data-mining tool for .CAT* (CATIA) files.",
    entry_points={
        'console_scripts': ['catminer = catminer.__main__:main']
    },
    install_requires=['pyvba', 'tqdm'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="catminer",
    version="1.5",
    packages=['catminer'],
    package_data={'catminer': ['config/settings.ini']},
    python_requires='>=3.7',
    url="https://github.com/WWU-CAD-Autograder/catminer",
)
