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

import os
import shutil

from armi import runLog
from armi.physics.neutronics.globalFlux import globalFluxInterface
from armi.physics.neutronics.settings import CONF_OUTERS_ as CONF_OUTERS
from armi.physics.neutronics.settings import CONF_INNERS_ as CONF_INNERS

from armi.settings import caseSettings
from armi.physics import neutronics
from armi.physics.neutronics import settings as gsettings

from . import settings
from . import fileSetsHandler


# The recommended option is P5P1 for small/medium cores, and P3P1 for large cores
VARIANT_TRANSPORT_AND_SCATTER_ORDERS = {
    "P1P0": (10101, 0),  # diffusion solution
    "P3P1": (10303, 1),  # transport with P3 angle and P1 scattering
    "P3P3": (10303, 3),  # transport with P3 angle and P3 scattering
    "P5P1": (10505, 1),  # transport with P5 angle and P1 scattering
    "P5P3": (10505, 3),  # transport with P5 angle and P3 scattering
}


class Dif3dOptions(globalFluxInterface.GlobalFluxOptions):
    """Define options for one particular DIF3D execution."""

    def __init__(self, label=None):
        globalFluxInterface.GlobalFluxOptions.__init__(self, label)
        self.templatePath = None
        self.kernelName = "DIF3D"
        self.libDataFile = neutronics.ISOTXS
        self.label = label if label else "dif3d"
        self.executablePath = None
        self.runDir = None
        self.maxOuters = None
        self.numberMeshPerEdge = 1
        self.erf = None
        self.neutronicsOutputsToSave = None
        self.nodal = None
        self.xsLibraryName = None
        self.existingFixedSource = None
        self.bcCoefficient = None
        self.d3dMem = None
        self.d3dMem2 = None
        self.nipMem = None
        self.xsMem = None
        self.asympExtrapOfOverRelaxCalc = None
        self.inners = None
        self.asympExtrapOfNodalCalc = None
        self.variantNodalSpatialApproximation = None
        self.useRadialInnerIterationAlgorithm = None
        self.variantTransportAndScatterOrder = None
        self.nodalApproxXY = None
        self.nodalApproxZ = None
        self.listIsotxs = None
        self.neglectFis = None
        self.variantFlag = False
        self.angularApprox = None
        self.anisotropicScatteringApprox = None
        self.detailedDb: Optional[str] = None
        # When writing the neutronics-mesh database, we need the actual case Settings
        # object in order for that database to be complete and capable of being read.
        # Storing the full cs object here seems contrary to the goal of Options classes
        # to decouple Executers from raw Settings. However, here we need the **object**,
        # rather than the settings that it contains. Future work to the ARMI framework
        # may relax the need for case settings in a database file to support loading, in
        # which case this would no longer be required.
        self.csObject: Optional[caseSettings.Settings] = None

    def fromUserSettings(self, cs: caseSettings.Settings):
        """Set options from user settings"""
        globalFluxInterface.GlobalFluxOptions.fromUserSettings(self, cs)
        self.executablePath = shutil.which(cs[settings.CONF_DIF3D_PATH])
        self.setRunDirFromCaseTitle(cs.caseTitle)
        self.neutronicsOutputsToSave = cs[settings.CONF_NEUTRONICS_OUTPUTS_TO_SAVE]
        self.existingFixedSource = cs[gsettings.CONF_EXISTING_FIXED_SOURCE]
        self.epsFissionSourceAvg = cs[gsettings.CONF_EPS_FSAVG]
        self.epsFissionSourcePoint = cs[gsettings.CONF_EPS_FSPOINT]
        self.epsEigenvalue = cs[gsettings.CONF_EPS_EIG]
        self.maxOuters = cs[CONF_OUTERS]
        self.numberMeshPerEdge = cs[gsettings.CONF_NUMBER_MESH_PER_EDGE]
        self.erf = cs[settings.CONF_ERF]
        self.bcCoefficient = cs[gsettings.CONF_BC_COEFFICIENT]
        self.d3dMem = cs[settings.CONF_D3D_MEM]
        self.d3dMem2 = cs[settings.CONF_D3D_MEM2]
        self.nipMem = cs[settings.CONF_NIP_MEM]
        self.xsMem = cs[settings.CONF_XS_MEM]
        self.asympExtrapOfOverRelaxCalc = cs[
            settings.CONF_ASYMP_EXTRAP_OF_OVER_RELAX_CALC
        ]
        self.coarseMeshRebalance = cs[settings.CONF_COARSE_MESH_REBALANCE]
        self.inners = cs[CONF_INNERS]
        self.asympExtrapOfNodalCalc = cs[settings.CONF_ASYMP_EXTRAP_OF_NODAL_CALC]
        self.variantNodalSpatialApproximation = cs[
            settings.CONF_VARIANT_NODAL_SPATIAL_APPROXIMATION
        ]
        self.useRadialInnerIterationAlgorithm = cs[
            settings.CONF_USE_RADIAL_INNER_ITERATION_ALGORITHM
        ]
        self.nodalApproxXY = cs[settings.CONF_NODAL_APPROX_XY]
        self.nodalApproxZ = cs[settings.CONF_NODAL_APPROX_Z]
        self.listIsotxs = cs[settings.CONF_LIST_ISOTXS]
        self.neglectFis = cs[settings.CONF_NEGLECT_FIS]

        transportAndScatterOrder = cs[settings.CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER]
        if transportAndScatterOrder:
            (
                self.angularApprox,
                self.anisotropicScatteringApprox,
            ) = VARIANT_TRANSPORT_AND_SCATTER_ORDERS[transportAndScatterOrder]

        if cs[settings.CONF_DIF3D_DB]:
            self.detailedDb = "{}_dif3dMesh.h5".format(cs.caseTitle)
            self.extraOutputFiles.append(self.detailedDb)
            self.csObject = cs

    def fromReactor(self, reactor):
        """Set options from an ARMI composite to be modeled (often a ``Core``)"""
        globalFluxInterface.GlobalFluxOptions.fromReactor(self, reactor)
        # figure out XS lib
        if self.xsLibraryName is None:
            self.xsLibraryName = f"ISOTXS-c{reactor.p.cycle}"
            if not os.path.exists(self.xsLibraryName):
                self.xsLibraryName = "ISOTXS"

        self.inputFile = f"{self.label}.inp"
        self.outputFile = f"{self.label}.out"

    def resolveDerivedOptions(self):
        """
        Set other options that are dependent on previous phases of loading options.

        For example, the nodal boolean is a function of the kernelName, which may be adjusted
        by the user after importing an initial set of options from the user-input cs. And then
        all the files that come back (e.g. NHFLUX vs. RTFLUX) are derived from that flag.
        """
        globalFluxInterface.GlobalFluxOptions.resolveDerivedOptions(self)
        if self.nodal is None:
            self.nodal = any(
                settingValue in self.kernelName.lower()
                for settingValue in ["nodal", "variant"]
            )
        self.variantFlag = self.kernelName == settings.CONF_OPT_VARIANT
        self.extraOutputFiles.extend(self._specifyOutputFilesToRetrieve())
        if self.xsLibraryName:
            self.extraInputFiles.append((self.xsLibraryName, "ISOTXS"))
        if self.existingFixedSource:
            self.extraInputFiles.append(
                (self.existingFixedSource, self.existingFixedSource)
            )
        if self.isRestart:
            for _label, fnames in fileSetsHandler.specifyRestartFiles(self).items():
                self.extraInputFiles.extend([(f, f) for f in fnames])

    def _specifyOutputFilesToRetrieve(self):
        """
        Specify the DIF3D files to be retrieved from the run directory.
        """
        filesToRetrieve = {}
        outputs = self.neutronicsOutputsToSave
        if neutronics.ALL in outputs:
            filesToRetrieve = fileSetsHandler.specifyAllFiles(self)

        elif neutronics.RESTARTFILES in outputs:
            filesToRetrieve = fileSetsHandler.specifyRestartFiles(self)

        elif neutronics.FLUXFILES in outputs:
            filesToRetrieve = fileSetsHandler.specifyFluxFiles(self)

        files = []
        if filesToRetrieve:
            runLog.debug("Will retrieve files specified by setting {}".format(outputs))
            for originFile in filesToRetrieve:
                files.append((originFile, filesToRetrieve[originFile]))
        else:
            runLog.debug("No output will be retrieved from the run directory.")
        return files



