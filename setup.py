"""
Copyright (c) 2021 Tilo van Ekeris / TMDT, University of Wuppertal
Copyright (c) 2024 Lorenzo Ortiz Aneiros
Distributed under the MIT license, see the accompanying
file LICENSE or https://opensource.org/licenses/MIT
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plantsim",
    version="0.2.1",
    author="Tilo van Ekeris, Lorenzo Ortiz Aneiros",
    author_email="tilo@vanekeris.de, lortane@pm.me",
    description="Python wrapper for Plant Simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=["pywin32==306", "pandas"],
)
