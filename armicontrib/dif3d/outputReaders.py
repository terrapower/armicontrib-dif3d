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
Components for reading DIF3D output files and updating ARMI state with results.

``Dif3dReader`` reads DIF3D binary interface files, many of which can be read and
manipulated with :py:mod:`armi.nuclearDataIO`. In addition, ``Dif3dStdoutReader``
extracts results from captured DIF3D standard output. This is needed to capture output
that is not written to the binary interface; currently it only reads block peak fluxes.

To apply DIF3D results to a ``reactor``, run something like::

    opts = Dif3dOptions()
    opts.fromUserSettings(cs)
    opts.fromReactor(reactor)
    reader = Dif3dReader(opts)
    reader.apply(reactor)
"""
import os

import numpy as np

from armi.nuclearDataIO import geodst, labels, rtflux, pwdint
from armi.reactor import reactors
from armi import runLog

from armi.bookkeeping.db import Database3

from .binaryIO import dif3dFile, pkedit
from .const import SolutionType
from .executionOptions import Dif3dOptions
from .inputWriters import getDIF3DStyleLocatorLabel

# TODO: should be a GlobalFluxResultMapper subclass to get dpa, etc.
class Dif3dReader:
    """
    Read DIF3D output files and apply to ARMI.

    Uses the ARMI state plus a template.
    """

    def __init__(self, options: Dif3dOptions):
        """
        Initialize the reader and check the output file, but do not read it yet.

        See Also
        --------
        apply
            Applies the results to a reactor object.
        """
        self.opts = options
        self.r: reactors.Reactor = None
        self._geom: geodst.GeodstData = None
        self._labels: labels.LabelsData = None
        self._dif3dData: dif3dFile.Dif3dData = None
        self._check()

    def _check(self):
        """
        Check current directory for valid output files.

        Also check convergence flag and warn if not converged.

        Notes
        -----
        Some users may prefer an error if the file is not converged, and this could
        become a user option if desired. Even unconverged files are useful in some
        analyses.

        Unfortunately, DIF3D 11.0 does not write the ``ITPS`` item in the
        standard RZFLUX file for
        convergence (this can be verified clearly by looking at ``wrzflx.f``
        in the source code. Thus the convergence check must come from elsewhere.
        It does write this information to the code-specific ``DIF3D``
        file, which is both and input and an output to a DIF3D run.
        """
        if not os.path.exists("DIF3D"):
            raise RuntimeError(
                "No valid DIF3D output found. Check DIF3D stdout for errors."
            )
        self._dif3dData = dif3dFile.Dif3dStream.readBinary(dif3dFile.DIF3D)
        runLog.info(
            "Found DIF3D output with:\n\t" + "\n\t".join(self._dif3dData.makeSummary())
        )

        if self._dif3dData.convergence != dif3dFile.Convergence.CONVERGED:
            runLog.warning(
                f"DIF3D run did not converge. Convergence state is {self._dif3dData.convergence}."
            )

    def apply(self, reactor: reactors.Reactor):
        """
        Read data from binary interface files apply to the ARMI model.

        Generally, the armiObject is the Case's Reactor object.
        """
        self.r = reactor
        self._readGeometry()
        self._readKeff()
        self._readPower()
        self._readFluxes()
        self._readPeakFluxes()

        if self.opts.detailedDb is not None:
            with Database3(self.opts.detailedDb, "w") as dbo:
                dbo.writeInputsToDB(self.opts.csObject)
                dbo.writeToDB(self.r)

    def getKeff(self):
        """Return keff directly from output files without applying to reactor."""
        return self._dif3dData.keff

    def _readGeometry(self):
        """Read basic region labels and geometry information into memory."""
        self._geom = geodst.readBinary(geodst.GEODST)
        self._labels = labels.readBinary(labels.LABELS)

    def _readKeff(self):
        """Store keff from the outputs onto the reactor model."""
        # TODO: Maybe also store the dominance ratio (SIGBAR) on the core?
        self.r.core.p.keff = self._dif3dData.keff

    def _readPower(self):
        """
        Read power density.

        Notes
        -----
        Peak power density in high-resolution finite difference cases can be
        gotten from PWDINT, but in nodal cases it cannot, and the code will
        have to process peaking factors (or estimations thereof) from
        elsewhere. It appears from the source code that the PKEDIT file may have
        power peaking information written to it. We can read that.
        ``/src_DIF3D/lib/wpkedt.f``

        This reads potentially large binary files into RAM. This is expected
        to be ok for most problems (even large full-core ones) on reasonable
        machines.
        """
        if self.opts.adjoint and not self.opts.real:
            runLog.extra("Skipping power update due to purely adjoint case")
            return
        runLog.extra("Reading power distributions from PWDINT")
        pwdintData = pwdint.PwdintStream.readBinary(pwdint.PWDINT)
        runLog.extra("Reading peak power distributions from PKEDIT")
        pkeditData = pkedit.PkeditStream.readBinary(pkedit.PKEDIT)
        for b in self.r.core.getBlocks():
            meshesInRegion, regIndex = self._getMeshesInRegion(b)
            numMeshes = meshesInRegion.shape[0]
            volumeCC = self._geom.regionVolumes[regIndex]
            pdenses = np.zeros(numMeshes)
            ppdenses = np.zeros(numMeshes)
            # pylint: disable=not-an-iterable.; pylint bug RE .T on ndarray
            for meshI, (i, j, k) in enumerate(meshesInRegion):
                pdenses[meshI] = pwdintData.powerDensity[i, j, k]
                ppdenses[meshI] = pkeditData.peakPowerDensity[i, j, k]
            # assume all meshes in region are the same size (e.g. triangles in a hex)
            b.p.pdens = pdenses.mean()
            b.p.ppdens = ppdenses.max()
            b.p.power = b.p.pdens * volumeCC

    def _getMeshesInRegion(self, b):
        """
        Find which mesh indices contain data for this object.

        Notes
        -----
        This could be cached in RAM so it's not computed for power and each flux
        if it turns out to be slow. Pending profiler results.
        """
        regionName = getDIF3DStyleLocatorLabel(b)
        regInd = np.where(self._labels.regionLabels == regionName)[0][0]
        regNum = regInd + 1
        return np.array(np.where(self._geom.coarseMeshRegions == regNum)).T, regInd

    def _readFluxes(self):
        """
        Read real and/or adjoint fluxes from binary interface files onto data model.

        This most straightforward place to get this from is from
        the :py:mod:`armi.nuclearDataIO.cccc.rtflux` CCCC interface files, which DIF3D can be asked
        to write in all geometry options. RTFLUX has the data
        collected by i,j,k mesh index, and it is possible that each
        ARMI block covers more than one (i,j,k) mesh point. This is
        common, e.g. in finite difference cases.

        Notes
        -----
        This may need more conditionals to expand it to work with photon parameters
        in gamma transport cases.
        """
        solutionType = SolutionType.fromGlobalFluxOpts(self.opts)
        if solutionType in (
            SolutionType.REAL,
            SolutionType.REAL_AND_ADJOINT,
        ):
            runLog.extra("Reading real flux from RTFLUX")
            rtfluxData = rtflux.RtfluxStream.readBinary(rtflux.RTFLUX)
            self._applyFluxData(rtfluxData, "mgFlux", "flux")

        if solutionType in (
            SolutionType.ADJOINT,
            SolutionType.REAL_AND_ADJOINT,
        ):
            runLog.extra("Reading adjoint flux from ATFLUX")
            atfluxData = rtflux.AtfluxStream.readBinary(rtflux.ATFLUX)
            self._applyFluxData(atfluxData, "adjMgFlux", "fluxAdj")

    def _applyFluxData(self, fluxData, mgParam, fluxParam):
        """
        Apply flux in a data structure to the reactor as certain parameters.

        This is functionalized so it can be used for real and/or adjoint flux
        e.g. from RTFLUX and ATFLUX files.

        Unfortunately, the peak flux information is not available in any of the
        binary interface files. It is listed in the ``REGION TOTALS`` part of
        the standard output file and may need to be read from there.
        """
        self._checkKeffs(fluxData)
        ng = fluxData.metadata["NGROUP"]
        for b in self.r.core.getBlocks():
            meshesInRegion, _regIndex = self._getMeshesInRegion(b)
            numMeshes = meshesInRegion.shape[0]
            fluxes = np.zeros((ng, numMeshes))
            # pylint: disable=not-an-iterable.; pylint bug RE .T on ndarray
            for meshI, (i, j, k) in enumerate(meshesInRegion):
                fluxes[:, meshI] = fluxData.groupFluxes[i, j, k, :]
            # mean over mesh axis gives G-group avg
            setattr(b.p, mgParam, fluxes.mean(1))
            setattr(b.p, fluxParam, getattr(b.p, mgParam).sum())

    def _readPeakFluxes(self):
        """Read peak fluxes from output."""
        if self.opts.adjoint and not self.opts.real:
            runLog.extra("Skipping peak flux update due to purely adjoint case")
            return

        stdoutReader = Dif3dStdoutReader(self.opts.outputFile)
        peakFluxes = stdoutReader.readRegionTotals()
        for b in self.r.core.getBlocks():
            b.p.fluxPeak = peakFluxes[getDIF3DStyleLocatorLabel(b)]

    def _checkKeffs(self, fluxData):
        """
        The keff on the flux file should be consistent with the problem keff.

        These values are not binary identical and need a float comparison.

        This helps catch situations when the adjoint run converges differently
        from a real run in a real and adjoint run, among other restart issues,
        etc.
        """
        if (
            abs(fluxData.metadata["EFFK"] - self.r.core.p.keff) / self.r.core.p.keff
            > 1e-5
        ):
            runLog.warning(
                "DIF3D/RTFLUX/ATFLUX keff inconsistency!\n\t"
                f"{self.r.core.p.keff} vs. {fluxData.metadata['EFFK']}"
            )


class Dif3dStdoutReader:
    """
    A reader that goes through a DIF3D stdout file.

    While it's preferable to use binary interface files for several reasons
    (higher precision, more explicit structure, faster, etc.), some information
    is not readily available in them (like peak flux). This is used
    for things that are only available in the text
    """

    def __init__(self, fname: str):
        self.fname = fname

    def readRegionTotals(self):
        """Read the region totals."""
        endMark = "0" + 40 * " " + "REACTION INTEGRALS IN DIRECTION OF CALCULATION"
        with open(self.fname) as f:
            for line in f:
                if (
                    line
                    == "0                                                       REGION TOTALS\n"
                ):
                    break
            activeRegionLabels = None
            peakFluxesByRegion = {}
            for line in f:
                if line.startswith("     REGION"):
                    activeRegionLabels = self._getRegionLabels(line)
                elif line.startswith(" PEAK FLUX"):
                    # start at item 2 since PEAK and FLUX will be the first two
                    for reg, val in zip(activeRegionLabels, line.split()[2:]):
                        peakFluxesByRegion[reg] = float(val)
                elif line.startswith(endMark):
                    break
        return peakFluxesByRegion

    @staticmethod
    def _getRegionLabels(line):
        """
        Get a list of region names from a REGION TOTALS line.

        ..warning:: If there are more than 10,000 regions in a case the space separating
        the region name and ID will be consumed!
            Like this:
            ```
                 REGION    10009  A9017710010  A9017810011  A9016A10012  A9016B10013  A9016C10014  A9016D10015  A9016E10016  A9016F10017  A9016G
            ```

        We chop off the first 15 chars and then expect space-delimited pairs of zone num/region num
        in fixed-length 13-wide windows.

        """
        regionLabels = []
        data = line[15:].strip()  # remove trailing newline
        for i in range(0, len(data), 13):
            # discard the zone numbers
            regionLabels.append(data[i : i + 13].split()[1])

        return regionLabels
