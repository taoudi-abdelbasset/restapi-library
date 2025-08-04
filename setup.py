from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="restapi-library",
    version="0.0.2",  # Incremented version for updates
    author="Taoudi Abdelbasset",
    author_email="taoudiabdu@gmail.com",
    description="A comprehensive REST API client library with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taoudi-abdelbasset/RestAPILibrary",  # Updated to match your project
    packages=find_packages(where="app"),  # Look for packages in the 'app' directory
    package_dir={"": "app"},  # Map package root to 'app' directory
    include_package_data=True,  # Include non-Python files like README.md
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "redis": ["redis>=4.0.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "twine>=3.0",  # Added for PyPI publishing
        ],
    },
    entry_points={
        "console_scripts": [
            "restapi-cli=restapi_library.cli:main",  # Updated to match package structure
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/taoudi-abdelbasset/RestAPILibrary/issues",
        "Source": "https://github.com/taoudi-abdelbasset/RestAPILibrary",
        "Documentation": "https://restapi-library.readthedocs.io/",
    },
)