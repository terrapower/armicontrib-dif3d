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
PKEDIT is a file made by DIF3D with peak power distribution information in it.

It is an undocumented(?) format as far as we can tell, but the format can
be understood from the source code that writes it in ```/src_DIF3D/lib/wpkedt.f``.
"""
import numpy as np

from armi.nuclearDataIO import cccc, nuclearFileMetadata

PKEDIT = "PKEDIT"

INT_CONTROL_2D_KEYS = (
    "NDIM",
    "NGROUP",
    "IM",
    "JM",
    "KM",
    "NOUTIT",
    "XKEFF",
    "POWIN",
    "NJBLOK",
)


class PkeditData(cccc.DataContainer):
    """
    Data representation that can be read from or written to a PKEDIT file.
    """

    def __init__(self):
        cccc.DataContainer.__init__(self)

        self.intControls = nuclearFileMetadata._Metadata()
        self.peakPowerDensity = np.array([])


class PkeditStream(cccc.StreamWithDataContainer):
    """
    Stream for reading to/writing from with PKEDIT data.

    Parameters
    ----------
    data : PkeditData
        Data structure
    fileName: str
        path to PKEDIT file
    fileMode: str
        string indicating if ``fileName`` is being read or written, and
        in ascii or binary format

    """

    @staticmethod
    def _getDataContainer() -> PkeditData:
        return PkeditData()

    def readWrite(self):
        """
        Step through the structure of the file and read/write it.
        """
        self._rwFileID()
        self._rw2DRecord()
        self._rw3DRecord()

    def _rwFileID(self):
        """
        Read/write file id record.

        Notes
        -----
        The username, version, etc are embedded in this string but it's
        usually blank. The number 28 was actually obtained from
        a hex editor and may be code specific.
        """
        with self.createRecord() as record:
            self._metadata["label"] = record.rwString(self._metadata["label"], 28)

    def _rw2DRecord(self):
        """
        Read/write int controls on 2D record.
        """
        with self.createRecord() as record:
            for key in INT_CONTROL_2D_KEYS:
                self._metadata[key] = record.rwInt(self._metadata[key])

    def _rw3DRecord(self):
        """
        Read/write blocks of data from 3D with peaking info.

        By inspection we see these values are double precision.
        """
        imax = self._metadata["IM"]
        jmax = self._metadata["JM"]
        kmax = self._metadata["KM"]
        nblck = self._metadata["NJBLOK"]
        if self._data.peakPowerDensity.size == 0:
            # initialize all-zeros here before reading now that we
            # have the matrix dimension metadata available.
            self._data.peakPowerDensity = np.zeros(
                (imax, jmax, kmax),
                dtype=np.float64,
            )
        for ki in range(kmax):
            for bi in range(nblck):
                jL, jU = cccc.getBlockBandwidth(bi + 1, jmax, nblck)
                with self.createRecord() as record:
                    self._data.peakPowerDensity[
                        :, jL : jU + 1, ki
                    ] = record.rwDoubleMatrix(
                        self._data.peakPowerDensity[:, jL : jU + 1, ki],
                        jU - jL + 1,
                        imax,
                    )
