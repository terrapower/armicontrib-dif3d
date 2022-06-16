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
Contains components that prepare, execute, and read output from DIF3D.

Anything wanting DIF3D results should instantiate these objects and use them.
The objects here are intended to be short lived e.g. created, used, and destroyed.

The ``Dif3dExecuter`` orchestrates the tasks of interpreting relevant case settings,
writing a DIF3D input file, executing DIF3D upon that file, and reading the resultant
DIF3D output files back in. The results read from the output files are then applied to
the reactor model. In addition to dealing specifically with DIF3D itself, this
sub-classes the :py:class:`GlobalFluxExecuter
<armi:armi.physics.neutronics.globalFlux.globalFluxInterface.GlobalFluxExecuter>`, which
assists in performing geometry transformations, flux-based parameter computation, and
other tasks.

See Also
--------
armi.physics.neutronics.globalFlux.globalFluxInterface.GlobalFluxExecuter : ARMI-provided base class to ``GlobalFluxExecuter``.

~armicontrib.dif3d.executionOptions.Dif3dOptions : Options that control the behavior of the Executer and its components.

~armicontrib.dif3d.schedulers.Dif3dCoreEvaluation : One particular client of this code that runs DIF3D on a core.
"""

import subprocess

from armi.utils import directoryChangers
from armi.utils import outputCache
from armi.reactor import composites
from armi.physics import executers
from armi.physics.neutronics.globalFlux import globalFluxInterface

from . import inputWriters
from . import outputReaders
from . import executionOptions
from armi.utils import codeTiming


class Dif3dExecuter(globalFluxInterface.GlobalFluxExecuter):
    """
    A short-lived object that coordinates the prep, execution, and processing of a flux solve.

    This is an implementation of ARMI's ``DefaultExecuter`` and thus follows that
    pattern closely.

    Parameters
    ----------
    options: executionOptions.Dif3dOptions
        run settings
    armiObj : composite.ArmiObject
        The object representing the scope of the DIF3D run (e.g. the Core or SFP, etc.)
    """

    @codeTiming.timed
    def writeInput(self):
        """
        Write the input for DIF3D/VARIANT.

        Compose an InputWriter from options and send it off to do its work.
        """
        writer = inputWriters.Dif3dWriter(self.r, self.options)
        with open(self.options.inputFile, "w") as dragonInput:
            writer.write(dragonInput)

    @codeTiming.timed
    def _execute(self):
        """
        Execute DIF3D on an existing input file. Produce output files.
        """
        globalFluxInterface.GlobalFluxExecuter._execute(self)

        if self.options.executablePath is None:
            raise ValueError(
                f"Cannot find executable at {self.options.executablePath}. "
                f"Update run settings."
            )
        with open(self.options.inputFile) as inpF, open(
            self.options.outputFile, "w"
        ) as outF:
            process = subprocess.Popen(
                self.options.executablePath,
                shell=False,
                stdin=inpF,
                stdout=outF,
                cwd=self.options.runDir,
                universal_newlines=True,
                bufsize=1,
            )
            _stdout, _stderr = process.communicate()

        return True

    @codeTiming.timed
    def _readOutput(self):
        """Read output."""
        reader = outputReaders.Dif3dReader(self.options)
        return reader
