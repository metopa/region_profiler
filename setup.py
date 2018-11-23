from setuptools import setup

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='region_profiler',
    version='0.1.1',
    description='Profile user-defined regions of code without any external tools',
    long_description=long_description,
    packages=['region_profiler'],
    keywords='timing, timer, profiling, profiler',
    license='MIT',
    url='https://github.com/metopa/region_profiler',
    author='Viacheslav Kroilov',
    author_email='slavakroilov@gmail.com',
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    data_files=[('region_profiler', ['LICENSE.rst'])],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities'
    ]
)
