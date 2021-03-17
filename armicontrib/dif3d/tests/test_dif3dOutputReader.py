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
Test output reading.

The output files are created by a DRAGON/DIF3D run as coordinated
by the :py:mod:`dif3ddemo.cli.makeTestFixtures` entry point.

Specifically, the 1/3-core nodal hex case is read here.

The basis for the test results is shown in :doc:`/testing`.
"""
import unittest

import numpy as np
from numpy import testing

from armi.reactor.tests import test_reactors
from armi.utils import directoryChangers

from armicontrib.dif3d import outputReaders
from armicontrib.dif3d import executers
from armicontrib.dif3d import executionOptions


from . import FIXTURE_DIR


class TestOutputReader(unittest.TestCase):
    """Test case for output reading."""

    @classmethod
    def setUpClass(cls):
        o, r = test_reactors.loadTestReactor()
        opts = executionOptions.Dif3dOptions("test-output-file")
        opts.fromUserSettings(o.cs)
        opts.resolveDerivedOptions()
        opts.fromReactor(r)
        with directoryChangers.DirectoryChanger(FIXTURE_DIR):
            outputReader = outputReaders.Dif3dReader(opts)
            outputReader.apply(r)

        cls.r = r

    def test_readKeff(self):
        """
        Read output files directly from binary files in test fixture.
        """

        # copied from 0000-DIF3D-Nodal-real-third periodic\dif3d-R-armiRun-0000-0-0.out
        self.assertAlmostEqual(self.r.core.p.keff, 1.00830171984)

    def test_readTotalFlux(self):
        """
        Compare flux in a block to a manually extracted flux from the text output file.

        Grab plenum block in ring 3, position 2, axial node 5.
        This is position label A3002E
        """
        loc = self.r.core.spatialGrid[1, 1, 0]
        assem = self.r.core.childrenByLocator[loc]
        block = assem[4]
        vol = block.getVolume()
        fluxVol = block.p.flux * vol
        # the printout is rounded off with 5 decimals, so we round
        # to 18-5 places = 13 for a perfect match.
        self.assertAlmostEqual(round(fluxVol, -13), 3.05696e18)

    def test_readPeakFlux(self):
        """Test reading peak flux from region A3002E"""
        # avg flux is 1.67752e14
        # round 14-5 = 9 places
        loc = self.r.core.spatialGrid[1, 1, 0]
        assem = self.r.core.childrenByLocator[loc]
        block = assem[4]
        self.assertAlmostEqual(round(block.p.fluxPeak, -9), 3.81625e14)

    def test_readMGFlux(self):
        """Compare processed values with entries copied from output file"""
        expected = np.array(
            [
                float(v)
                for v in (
                    "1.47312E+14      2.30742E+15      1.53930E+16      2.54007E+16      6.25577E+16      1.44366E+17 "
                    "1.97879E+17      4.38889E+17      3.41350E+17      3.64783E+17      2.39746E+17      2.56849E+17 "
                    "2.73795E+17      1.71025E+17      1.11952E+17      8.32989E+16      3.26362E+16      2.98441E+16 "
                    "7.66527E+16      5.52959E+16      5.77510E+16      3.08758E+16      1.98528E+16      1.15805E+16 "
                    "5.43152E+15      3.75557E+15      1.38772E+15      6.75732E+14      9.02733E+14      2.31725E+14 "
                    "3.40262E+14      3.05077E+12      3.51154E+12 "
                ).split()
            ]
        )
        loc = self.r.core.spatialGrid[1, 1, 0]
        assem = self.r.core.childrenByLocator[loc]
        block = assem[4]
        mgflux = block.p.mgFlux * block.getVolume()
        # 1e-5 best we can do b/c output table only prints 5 decimals
        testing.assert_allclose(mgflux, expected, rtol=1e-5)

    def test_power(self):
        """
        Compare power, power density, and peak power density  with value manually extracted

        Values came from REGION TOTALS table in output.
        Note that we need to use a core region here rather than a plenum.
        """
        powExpected = 7.34698e05
        powDensityAvgExpected = 1.20951e02
        powDensityPeakExpected = 1.69977e02
        loc = self.r.core.spatialGrid[1, 1, 0]
        assem = self.r.core.childrenByLocator[loc]
        block = assem[3]
        # for each float val, round by 5 digits - the exponent to match the table
        self.assertAlmostEqual(round(block.p.power, 5 - 5), powExpected)
        self.assertAlmostEqual(round(block.p.pdens, 5 - 2), powDensityAvgExpected)
        self.assertAlmostEqual(round(block.p.ppdens, 5 - 2), powDensityPeakExpected)

    def test_tenthousandRegion(self):
        line = (
            "     REGION    10009  A9017710010  A9017810011  A9016A10012  A9016B10013  "
            "A9016C10014  A9016D10015  A9016E10016  A9016F10017  A9016G\n"
        )
        reader = outputReaders.Dif3dStdoutReader(None)
        labels = reader._getRegionLabels(line)  # pylint: disable=protected-access
        self.assertIn("A9016F", labels)
        self.assertEqual(len(labels), 9)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
