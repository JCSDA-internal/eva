# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

# Setup and installation script
#
# Usage: pip install --prefix=/path/to/install .

# --------------------------------------------------------------------------------------------------

import setuptools

setuptools.setup(
    name='eva',
    version='0.0.0',
    author='Community owned code',
    description='Evaluation and Verification of an Analysis',
    url='https://github.com/danholdaway/eva',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent'],
    python_requires='>=3.6',
    install_requires=[
        'pyyaml>=5.4',
        'pycodestyle>=2.8.0',
        'netCDF4>=1.5.7',
        'matplotlib>=3.4.3',
    ],
    entry_points={
        'console_scripts': [
            'eva = eva.base:main',
        ],
    },
    )

# --------------------------------------------------------------------------------------------------
