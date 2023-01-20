from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
VERSION = "0.11.4"

setup(
    name="Qpro",
    version=VERSION,
    description="Small but powerful command line IDE.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="script for CLionProjects",
    author="RhythmLian",
    url="https://github.com/Rhythmicc/QuickProject",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["pyperclip", "rich", "gitpython", "inquirer-rhy", "langSrc"],
    entry_points={
        "console_scripts": [
            "Qpro = QuickProject.Qpro:main",
            "qrun = QuickProject.qrun:main",
        ]
    },
)
