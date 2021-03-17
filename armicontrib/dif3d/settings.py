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
Define DIF3D-specific ARMI user-configurable settings.

This module implements the :py:meth:`ArmiPlugin.defineSettings()
<armi:armi.plugins.ArmiPlugin.defineSettings()>` and
:py:meth:`ArmiPlugin.defineSettingsValidators()
<armi:armi.plugins.ArmiPlugin.defineSettingsValidators()>` Plugin APIs. Aside from the
settings that control DIF3D's behavior specifically, this provides new options to the
ARMI built-in ``neutronicsKernel`` setting:

    * "DIF3D-Nodal": Enable DIF3D with nodal solver.
    * "DIF3D-FD": Enable DIF3D with finite-difference solver.
    * "VARIANT": Enable DIF3D with VARIANT Pn solver.
"""
import shutil

from armi.physics.neutronics import settings as neutronicsSettings
from armi.settings import setting
from armi.operators import settingsValidation
from armi.physics import neutronics


CONF_ASYMP_EXTRAP_OF_OVER_RELAX_CALC = "asympExtrapOfOverRelaxCalc"
CONF_ASYMP_EXTRAP_OF_NODAL_CALC = "asympExtrapOfNodalCalc"
CONF_LIST_ISOTXS = "listIsotxs"
CONF_NODAL_APPROX_XY = "nodalApproxXY"
CONF_NODAL_APPROX_Z = "nodalApproxZ"
CONF_COARSE_MESH_REBALANCE = "coarseMeshRebalance"
CONF_D3D_MEM = "d3dMem"
CONF_D3D_MEM2 = "d3dMem2"
CONF_DIF3D_PATH = "dif3dExePath"
CONF_ERF = "erf"
CONF_NEGLECT_FIS = "neglectFis"
CONF_NIP_MEM = "nipMem"
CONF_OUTERS = "outers"
CONF_INNERS = "inners"
CONF_XS_MEM = "xsMem"
CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER = "variantTransportAndScatterOrder"
CONF_EPS_BURN_TIME = "epsBurnTime"
CONF_EPS_CYCLIC = "epsCyclic"
CONF_EPS_NDENS = "epsNdens"
CONF_NEUTRONICS_OUTPUTS_TO_SAVE = "neutronicsOutputsToSave"
CONF_USE_RADIAL_INNER_ITERATION_ALGORITHM = "useRadialInnerIterationAlgorithm"
CONF_VARIANT_NODAL_SPATIAL_APPROXIMATION = "variantNodalSpatialApproximation"
CONF_DIF3D_DB = "writeDif3dDb"


CONF_OPT_DIF3DNODAL = "DIF3D-Nodal"
CONF_OPT_DIF3DFD = "DIF3D-FD"
CONF_OPT_VARIANT = "VARIANT"

# This should live in the gamma plugin, but the DIF3D plugin is still using it to do
# something with input file declarations. Should refactor and migrate this.
CONF_OPT_GAMSOR = "GAMSOR"


KERNELS = {CONF_OPT_DIF3DNODAL, CONF_OPT_DIF3DFD, CONF_OPT_VARIANT}


def defineSettings():
    settings = [
        setting.Setting(
            CONF_DIF3D_DB,
            default=False,
            label="Output database with DIF3D neutronics mesh",
            description="If enabled, a database will be created containing the results "
            "of the most recent DIF3D invocation before converting back to the input "
            "mesh. This is useful for visualizing/analyzing the direct results of the "
            "DIF3D run without any mesh conversions taking place.",
        ),
        setting.Option(CONF_OPT_DIF3DNODAL, neutronicsSettings.CONF_NEUTRONICS_KERNEL),
        setting.Option(CONF_OPT_DIF3DFD, neutronicsSettings.CONF_NEUTRONICS_KERNEL),
        setting.Option(CONF_OPT_VARIANT, neutronicsSettings.CONF_NEUTRONICS_KERNEL),
        setting.Setting(
            CONF_ASYMP_EXTRAP_OF_OVER_RELAX_CALC,
            default=0,
            label="Acceleration of optimum overrelaxation factor calculation",
            description=(
                "Asymptotic source extrapolation of power iterations used to estimate "
                "the spectral radius of each within group iteration matrix. Intended "
                "for problems with overrelaxation factor > 1.8."
            ),
        ),
        setting.Setting(
            CONF_ASYMP_EXTRAP_OF_NODAL_CALC,
            default=0,
            label="Perform asymptotic source extrapolation.",
            description=(
                "Perform asymptotic source extrapolation on the the nodal outer "
                "iterations. Applies to DIF3D-Nodal and VARIANT."
            ),
        ),
        setting.Setting(
            CONF_LIST_ISOTXS,
            default=False,
            label="listIsotxs",
            description="list ISOTXS in the DIF3D output file",
        ),
        setting.Setting(
            CONF_NODAL_APPROX_XY,
            default=40,
            label="XY Nodal approx",
            description=(
                "Approximation controls in XY-Plane (LMN). L can either be 0 (diffusion) "
                "or 1 (transport), M is the flux approximation order (2: quadratic, "
                "3: cubic, or 4: quartic), and N is the leakage approximation order "
                "(0: constant or 2: quadratic). For details, see A.DIF3D file formats "
                "document, under TYPE 10."
            ),
        ),
        setting.Setting(
            CONF_NODAL_APPROX_Z,
            default=32,
            label="Z Nodal approx",
            description=(
                "Approximation controls in Z-direction. M is the flux approximation "
                "order (2: quadratic, 3: cubic, or 4: quartic), and N is the leakage approximation "
                "order (0: constant or 2: quadratic). For details, see A.DIF3D file formats"
                " document, under TYPE 10."
            ),
        ),
        setting.Setting(
            CONF_COARSE_MESH_REBALANCE,
            default=0,
            label="Coarse mesh rebalance",
            description=(
                "Sets the coarse-mesh rebalance acceleration to something other than the "
                "default."
            ),
        ),
        setting.Setting(
            CONF_D3D_MEM,
            default=24000000,
            label="Extended Core Memory Size",
            description=(
                "POINTR container array size in extended core memory for A.DIF3D card of "
                "DIF3D/REBUS. Max recommended=159999000"
            ),
        ),
        setting.Setting(
            CONF_D3D_MEM2,
            default=40000000,
            label="Fast Core Memory Size",
            description=(
                "POINTR container array size in fast core memory in REAL*8 words "
                "in A.DIF3D card of DIF3D/REBUS. Max recommended=40000000"
            ),
        ),
        setting.Setting(
            CONF_DIF3D_PATH,
            default="dif3d",
            label="DIF3D path",
            description="The path do the DIF3D executable",
            options=[],
        ),
        setting.Setting(
            CONF_ERF,
            default=0.04,
            label="Inner iteration error reduction factor",
            description=(
                "Error reduction factor to be achieved by each series of inner "
                "iteration for each group during a shape calculation in DIF3D/REBUS. "
                "Reduce to 0.01 if dominance ratio estimate is sporadic, or if pointwise "
                "fission source convergence is not monotonic."
            ),
        ),
        setting.Setting(
            CONF_NEGLECT_FIS,
            default=0.001,
            label="Min. fission source",
            description=(
                "Any pointwise fission source will be neglected in the pointwise "
                "fission source convergence test if it is less than this factor "
                "times the RMS fission source in DIF3D/REBUS"
            ),
        ),
        setting.Setting(
            CONF_NIP_MEM,
            default=40000000,
            label="Memory for A.NIP3",
            description=(
                "Size of main core storage array for geometry processing module "
                "(GNIP4C) in A.NIP card of DIF3D/REBUS. Max recommended=40000000"
            ),
        ),
        setting.Setting(
            CONF_OUTERS,
            default=100,
            label="Max Outer Iterations",
            description="Max number of outer iterations to converge",
        ),
        setting.Setting(
            CONF_INNERS,
            default=0,
            label="Inner Iterations",
            description=(
                "XY and Axial partial current sweep inner iterations. 0 is let DIF3D "
                "pick or use default if can't pick."
            ),
        ),
        setting.Setting(
            CONF_XS_MEM,
            default=40000000,
            label="XS Processing Memory Size",
            description=(
                "Size of main core storage array for cross section processing modules. "
                "Max recommended=40000000"
            ),
        ),
        setting.Setting(
            CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER,
            default="",
            label="VARIANT Flux/Leakage Angle and Scattering Orders",
            description=(
                "The flux/leakage angle and scattering orders to use with neutronics "
                "kernel VARIANT."
            ),
            options=["", "P1P0", "P3P1", "P3P3", "P5P1", "P5P3"],
        ),
        setting.Setting(
            CONF_EPS_BURN_TIME,
            default=1.0,
            label="Burn time eps",
            description=(
                "Burn time eps (Cycle length convergence.  "
                "Set to 1.0 if the cycle length is known.)"
            ),
        ),
        setting.Setting(
            CONF_EPS_CYCLIC,
            default=0.001,
            label="Cyclic density eps",
            description="max relative error in isotope stage density during cyclics  (0.001)",
        ),
        setting.Setting(
            CONF_EPS_NDENS,
            default=0.001,
            label="Region Ndens eps",
            description="max relative error in any isotope in region density (0.001)",
        ),
        setting.Setting(
            CONF_NEUTRONICS_OUTPUTS_TO_SAVE,
            default="Input/Output",
            label="Save DIF3D Files",
            description=(
                "Defines outputs from DIF3D-based neutronics kernel to be copied from "
                "the fast path to the network drive for inspection, restarts, debugging, "
                "etc."
            ),
            options=["", "Input/Output", "Flux files", "Restart files", "All"],
        ),
        setting.Setting(
            CONF_USE_RADIAL_INNER_ITERATION_ALGORITHM,
            default=False,
            label="Use Radial Inner Iter Algorithm",
            description=(
                "Use the VARIANT Radial Inner Iteration Algorithm which is helpful for "
                "cases with small node mesh. Type 12 card in A.DIF3D"
            ),
        ),
        setting.Setting(
            CONF_VARIANT_NODAL_SPATIAL_APPROXIMATION,
            default="20501",  # minimum required for hex
            label="VARIANT Nodal Spatial Approx.",
            description=(
                "The Nodal Spatial polynomial approximation in VARIANT. See Type 12 card "
                "in A.DIF3D for information."
            ),
        ),
    ]
    return settings


def defineSettingValidators(inspector):
    """Define DIF3D-related setting validations."""
    queries = [
        settingsValidation.Query(
            lambda: (
                inspector.cs[neutronicsSettings.CONF_NEUTRONICS_KERNEL]
                == CONF_OPT_DIF3DNODAL
                and neutronics.adjointCalculationRequested(inspector.cs)
            )
            and inspector.cs[CONF_COARSE_MESH_REBALANCE] > -1,
            "The DIF3D nodal approximation will not converge for the adjoint flux solution if the "
            f"`{CONF_COARSE_MESH_REBALANCE}` setting is enabled.",
            f"Disable `{CONF_COARSE_MESH_REBALANCE}`?",
            lambda: inspector._assignCS(CONF_COARSE_MESH_REBALANCE, -1),
        ),
        settingsValidation.Query(
            lambda: inspector.cs[neutronicsSettings.CONF_NEUTRONICS_KERNEL]
            == CONF_OPT_DIF3DNODAL
            and inspector.cs[CONF_ASYMP_EXTRAP_OF_NODAL_CALC] == -1,
            f"The value of `{CONF_ASYMP_EXTRAP_OF_NODAL_CALC}` is not valid "
            f"for {CONF_OPT_DIF3DNODAL}",
            "Set value to 0 to perform asymptotic source extrapolation?",
            lambda: inspector._assignCS(CONF_ASYMP_EXTRAP_OF_NODAL_CALC, 0),
        ),
        settingsValidation.Query(
            lambda: inspector.cs[neutronicsSettings.CONF_NEUTRONICS_KERNEL]
            == CONF_OPT_VARIANT
            and not inspector.cs[CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER],
            f"The value of `{CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER}` must be set "
            f"for {CONF_OPT_VARIANT}",
            "Set value to P3P3?",
            lambda: inspector._assignCS(
                CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER, "P3P3"
            ),
        ),
        settingsValidation.Query(
            lambda: shutil.which(
                inspector.cs[CONF_DIF3D_PATH]
            )
            is None,
            "The provided DIF3D executable cannot be found: {}".format(inspector.cs[CONF_DIF3D_PATH]),
            "Please update executable location to the valid location.",
            inspector.NO_ACTION,
        ),
    ]
    return queries
