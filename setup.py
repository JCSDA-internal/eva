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
    version='1.3.4',
    author='Community owned code',
    description='Evaluation and Verification of an Analysis',
    url='https://github.com/JCSDA-internal/eva',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
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
        'emcpy @ git+https://github.com/NOAA-EMC/' +
        'emcpy@471cb60c44c51a7e07dfbd0173c276ecdc1b46f1#egg=emcpy',
        # Option dependency for making density plots
        # 'seaborn==0.12',
    ],
    package_data={
        '': [
               'tests/config/*',
               'tests/data/*',
               'tests/notebooks/*',
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
