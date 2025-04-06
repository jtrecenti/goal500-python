from setuptools import setup, find_packages

setup(
    name="goal500",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pandas",
        "matplotlib",
        "numpy",
        "pillow",
        "imageio",
    ],
    entry_points={
        "console_scripts": [
            "goal500=goal500.cli:main",
        ],
    },
    author="jtrecenti",
    author_email="jtrecenti@example.com",
    description="Extrai dados de gols acumulados por ano de jogadores de futebol da Wikipedia",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jtrecenti/goal500-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
