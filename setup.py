from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()
VERSION = '0.2.0'

setup(
    name='Qpro',
    version=VERSION,
    description='create some practical scripts for your clion project!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='script for CLionProjects',
    author='RhythmLian',
    author_mail='RhythmLian@outlook.com',
    url="https://github.com/Rhythmicc/QuickProject",
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=['pyperclip'],
    entry_points={
        'console_scripts': [
            'Qpro = QuickProject.Qpro:main'
        ]
    },
)
