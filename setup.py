from setuptools import setup, find_packages
import sys

is_win = sys.platform.startswith('win')

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
VERSION = '0.6.3'

setup(
    name='Qpro',
    version=VERSION,
    description='Small but powerful command line IDE.',
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
            'Qpro = QuickProject.Qpro:main',
            'qrun = QuickProject.run:main' if is_win else 'run = QuickProject.run:main',
            'tmpm = QuickProject.tmpm:main',
            'detector = QuickProject.detector:main'
        ]
    },
)
