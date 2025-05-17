from setuptools import setup, find_packages

setup(
    name="fib-manager",
    version="1.0.0",
    description="FIB Manager - A tool to search and generate valid class schedules for FIB degrees.",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={
        'console_scripts': [
            'fib-manager=app.commands.command_line:main',
        ],
    },
    install_requires=[
        "requests",
        "rich",
        "questionary",
        "pyfiglet",
    ],
)
