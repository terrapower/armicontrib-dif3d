# Copyright 2021 TerraPower, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Components for writing DIF3D inputs from ARMI models.

DIF3D Inputs can be specified in a combination of binary interface files (see, e.g.,
:py:mod:`armi:armi.nuclearDataIO`) and/or textual input in free format (order matters)
or fixed format (column number matters).

DIF3D will convert any input into binary interface files on initialization, so there may
be some performance advantage of using binary when possible. However, the implementation
currently produces text-based input files. These are created using the `Jinja2
<https://palletsprojects.com/p/jinja/>`_ template engine, which aims to separate
boilerplate text from case-dependent contents through text interpolation.

Geometry details are specified on what DIF3D calls the A.NIP3 cards. To support
different geometries (Hex, Cartesian, Triangular, RZ, etc.) we support subclassing of
the ``GeometryWriter`` subclasses, which are composed into ``Dif3dWriter`` objects.
Ultimately, these data, along with material information, execution settings, etc. are
packaged in a payload dictionary in :py:meth:`Dif3dWriter._buildTemplateData`, then
passed to the Jinja2 template to generate the actual DIF3D input file. The template file
itself can be found at ``armicontrib/dif3d/templates/dif3d.inp``.

.. pyreverse:: armicontrib.dif3d.inputWriters -A
    :align: center
