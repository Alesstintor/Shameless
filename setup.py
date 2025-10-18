"""
Setup configuration for Shameless Sentiment Analyser package.
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="shameless-sentiment-analyser",
    version="0.1.0",
    author="Shameless Team",
    author_email="your.email@example.com",
    description="A professional sentiment analysis platform combining web scraping with ML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Shameless",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "*.ipynb"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "isort>=5.13.2",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "shameless=sentiment_analyser.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
