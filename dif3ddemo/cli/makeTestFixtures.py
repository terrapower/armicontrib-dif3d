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

r"""
Run suite of small inputs with a variety of settings.

This runs:

* A 3x3 matrix of runs 1/3-core DIF3D runs varying solver (Nodal, Finite Difference, 
  VARIANT diffusion) as well as solution type (real, adjoint, both).
* One VARIANT P3P1 transport case
* One DIF3D nodal full-core real flux case

Each case uses the DRAGON plugin to generate cross sections.

Site-specific executable paths and library paths should be passed in
on the command line. For example::

    dif3ddemo make-fixture-suite --dragonDataPath=\dragon\data\draglibendfb8r0SHEM361 > fixtures.log

"""
import os
import shutil
import sys
import tabulate

from armi import runLog
from armi.cli.entryPoint import EntryPoint
from armi.settings import caseSettings
from armi.reactor.tests import test_reactors
from armi.utils import directoryChangers
from armi.settings.fwSettings.globalSettings import (
    CONF_N_CYCLES,
    CONF_START_NODE,
    CONF_BURN_STEPS,
)
from armi.settings.fwSettings.databaseSettings import CONF_DB
from armi.physics.neutronics.settings import (
    CONF_GLOBAL_FLUX_ACTIVE,
    CONF_GEN_XS,
    CONF_XS_KERNEL,
    CONF_NEUTRONICS_KERNEL,
    CONF_NEUTRONICS_TYPE,
)
from armi.physics.fuelCycle.settings import CONF_SHUFFLE_LOGIC, CONF_FUEL_HANDLER_NAME

from terrapower.physics.neutronics.dragon.settings import (
    CONF_DRAGON_PATH,
    CONF_DRAGON_DATA_PATH,
)

from armicontrib.dif3d.tests import FIXTURE_DIR
from armicontrib.dif3d.settings import (
    CONF_DIF3D_PATH,
    CONF_NEUTRONICS_OUTPUTS_TO_SAVE,
    CONF_COARSE_MESH_REBALANCE,
    CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER,
)


