from setuptools import setup, find_packages

setup(
    name="robot-control",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "jinja2",
        "python-multipart",
        "aiosqlite",
    ],
)