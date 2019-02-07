from setuptools import setup, Extension

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup_args = {
    'name': 'region_profiler',
    'version': '0.5',
    'description': 'Profile user-defined regions of code without any external tools',
    'long_description': long_description,
    'packages': ['region_profiler'],
    'package_dir': {'region_profiler': 'region_profiler'},
    'package_data': {'region_profiler': ['*.pxd', '*.py']},
    'keywords': 'timing, timer, profiling, profiler',
    'license': 'MIT',
    'url': 'https://github.com/metopa/region_profiler',
    'author': 'Viacheslav Kroilov',
    'author_email': 'slavakroilov@gmail.com',
    'setup_requires': ['pytest-runner', 'setuptools>=18.0', 'cython'],
    'tests_require': ['cython', 'pytest', 'pytest-cov==::2.6.0', 'codecov'],
    'data_files': [('region_profiler', ['LICENSE.rst'])],
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities'
    ],
    'ext_modules': [Extension('region_profiler.cython.listener', language='c++',
                              sources=['region_profiler/cython/listener.pyx']),
                    Extension('region_profiler.cython.node', language='c++',
                              sources=['region_profiler/cython/node.pyx']),
                    Extension('region_profiler.cython.profiler', language='c++',
                              sources=['region_profiler/cython/profiler.pyx']),
                    Extension('region_profiler.cython.utils', language='c++',
                              sources=['region_profiler/cython/utils.pyx'])
                    ],
}

setup(**setup_args)
