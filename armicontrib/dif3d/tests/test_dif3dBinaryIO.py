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
Test reading/writing of the DIF3D-generated binary file entitled ``DIF3D``.

This is a small file that contains high-level info about a DIF3D run.
"""
import unittest
import os

from ..binaryIO import dif3dFile, pkedit

THIS_DIR = os.path.dirname(__file__)
SAMPLE_DIF3D = os.path.join(THIS_DIR, "fixtures", "DIF3D")
SAMPLE_DIF3D_FD = os.path.join(THIS_DIR, "fixtures", "DIF3D-FD")

SAMPLE_PKEDIT = os.path.join(THIS_DIR, "fixtures", "PKEDIT")


class TestDIF3DIO(unittest.TestCase):
    """Ensure we can read/write DIF3D binary files."""

    def testReadKeff(self):
        data = dif3dFile.Dif3dStream.readBinary(SAMPLE_DIF3D)
        self.assertAlmostEqual(data.keffData["EFFK"], 1.0083017198449564)
        self.assertEqual(
            dif3dFile.Convergence(data.intControls["IRETRN"]),
            dif3dFile.Convergence.CONVERGED,
        )

    def testReadDominanceRatio(self):
        # check dominance ratio
        # huh, in the FD cases version this is non-zero but in the hex nodal case it is zero.
        data = dif3dFile.Dif3dStream.readBinary(SAMPLE_DIF3D_FD)
        self.assertAlmostEqual(data.keffData["SIGBAR"], 0.750317601546759)

        self.assertIn("keff", "".join(data.makeSummary()))

    def testWrite(self):
        """Ensure that we can write a modified DIF3D file."""
        data = dif3dFile.Dif3dStream.readBinary(SAMPLE_DIF3D)
        dif3dFile.Dif3dStream.writeBinary(data, "DIF3D2")
        data2 = dif3dFile.Dif3dStream.readBinary("DIF3D2")
        self.assertListEqual(
            list(data.keffData.values()), list(data2.keffData.values())
        )
        os.remove("DIF3D2")


class TestPKEDIT(unittest.TestCase):
    """Ensure we can read/write PKEDIT binary files."""

    def testRead(self):
        data = pkedit.PkeditStream.readBinary(SAMPLE_PKEDIT)
        self.assertGreaterEqual(data.peakPowerDensity.min(), 0.0)

    def testWrite(self):
        """Ensure that we can write a modified PKEDIT file."""
        data = pkedit.PkeditStream.readBinary(SAMPLE_PKEDIT)
        pkedit.PkeditStream.writeBinary(data, "PKEDIT2")
        data2 = pkedit.PkeditStream.readBinary("PKEDIT2")
        self.assertTrue((data.peakPowerDensity == data2.peakPowerDensity).all())
        os.remove("PKEDIT2")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
