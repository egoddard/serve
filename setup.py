from setuptools import setup, find_packages

setup(
    name='serve',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'jinja2',
    ],
    entry_points='''
        [console_scripts]
        serve=serve.scripts.serve:serve
    ''',
)
