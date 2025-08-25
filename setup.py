"""Setup script for the slack_bot package."""

from setuptools import find_packages, setup

setup(
    name="slack_bot",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "slack-bolt>=1.18.0",
        "slack-sdk>=3.26.0",
        "google-generativeai>=0.3.0",
        "chromadb>=0.4.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "mypy>=1.5.0",
            "flake8>=6.1.0",
            "black>=23.7.0",
            "isort>=5.12.0"
        ]
    }
)
