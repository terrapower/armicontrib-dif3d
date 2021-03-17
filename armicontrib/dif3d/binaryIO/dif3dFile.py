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
Read/write the DIF3D binary interface file. 

This is a DIF3D-specific file with format defined in the DIF3D manual.

To be clear, this is a file called ``DIF3D`` that is made for/by the DIF3D
code. It is used as input to a DIF3D run and is modified during the run
to contain information about convergence, keff, dominance ratio, 
coarse-mesh rebalancing, optimum overrelaxation factors, etc.

Most things defined in the ``A.DIF3D`` input card end up in this file.
This file is required by DIF3D for initial runs and restarts.

This reads/writes version 10/31/00 (1.3) of the file from the REBUS manual
https://digital.library.unt.edu/ark:/67531/metadc735151/m1/141/

"""
from enum import Enum

from armi.nuclearDataIO import cccc, nuclearFileMetadata
from ..const import SolutionType, ProblemType

DIF3D = "DIF3D"

INT_CONTROL_2D_KEYS = (
    "IPROBT",
    "ISOLNT",
    "IXTRAP",
    "MINBSZ",
    "NOUTMX",
    "IRSTRT",
    "LIMTIM",
    "NUPMAX",
    "IOSAVE",
    "IOMEG",
    "INRMAX",
    "NUMORP",
    "IRETRN",
    "IEDF1",
    "IEDF2",
    "IEDF3",
    "IEDF4",
    "IEDF5",
    "IEDF6",
    "IEDF7",
    "IEDF8",
    "IEDF9",
    "IEDF10",
    "NOUTBQ",
    "IOFLUX",
    "NOEDIT",
    "NOD3ED",
    "ISRHED",
    "NSN",
    "NSWMAX",
    "NAPRX",
    "NAPRXZ",
    "NFMCMX",
    "NXYSWP",
    "NZSWP",
    "ISYMF",
    "NCMRZS",
    "ISEXTR",
    "NPNO",
    "NXTR",
    "IOMEG",
    "IFULL",
    "NVFLAG",
    "ISIMPL",
    "IWNHFL",
    "IPERT",
    "IHARM",
)

KEYS_3D_RECORD = (
    "EPS1",
    "EPS2",
    "EPS3",
    "EFFK",
    "FISMIN",
    "PSINRM",
    "POWIN",
    "SIGBAR",
    "EFFKQ",
    "EPSWP",
) + ("DUM",) * 20


class Convergence(Enum):
    """Convergence flags for DIF3D outers."""

    NO_ITERATIONS = 0
    CONVERGED = 1
    OUTERS_LIMIT_REACHED = 2
    TIME_LIMIT_REACHED = 3


class Dif3dData(cccc.DataContainer):
    """
    Data representation that can be read from or written to a DIF3D file.

    This exposes several useful items from the data structure as properties
    for convenience.
    """

    def __init__(self):
        cccc.DataContainer.__init__(self)

        self.intControls = nuclearFileMetadata._Metadata()
        self.keffData = nuclearFileMetadata._Metadata()

    def makeSummary(self):
        """Make a short summary of info contained in this file."""
        return [
            f"| keff= {self.keff}",
            f"| Dominance ratio= {self.keffData['SIGBAR']}",
            f"| Problem type= {self.problemType.name}",
            f"| Solution type= {self.solutionType.name}",
            f"| Restart= {self.intControls['IRSTRT']}",
            f"| Convergence= {self.convergence.name}",
        ]

    @property
    def problemType(self):
        return ProblemType(self.intControls["IPROBT"])

    @property
    def solutionType(self):
        """
        Get the read/adjoint solution type.

        .. warning:: If you run a DIF3D run in ``REAL_AND_ADJOINT``
            mode, the ``DIF3D`` file that remains just has the ``ADJOINT``
            flag.
        """
        return SolutionType(self.intControls["ISOLNT"])

    @property
    def convergence(self):
        return Convergence(self.intControls["IRETRN"])

    @property
    def keff(self):
        return self.keffData["EFFK"]


class Dif3dStream(cccc.StreamWithDataContainer):
    """
    Stream for reading to/writing from with DIF3D data.

    Parameters
    ----------
    data : Dif3dData
        Data structure
    fileName: str
        path to DIF3D file
    fileMode: str
        string indicating if ``fileName`` is being read or written, and
        in ascii or binary format

    """

    @staticmethod
    def _getDataContainer() -> Dif3dData:
        return Dif3dData()

    def readWrite(self):
        """
        Step through the structure of the file and read/write it.
        """
        self._rwFileID()
        self._rw1DRecord()
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

    def _rw1DRecord(self):
        """
        Discard the 1D record for now (will need if writing a complete file)
        """
        with self.createRecord() as record:
            for _data in range(25):
                record.rwInt(0)

    def _rw2DRecord(self):
        """
        Read/write int controls on 2D record.
        """
        with self.createRecord() as record:
            for key in INT_CONTROL_2D_KEYS:
                self._data.intControls[key] = record.rwInt(self._data.intControls[key])

    def _rw3DRecord(self):
        """
        Read/write data from the 3D record which contains keff and convergence criteria

        And dominance ratio
        """
        with self.createRecord() as record:
            for key in KEYS_3D_RECORD:
                self._data.keffData[key] = record.rwDouble(self._data.keffData[key])

    def _rw4DRecord(self):
        """Read/write the optimum overrelaxation factors"""
        raise NotImplementedError()

    def _rw5DRecord(self):
        """Read/write the axial coarse mesh rebalance boundaries."""
        raise NotImplementedError()
