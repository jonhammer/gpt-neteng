from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="gpt-neteng",
    version="0.1",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "gpt-neteng=gpt_neteng.app:main",
        ],
    },
    url="https://github.com/jonhammer/gpt-neteng",
    license="Apache License 2.0",
    author="Jonathan Hammer",
    author_email="jon.p.hammer@gmail.com",
    description="The first AI Network Engineer",
)
