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

"""App for testing the DIF3D plugin."""
import armi
from armi import plugins


class Dif3dTestingApp(armi.apps.App):
    """App that adds only the DIF3D plugin for testing purposes."""

    name = "DIF3D Test App"

    def __init__(self):

        armi.apps.App.__init__(self)

        # Only registering DIF3D, main purpose is for testing.
        from armicontrib.dif3d.plugin import Dif3dPlugin

        self._pm.register(Dif3dPlugin)

    @property
    def splashText(self):
        return """
     ================================
     == DIF3D Testing Application ==
     ================================
"""
