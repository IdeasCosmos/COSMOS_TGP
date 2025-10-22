"""Setup configuration for SJZIP."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="sjzip",
    version="2.0.0",
    author="Multibus TGP Team",
    author_email="info@multibus-tgp.org",
    description="Secure text compression system using 3D spiral space mapping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IdeasCosmos/COSMOS_TGP",
    packages=find_packages(exclude=["tests", "scripts", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Archiving :: Compression",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Security :: Cryptography",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0,<2.0.0",
        "pandas>=2.0.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "bandit>=1.7.5",
        ],
        "viz": [
            "matplotlib>=3.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sjzip=scripts.sjzip_main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/IdeasCosmos/COSMOS_TGP/issues",
        "Source": "https://github.com/IdeasCosmos/COSMOS_TGP",
        "Documentation": "https://github.com/IdeasCosmos/COSMOS_TGP/wiki",
    },
)
