"""Setup script for Google Maps CLI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="google-maps-cli",
    version="1.0.0",
    author="Nitai Aharoni",
    description="Command-line interface for Google Maps Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nitaiaharoni/google-maps-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "maps=google_maps_cli.cli:cli",
        ],
    },
)

