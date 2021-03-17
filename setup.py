"""Setup.py script for the Open Source DIF3D ARMI plugin"""

from setuptools import setup, find_namespace_packages

with open("README.md") as f:
    README = f.read()

setup(
    name="armicontrib-dif3d",
    version="1.0",
    description=("ARMI plugin for neutronics analysis with DIF3D."),
    author="TerraPower LLC",
    author_email="armi-devs@terrapower.com",
    packages=find_namespace_packages(),
    package_data={
        "armicontrib.dif3d": ["templates/*", "templates/**"],
    },
    entry_points={"console_scripts": ["dif3ddemo=dif3ddemo:main"]},
    long_description=README,
    install_requires=[
        # ARMI 0.1.6 is needed since it is the last version before Locations were
        # removed, which this still uses. Need to refactor to grids/spatial locators to
        # target newer ARMI versions
        "armi==0.1.6",
        "jinja2",
        "terrapower-dragon",
    ],
    extras_require={
        "dev": [
            "pytest",
            "sphinx",
            "sphinx_rtd_theme",
            "sphinxcontrib-apidoc",
            "sphinxcontrib-needs",
            "sphinxcontrib-plantuml",
        ]
    },
    keywords=["ARMI, DIF3D", "Neutronics"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    test_suite="tests",
    include_package_data=True,
)
