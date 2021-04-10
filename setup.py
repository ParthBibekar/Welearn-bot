from setuptools import setup

requirements = []
with open('requirements.txt', 'r') as fh:
    for line in fh:
        requirements.append(line.strip())

setup(
    name = "welearn-bot-iiserkol",
    description = "A command line client for WeLearn, in the IISER Kolkata domain",
    author = "Parth Bibekar",
    author_email = "bibekarparth24@gmail.com",
    url = "https://github.com/ParthBibekar/Welearn-bot",
    version = "1.0.0",
    license = "MIT",
    scripts = ["welearn_bot"],
    install_requires = requirements
)