"""
from typing import NamedTuple

import jinja2

from armi.nucDirectory import nuclideBases
from armi import runLog
from armi.physics import neutronics
from armi.reactor import geometry

from . import const


class NuclideSummary(NamedTuple):
    """An entry for single nuclide in A.SUMMAR"""

    libID: str
    typeID: str
    weight: float
    isotxsLabel: str


class Nip9MeshValue(NamedTuple):
    """An entry in a NIP card 09 mesh definition"""

    direction: str
    """Letter specifying which axis (e.g. ``Z``)"""

    submeshes: int
    """Number of equal submeshes within this mesh step"""

    upperCm: float
    """Upper bound of mesh in centimeters"""


class NumberDensityDatum(NamedTuple):
    """An entry in a NIP card 13 number density definition"""

    region: str
    """DIF3D region label"""

    nuclideID: str
    """Nuclide id as it will be found in the library (often with XSID)"""

    ndens: float
    """Number density in atoms/bn-cm"""


class HexDatum(NamedTuple):
    """A single hexagon definition for NIP3 card 30 in hex case"""

    loc: str
    ring: int
    pos: int
    bottom: float
    top: float


class Dif3dWriter:
    """
    Write DIF3D input file.

    Uses the ARMI state plus a template.

    Geometry code is handled through a GeometryWriter subclass, which allows geometric
    specialization through composition instead of inheritance.
    """

    def __init__(self, reactor, options):
        """Build the writer"""
        self._env = None
        self.r = reactor
        self.options = options
        self.geometryWriter = HexGeom(reactor, options)
        self.regionWriter = ISOTXSRegionGenerator(reactor, options)

    def write(self, stream):
        """Write the input file to a stream."""

        runLog.info(f"Writing DIF3D input based on: {self.r.core}")

        templateData = self._buildTemplateData()
        self._makeTemplateEnvironment()
        template = self._env.get_template("dif3d.inp")
        stream.write(template.render(**templateData))

    def _makeTemplateEnvironment(self):
        """
        Set up the template environment.

        We set up the path to template here and set
        whitespace control appropriate for dif3d.
        """
        self._env = jinja2.Environment(
            loader=jinja2.PackageLoader("armicontrib.dif3d", "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=jinja2.StrictUndefined,
        )

    def _buildTemplateData(self):
        """
        Populate data structures for rendering in the template.
        """
        boundaries, geomNum = self.geometryWriter.getBoundaryConditionsAndGeomNum()
        return {
            "opts": self.options,
            "r": self.r,
            "boundaryConditions": boundaries,
            "geomNum": geomNum,
            "nuclideSummary": self.regionWriter.writeSummaryLines(),
            "compositions": self.regionWriter.makeNIP13(),
            # todo: probably pass this dict to geomWriter to add its keys
            "axialMesh": self.geometryWriter.makeNIP9(),
            "hexes": self.geometryWriter.makeNIP30(),
        }


class GeometryWriter:
    """Handles geometry-specific information on A.NIP3."""

    def __init__(self, reactor, options):
        self.r = reactor
        self.options = options

    def _defineBoundaryCoefficients(self):
        # settings are checked in _validateboundaryConditions
        if self.options.boundaries == neutronics.EXTRAPOLATED:
            return  # DIF3D  already sets to extrapolated
        elif self.options.boundaries == neutronics.ZERO_INWARD_CURRENT:
            self._dif3dBoundaryCoefficients = 0.5
        elif self.options.boundaries == neutronics.GENERAL_BC:
            self._dif3dBoundaryCoefficients = self.options.bcCoefficient
        else:
            raise ValueError("Unsupported `boundaries` setting.")


class HexGeom(GeometryWriter):
    """Specialization for hexagonal geometry."""

    def getBoundaryConditionsAndGeomNum(self):
        """Get DIF3D line representing boundary conditions and a geometry number"""
        invalidMsg = f"{self.options.boundaries} is either invalid or not implemented for hex geometry"
        if self.r.core.isFullCore:
            geomNumber = "120" if self.options.nodal else "100"
            if self.options.boundaries == neutronics.INFINITE:
                bc = " 3     3     3     3     3     3 "
            elif self.options.boundaries == neutronics.REFLECTIVE:
                bc = " 3     3     3     3     4     4 "
            elif self.options.boundaries in const.GENERALIZED_BC:
                bc = " 4     4     4     4     4     4 "
                self._defineBoundaryCoefficients()
            elif self.options.boundaries == neutronics.ZEROFLUX:
                bc = " 7     2     2     2     2     2 "
            else:
                raise ValueError(invalidMsg)

        elif self.r.core.symmetry == geometry.THIRD_CORE + geometry.PERIODIC:
            geomNumber = "126" if self.options.nodal else "94"
            if self.options.boundaries == neutronics.INFINITE:
                bc = " 7     3     3     3     3     3 "
            elif self.options.boundaries == neutronics.REFLECTIVE:
                bc = " 7     3     3     3     4     4 "
            elif self.options.boundaries in const.GENERALIZED_BC:
                bc = " 7     4     4     4     4     4 "
                self._defineBoundaryCoefficients()
            elif self.options.boundaries == neutronics.ZEROFLUX:
                bc = " 7     2     2     2     2     2 "
            else:
                raise ValueError(invalidMsg)
        else:
            raise ValueError(
                "{} is not a valid symmetry for hex geometry".format(
                    self.r.core.symmetry
                )
            )
        return bc, geomNumber

    def makeNIP9(self):
        """Write axial mesh for hex cases."""
        axMesh = self.r.core.p.axialMesh
        checkMesh(axMesh)
        meshData = []
        for upperCm in axMesh[1:]:
            meshData.append(Nip9MeshValue("Z", submeshes=1, upperCm=upperCm))
        return meshData

    def makeNIP30(self):
        """Write hexagons"""
        hexes = []
        for a in self.r.core.getAssemblies():
            bottom = 0.0
            top = 0.0
            ring, pos = a.spatialLocator.getRingPos()
            for block in a:
                top += block.getHeight()
                # be careful, sometimes we get 1.242E+003. we want just E+03. careful
                if ring is None or pos is None:
                    raise ValueError("{} in {} has invalid location.".format(block, a))
                hexes.append(
                    HexDatum(block.getLocation(), ring, pos, bottom, top)
                )
                bottom = top
        return hexes


def checkMesh(meshPoints):
    lastMesh = 0.0
    for meshVal in meshPoints[1:]:  # skip the first entry (which is 0)
        if abs(meshVal - lastMesh) < 0.1:
            runLog.warning(
                "Mesh value {0} is close to neighboring mesh value {1}. "
                "Watch for DIF3D convergence issues.".format(meshVal, lastMesh)
            )
        lastMesh = meshVal


class _XSBasedRegionGenerator(object):
    """
    Object for writing library-specific region definition in DIF3D inputs.

    This is used to add flexibility to the composition of the Dif3dWriter objects.
    In cases where COMPXS is available already (pre-defined macroscopic XS), then
    the nuclide-level region input is not necessary. When COMPXS is to be created
    by the DIF3D from nuclide number densities (typical), then they must be included
    in the input file.

    This is a composition-over-inheritance design decision rooted in experience.
    """

    def __init__(self, reactor, options):
        self.r = reactor
        self.options = options

    def _nuclideIsSkipped(self, nuclideBase):
        """
        Check if the nuclide base should be skipped during the DIF3D input writing process.

        Notes
        -----
        This applies to `DUMMY` or `DMP` nuclides that no neutronic significance to the reactor.
        """
        if "REBUS" in self.options.kernelName:
            return False
        if isinstance(nuclideBase, nuclideBases.DummyNuclideBase):
            return True
        return False

    def writeHomogenizationLines(self, outFile):
        raise NotImplementedError

    def writeNIP13(self, outFile, external=False):
        raise NotImplementedError

    def writeNIP14(self, outFile):
        raise NotImplementedError

    def writeSummaryLines(self):
        raise NotImplementedError


class ISOTXSRegionGenerator(_XSBasedRegionGenerator):
    """
    Writes number density sections of DIF3D input file when an ``ISOTXS`` library is used.

    Parameters
    ----------
    cs: :py:class:`~armi.settings.caseSettings.Settings`
        Settings that determine what is written
    r: :py:class:`~armi.reactors.Reactor`
        Reactor that this interface to which this interface is attached

    Notes
    -----
    ``ISOTXS`` specific changes

        * ``DATASET=ISOTXS``
        * ``UNFORM=A.HMG4C`` homogenization block
        * ``UNFORM=A.SUMMAR`` nuclide summary block
        * 13 cards - nuclide number densities for each block
        * 14 cards - list both the primary and secondary compositions for each block
    """

    def __init__(self, reactor, options):
        _XSBasedRegionGenerator.__init__(self, reactor, options)
        self.inputDeclaration = "DATASET=" + neutronics.ISOTXS

    def writeSummaryLines(self):
        nuclides = []
        allNuclides = self.r.blueprints.allNuclidesInProblem
        for xsSuffix in self.r.core.getAllXsSuffixes():
            for nuclideName in allNuclides:

                nuclide = nuclideBases.byName[nuclideName]
                if self._nuclideIsSkipped(nuclide):
                    continue
                if self.options.xsKernel == "MC2v2":
                    libID = nuclide.mc2id
                else:
                    libID = nuclide.getMcc3Id()
                if nuclide.isFissile():
                    typeID = "FISS"
                elif nuclide.isHeavyMetal():
                    typeID = "FERT"
                else:
                    typeID = ""
                nuclides.append(
                    NuclideSummary(
                        libID=libID,
                        typeID=typeID,
                        weight=nuclide.weight,
                        isotxsLabel=nuclide.label + xsSuffix,
                    )
                )
        return nuclides

    def makeNIP13(self):
        """
        Make the NIP card 13, which defines the isotopic compositions of all blocks.

        All possible nuclides should be listed with proper XS library identifier.

        Raises
        ------
        ValueError
            Empty list of number densities.
        """
        compositions = []
        for b in self.r.core.getBlocks():  # pylint: disable=too-many-nested-blocks
            for nucName, dens in zip(
                self.r.blueprints.allNuclidesInProblem,
                b.getNuclideNumberDensities(self.r.blueprints.allNuclidesInProblem),
            ):
                nuclideBase = nuclideBases.byName[nucName]
                if not dens or self._nuclideIsSkipped(nuclideBase):
                    continue
                mc2Label = nuclideBases.byName[nucName].label
                nucLabel = mc2Label + b.getMicroSuffix()
                compositions.append(NumberDensityDatum(b.name, nucLabel, dens))
        return compositions

    def writeNIP14(self, outFile):
        """
        Write primary and secondary composition definitions.

        Primary composition labels start with ``"Y"`` and secondary labels start with ``"Z"``
        """
        lines = []
        for block in self.r.core.getBlocks():
            name = block.name[1:]
            lines.append("14          Z{:5s} {:6s} 1.0\n".format(name, block.name))
            lines.append("14          Y{:5s} Z{:5s} 1.0\n".format(name, name))

        outFile.write("".join(lines))