class MakeFixtures(EntryPoint):
    """
    Build and run case suite for building test fixtures.

    This runs a specialized run based on an ARMI sample case and then overwrites
    the binary interface files in the test fixture folder. This captures
    the process for making the fixture files as well as providing a mechanism to
    update them as different features are needed.
    """

    name = "make-fixture-suite"
    settingsArgument = None

    def addOptions(self):
        self.createOptionFromSetting(CONF_DIF3D_PATH)
        self.createOptionFromSetting(CONF_DRAGON_PATH)
        self.createOptionFromSetting(CONF_DRAGON_DATA_PATH)
        self.parser.add_argument(
            "--post-process",
            "-p",
            action="store_true",
            default=False,
            help="Just post-process an existing suite; don't run",
        )

    @staticmethod
    def _initSettings():
        """
        Provide hard-coded settings rather than user-provided ones.

        Notes
        -----
        We need to override this method to set our own settings object.

        These settings are modified because the base case is used for many other
        tests across the ARMI ecosystem. We start from them but modify as necessary
        to get the fixture run set up. By re-using this input file, we will
        benefit from getting automatically-updated test inputs as the ARMI
        framework progresses in the future.
        """
        cs = caseSettings.Settings(
            os.path.join(test_reactors.TEST_ROOT, "armiRun.yaml")
        )
        print("setting from _initSettings", cs[CONF_DIF3D_PATH])

        return cs

    def invoke(self):
        if shutil.which(self.cs[CONF_DIF3D_PATH]) is None:
            runLog.error(
                "The requested DIF3D executable, `{}` cannot be found".format(
                    self.cs[CONF_DIF3D_PATH]
                )
            )
            sys.exit(1)

        if shutil.which(self.cs[CONF_DRAGON_PATH]) is None:
            runLog.error(
                "The requested DRAGON executable, `{}` cannot be found".format(
                    self.cs[CONF_DRAGON_PATH]
                )
            )
            sys.exit(1)

        if not self.args.post_process:
            suite = self._execute()
        else:
            suite = None
        self._postProcess(suite)

    def _execute(self):
        # pylint: disable=import-outside-toplevel; need to be configured first
        from armi import cases
        from armi.cases import suiteBuilder
        from armi.cases.inputModifiers.inputModifiers import (
            SettingsModifier,
            MultiSettingModifier,
            FullCoreModifier,
        )

        self._updateSettings()
        bp = self._updateBlueprints()

        baseCase = cases.Case(cs=self.cs, bp=bp)
        builder = suiteBuilder.FullFactorialSuiteBuilder(baseCase)
        problemTypes = [
            SettingsModifier(CONF_NEUTRONICS_KERNEL, "DIF3D-Nodal"),
            SettingsModifier(CONF_NEUTRONICS_KERNEL, "DIF3D-FD"),
            MultiSettingModifier(
                {
                    CONF_NEUTRONICS_KERNEL: "VARIANT",
                    CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER: "P1P0",
                }
            ),
        ]
        builder.addDegreeOfFreedom(problemTypes)
        solutionTypes = [
            SettingsModifier(CONF_NEUTRONICS_TYPE, "real"),
            # turn off coarse mesh rebalancing in all adjoint cases so they converge.
            MultiSettingModifier(
                {CONF_NEUTRONICS_TYPE: "adjoint", CONF_COARSE_MESH_REBALANCE: -1}
            ),
            MultiSettingModifier(
                {CONF_NEUTRONICS_TYPE: "both", CONF_COARSE_MESH_REBALANCE: -1}
            ),
        ]
        builder.addDegreeOfFreedom(solutionTypes)

        # add a higher-order VARIANT case as well.
        # note that you can't do scattering order beyond P1 with Dragon-produced XS
        builder.addModiferSet(
            [
                MultiSettingModifier(
                    {
                        CONF_NEUTRONICS_KERNEL: "VARIANT",
                        CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER: "P3P1",
                    }
                ),
            ]
        )
        # need full core too
        builder.addModiferSet(
            [
                FullCoreModifier(),
            ]
        )

        def namingFunc(index, case, _mods):
            number = f"{index:0>4}"
            name = (
                f"{case.cs[CONF_NEUTRONICS_KERNEL]}-"
                f"{case.cs[CONF_NEUTRONICS_TYPE]}-"
                f"{case.bp.gridDesigns['core'].symmetry}"
            )
            return os.path.join(
                ".",
                "case-suite",
                f"{number}-{name}",
                f"{baseCase.title}-{number}",
            )

        suite = builder.buildSuite(namingFunc=namingFunc)
        suite.echoConfiguration()
        suite.writeInputs()
        suite.run()
        return suite

    def _postProcess(self, suite=None):
        from armi import cases
        from armi.bookkeeping.db import databaseFactory

        if suite is None:
            cs = self._initSettings()
            suite = cases.CaseSuite(cs)
            suite.discover(rootDir="case-suite", patterns=["armiRun-????.yaml"])
        keffs = {}
        for case in suite:
            sym = f'-{case.bp.gridDesigns["core"].symmetry}'
            kern = case.cs[CONF_NEUTRONICS_KERNEL]
            order = case.cs[CONF_VARIANT_TRANSPORT_AND_SCATTER_ORDER]
            ntype = case.cs[CONF_NEUTRONICS_TYPE]
            with directoryChangers.DirectoryChanger(case.directory):
                db = databaseFactory(case.cs.caseTitle + ".h5", "r")
                with db:
                    r = db.load(0, 0)
                    keffs[kern + order + sym, ntype] = r.core.p.keff

        table = []
        kernels, ntypes = zip(*keffs.keys())
        # uniquify
        kernels = sorted(list(set(kernels)))
        ntypes = ["real", "adjoint", "both"]
        for k in kernels:
            line = [k] + [keffs.get((k, t), "-") for t in ntypes]
            table.append(line)

        print("Keff summary for all runs")
        print(
            tabulate.tabulate(
                table, headers=ntypes, floatfmt=".9f", disable_numparse=True
            )
        )

    def _updateSettings(self):
        cs = self.cs
        print("setting from updateSettings", cs[CONF_DIF3D_PATH])
        cs[CONF_N_CYCLES] = 1
        cs[CONF_START_NODE] = 0
        cs[CONF_BURN_STEPS] = 0
        cs[CONF_GLOBAL_FLUX_ACTIVE] = "Neutron"
        cs[CONF_GEN_XS] = "Neutron"
        cs[CONF_XS_KERNEL] = "DRAGON"
        cs[CONF_NEUTRONICS_KERNEL] = "DIF3D-Nodal"
        cs[CONF_DB] = True
        cs[CONF_NEUTRONICS_OUTPUTS_TO_SAVE] = "All"

        # disable fuel management
        cs[CONF_SHUFFLE_LOGIC] = ""
        cs[CONF_FUEL_HANDLER_NAME] = ""

    def _updateBlueprints(self):
        from armi.reactor import blueprints
        from armi.reactor.blueprints import isotopicOptions

        # modify nuclide expansion flags as well b/c the main DRAGON lib only has C12.
        bp = blueprints.loadFromCs(self.cs)
        bp.nuclideFlags = isotopicOptions.genDefaultNucFlags()
        bp.nuclideFlags["C"].expandTo = ["C12"]
        bp.nuclideFlags["W"].expandTo = ["W182", "W183", "W184", "W186"]
        return bp


class CopyFixtureFiles(EntryPoint):
    """
    Move fixture files to fixture.

    Specifically moves files to the test fixture for unit testing.
    """

    name = "copy-fixture-files"
    settingsArgument = None

    def _copyOutputs(self):
        runDir = os.path.join("case-suite", "0000-DIF3D-Nodal-real-third periodic")
        for output in ["RZFLUX", "DIF3D", "PWDINT", "GEODST", "LABELS", "RTFLUX"]:
            shutil.copy(os.path.join(runDir, output), FIXTURE_DIR)

    def invoke(self):
        self._copyOutputs()
