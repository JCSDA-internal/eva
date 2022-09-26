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
    version='1.2.2',
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
        'pyyaml>=6.0',
        'pycodestyle>=2.8.0',
        'netCDF4>=1.5.3',
        'matplotlib>=3.5.2',
        'cartopy>=0.18.0',
        'scikit-learn>=1.0.2',
        'xarray>=0.11.3',
    ],
    package_data={
        '': [
               'tests/config/*',
               'tests/data/*',
               'defaults/*.yaml'
             ],
    },
    entry_points={
        'console_scripts': [
            'eva = eva.eva_base:main',
            'eva_tests = eva.eva_tests:main',
        ],
    },
    )

# --------------------------------------------------------------------------------------------------
