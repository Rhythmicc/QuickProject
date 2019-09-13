from setuptools import setup, find_packages

VERSION = '0.1.1'

setup(
    name='Qpro',
    version=VERSION,
    description='create some practical scripts for your clion project!',
    classifiers=[],
    keywords='script for CLionProjects',
    author='RhythmLian',
    author_mail='RhythmLian@outlook.com',
    url="https://github.com/Rhythmicc/QuickProject",
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'Qpro = QuickProject.Qpro:main'
        ]
    },
)
