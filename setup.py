import os

from setuptools import find_packages, setup

current_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(current_directory, 'README.md'), "r") as readme:
    package_description = readme.read()

version_string = "0.1.4"
version_path = os.path.join(current_directory, ".version")
if os.path.exists(version_path):
    with open (os.path.join(current_directory, ".version"), 'r') as version_file:
        version_string = version_file.read()

setup(
    name="werkflow",
    version=version_string,
    description="Composable workflows for all.",
    long_description=package_description,
    long_description_content_type="text/markdown",
    author="Ada Lundhe",
    author_email="corpheus91@gmail.com",
    url="https://github.com/scorbettUM/werkflow",
    packages=find_packages(),
    keywords=[
        'pypi', 
        'cicd', 
        'python',
        'setup',
        'repo',
        'project',
        'migrate',
        'monorepo'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'click',
        'psutil',
        'distro',
        'pydantic',
        'networkx',
        'aiologger',
        'yaspin',
        'art',
        'python-dotenv'
    ],
    entry_points = {
        'console_scripts': [
            'werkflow=werkflow.cli:run',
        ],
    },
    extras_require = {
        'all': [
            'werkflow-aws',
            'werkflow-docker',
            'werkflow-encryption',
            'werkflow-git',
            'werkflow-github',
            'werkflow-http',
            'werkflow-metrik',
            'werkflow-secrets'
        ],
        'aws': [
            'werkflow-aws'
        ],
        'docker': [
            'werkflow-docker'
        ],
        'encryption': [
            'werkflow-encryption',
        ],
        'git': [
            'werkflow-git'
        ],
        'github': [
            'werkflow-github'
        ],
        'http': [
            'werkflow-http'
        ],
        'metrik': [
            'werkflow-metrik'
        ],
        'secrets': [
            'werkflow-secrets'
        ]
    },
    python_requires='>=3.8'
)
