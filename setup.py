"""Setup script for sap_hana_client_generator."""

from setuptools import setup, find_packages

setup(
    name="sap_hana_client_generator",
    version="0.1.0",
    description="Generate Python client libraries from SAP HANA OpenAPI specifications",
    long_description="""
    A Python package that generates client libraries from OpenAPI specifications for SAP HANA.
    The generated clients provide a convenient way to interact with SAP HANA APIs.
    """,
    author="SAP HANA Client Generator",
    author_email="user@example.com",
    url="https://github.com/example/sap-hana-client-generator",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=5.4.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "sap-hana-client-generator=sap_hana_client_generator.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
) 