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
Series of functions that define subsets of files names to be copied back from the fastPath to the
working directory based on user-specified setting and/or unsuccessful DIF3D/VARIANT run.
"""
import armi
from armi.physics.neutronics import (
    realCalculationRequested,
    adjointCalculationRequested,
)

from armi.nuclearDataIO.cccc.rtflux import RTFLUX, ATFLUX
from armi.nuclearDataIO.cccc.labels import LABELS
from armi.nuclearDataIO.cccc.geodst import GEODST
from armi.nuclearDataIO.cccc.pwdint import PWDINT
from armi.nuclearDataIO.cccc.rzflux import RZFLUX

from .binaryIO import dif3dFile, pkedit

# GAMSOR-specific constants
GAMSOR_GAMMA_SRCGEN = "-step_1"
GAMSOR_GAMMA_FLUX = "-step_2"
GAMSOR_POWERCALC = "-step_3"
GAMMA_ARMI = "ARMI"

# Constants for ANL ARC system's interface file names
VARIANT = "VARIANT"
VARSRC = "VARSRC"
FIXSRC = "FIXSRC"
ANIP3 = "ANIP3"
NAFLUX = "NAFLUX"
NHFLUX = "NHFLUX"
NPDINT = "NPDINT"
GPDINT = "GPDINT"
GTFLUX = "GTFLUX"
GHFLUX = "GHFLUX"
SFEDIT = "SFEDIT"


def specifyAllFiles(options):
    """Specify that all files managed by this interface are to be retrieved."""
    filesToRetrieve = dict()
    filesToRetrieve.update(specifyGeomFiles(options))
    filesToRetrieve.update(specifyRestartFiles(options))
    filesToRetrieve.update(specifyPowerFiles(options))
    if (
        options.energyDepoCalcMethodStep
        and GAMSOR_POWERCALC in options.energyDepoCalcMethodStep
    ):
        filesToRetrieve.merge(specifyGamsorPowerFiles())
    return filesToRetrieve


def specifyRestartFiles(options):
    """
    Specify files necessary for a DIF3D restart calculation are to be retrieved.

    File names are contained in a dictionary with the format {local : destination} names.
    """
    restartFiles = {dif3dFile.DIF3D: dif3dFile.DIF3D}
    restartFiles.update(specifyFluxFiles(options))
    restartFiles.update(specifyGamsorOtherFiles(options))
    return restartFiles


def specifyPowerFiles(options):
    """Specify PWDINT when real flux is active"""
    if options.real:
        return {pkedit.PKEDIT: pkedit.PKEDIT}
    return dict()


def specifyFluxFiles(options):
    """Specify flux files depending on calculation type and neutronics kernel."""
    neutronFluxFiles = specifyRegionTotalFluxFiles(options)
    if options.nodal:
        neutronFluxFiles.update(specifyNodalFluxFiles(options))
    return neutronFluxFiles


def specifyNodalFluxFiles(options):
    """
    Specify DIF3D-Nodal flux files depending on calculation type.

    File names are contained in a dictionary with the format {local : destination} names.
    """
    nodalFluxFiles = dict()
    depo = options.energyDepoCalcMethodStep
    # MTY: GAMMA_ARMI seems sus here
    if depo and (GAMMA_ARMI in depo or GAMSOR_GAMMA_FLUX in depo):
        destinationName = GHFLUX
    else:
        destinationName = NHFLUX

    if options.real:
        nodalFluxFiles.update({NHFLUX: destinationName})
    if options.adjoint:
        nodalFluxFiles.update({NAFLUX: NAFLUX})
    return nodalFluxFiles


def specifyGeomFiles(options):  # pylint: disable=unused-argument
    geomFiles = {GEODST: GEODST, LABELS: LABELS, "DIF3D": "DIF3D"}
    return geomFiles


def specifyRegionTotalFluxFiles(options):
    """
    Specify region total flux files depending on calculation type.

    File names are contained in a dictionary with the format {local : destination} names.
    """
    regionTotalFluxFiles = dict()
    depo = options.energyDepoCalcMethodStep
    if depo and (GAMMA_ARMI in depo or GAMSOR_GAMMA_FLUX in depo):
        destinationName = GTFLUX
    else:
        destinationName = RTFLUX

    if options.real:
        regionTotalFluxFiles.update({RZFLUX: RZFLUX})
        regionTotalFluxFiles.update({RTFLUX: destinationName})
        regionTotalFluxFiles.update({PWDINT: PWDINT})
    if options.adjoint:
        regionTotalFluxFiles.update({ATFLUX: ATFLUX})
    return regionTotalFluxFiles


def specifyGamsorOtherFiles(options):
    """
    Specify GAMSOR other files to retrieve based on the methodology step.

    File names are contained in a dictionary with the format {local : destination} names.
    """
    gamsorFiles = dict()
    depo = options.energyDepoCalcMethodStep
    if depo and GAMSOR_GAMMA_SRCGEN in depo:
        gamsorFiles.update(specifyFixedSourceFiles(options))

    elif depo and GAMSOR_GAMMA_FLUX in depo:
        gamsorFiles.update({ANIP3: ANIP3})

    elif depo and GAMSOR_POWERCALC in depo:
        gamsorFiles.update({RTFLUX: RTFLUX, GTFLUX: GTFLUX, ANIP3: ANIP3})
    return gamsorFiles


def specifyFixedSourceFiles(options):
    if VARIANT not in options.kernelName:
        variantFixedSourceFiles = {FIXSRC: FIXSRC}
    else:
        variantFixedSourceFiles = {VARSRC: VARSRC}
    return variantFixedSourceFiles


def specifyGamsorPowerFiles():
    gamsorPowerFiles = {NPDINT: NPDINT, GPDINT: GPDINT, PWDINT: PWDINT}
    return gamsorPowerFiles
