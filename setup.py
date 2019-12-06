"""
maegtk: a maester genotyping toolkit
"""
from setuptools import find_packages, setup

dependencies = ['click', 'pysam', 'pytest', 'snakemake', 'biopython', 'optparse-pretty', 'regex', 'ruamel.yaml']

setup(
    name='maegtk',
    version='0.0.1',
    url='https://github.com/aryeelab/mgatk',
    license='MIT',
    author='Caleb Lareau',
    author_email='clareau@broadinstitute.org',
    description='Processing and quality control of mitochondrial genome variants from Maester data.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'maegtk = maegtk.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
         'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
