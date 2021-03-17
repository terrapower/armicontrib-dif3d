# Open-Source ARMI-DIF3D Plugin

This code connects TerraPower's ARMI® engineering automation code with ANL's
DIF3D global flux code, for use in building/designing/supporting fast reactors.
It was originally developed under contract for Idaho National Laboratory (see
Attribution below), with the intent to release as open source to the community.
The accompanying documentation justify and demonstrate satisfaction of the
requirements of the original scope of work, and accompanied the code as a report
when delivered to INL. As this plugin evolves, these documents are expected to
evolve and generalize as well.

## Features

* Build DIF3D input files based on ARMI representations of a reactor in Hex
  geometry

* Execute DIF3D

* Read DIF3D output information and store it back on the ARMI reactor model for
  coupling with other codes (e.g. for depletion, thermal/hydraulics, fuel
  performance etc.)

## Limitations

* Only supports a subset of DIF3D geometries

* Cross sections must be provided externally (e.g. from MC2 or DRAGON or OpenMC)

* Does not support all DIF3D features

## Installation

The DIF3D plugin and demonstration application, along with ARMI and all other
required dependencies can be installed by running

    pip install -r requirements.txt

from within a Python environment. It is recommended to do this inside of a
Python [Virtual Environment](https://docs.python.org/3/tutorial/venv.html) to
gain better control of installed dependencies and their versions.

## Attribution
This work was initially sponsored by Battelle Energy Alliance, LLC Under
Amendment No 06 to Release No 01 Under Blanket Master Contract No. 00212114 with
scope defined in SOW-15678, effective 8/25/2020.

