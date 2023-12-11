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
    version='1.6.1',
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
            'eva = eva.eva_driver:main',
            'eva_tests = eva.eva_tests:main',
        ],
    },
    )

# --------------------------------------------------------------------------------------------------
