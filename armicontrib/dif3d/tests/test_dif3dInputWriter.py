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
Tests for writing DIF3D input file
"""
import unittest
import os

from armi.reactor.tests import test_reactors
from armi.physics.neutronics.settings import CONF_NEUTRONICS_KERNEL
from armi.tests import ArmiTestHelper

from armicontrib.dif3d import inputWriters
from armicontrib.dif3d import executers
from armicontrib.dif3d import executionOptions


from . import FIXTURE_DIR, THIS_DIR

INPUT_TEST = os.path.join(THIS_DIR, "dif3d-test.inp")
INPUT_REF = os.path.join(FIXTURE_DIR, "dif3d-ref.inp")


class TestInputWriter(ArmiTestHelper):
    def setUp(self):
        self.o, self.r = test_reactors.loadTestReactor()
        self.o.cs[CONF_NEUTRONICS_KERNEL] = "DIF3D-Nodal"

    def testWriteInput(self):
        """Write input and compare to reference input."""
        opts = executionOptions.Dif3dOptions("Test input file")

        opts.fromUserSettings(self.o.cs)
        opts.resolveDerivedOptions()
        writer = inputWriters.Dif3dWriter(self.r, opts)
        with open(INPUT_TEST, "w") as stream:
            writer.write(stream)
        self.compareFilesLineByLine(INPUT_REF, INPUT_TEST)


if __name__ == "__main__":
    unittest.main()
