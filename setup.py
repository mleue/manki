from setuptools import setup, find_packages

setup(
    name="manki",
    version="0.0.1",
    description="Convert markdown files to anki decks.",
    url="",
    author="Michael Leue",
    author_email="michael@mleue.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": ["manki=manki.cli:manki_cli"],
    },
    keywords="anki markdown flashcard",
    packages=find_packages(exclude=["tests"]),
    install_requires=["genanki", "click"],
    extras_require={"dev": ["pytest"]},
)
