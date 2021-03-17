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

import math
import pathlib
import sys

import matplotlib.pyplot as plt

import armi
import dif3ddemo

from bench_data import *

armi.configure(dif3ddemo.Dif3dDragonApp())

from armi.bookkeeping.db import Database3
from armi.reactor.flags import Flags
from armi.physics.neutronics import energyGroups
from armi.utils import units


def normalizeFlux(flux, _energy):
    """
    Normalize to equal peak flux. This helps simplify things because the energy ranges
    are so different.
    """

    norm = 1.0 / max(flux)

    return [f * norm for f in flux]


def plotFlux(block, benchFlux, mcnpFlux, benchEnergy, title):
    armiEnergy = [e for e in energyGroups.getGroupStructure("ANL33")]

    ax = plt.subplot(111)
    ax.set_xscale("log")

    benchFlux = normalizeFlux(benchFlux, benchEnergy)
    mcnpFlux = normalizeFlux(mcnpFlux, benchEnergy)
    # duplicate the last group flux to get a full step in the chart
    benchFlux.append(benchFlux[-1])
    mcnpFlux.append(mcnpFlux[-1])
    plt.step(benchEnergy, benchFlux, label="Benchmark", where="post")
    plt.step(benchEnergy[:-1], mcnpFlux, label="Calculated MCNP", where="post")

    flux = block.getMgFlux()[:-12]
    # make the last flux value the same as the one before it so the step chart doesnt
    # look weird
    flux[-1] = flux[-2]
    energy = armiEnergy[:-12]
    flux = normalizeFlux(flux, energy)

    plt.step(energy, flux, label="ARMI DIF3D", where="post")

    plt.title(title)
    plt.legend()
    plt.xlabel("Energy (eV)")
    plt.ylabel("Normalized Flux")
    plt.show()


db = Database3(pathlib.Path(sys.argv[1]), "r")

# Get both energy ranges into eV
midBenchEnergy = [erg * 1000.0 for erg in BENCH_MIDPLANE_ENERGY]
lowBenchEnergy = [erg * 1000.0 for erg in BENCH_LOWER_ENERGY]

with db:
    r = db.load(0, 0)

grid = r.core.spatialGrid
locator = grid.getLocatorFromRingAndPos(2, 6)
a = r.core.childrenByLocator[locator]
# Detector blocks are tagged with the TEST flag. The block corresponding to the core
# mid-plane is the 4th (index 3)
test_blocks = a.getBlocks(Flags.TEST)
mid_block = test_blocks[3]
low_block = test_blocks[1]

plotFlux(mid_block, BENCH_MIDPLANE_FLUX, MCNP_MIDPLANE_FLUX, midBenchEnergy, "Normalized Flux at Core Midplane")
plotFlux(low_block, BENCH_LOWER_FLUX, MCNP_LOWER_FLUX, lowBenchEnergy, "Normalized Flux at 80cm Below Core Midplane")
plotFlux()
