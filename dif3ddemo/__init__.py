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
The DIF3D Demonstration Application

This package contains the code that implements the DIF3D Demonstration Application,
``dif3ddemo``. The main ARMI-based application definition lives in
:py:class:`dif3ddemo.app.Dif3dDragonApp`, which registers the ``Dif3dPlugin`` and
``DragonPlugin`` ARMI plugins with the ARMI framework. With these plugins ``dif3ddemo
run [settings file]`` with perform simple neutronics analysis.

In addition, it includes the ``InlDif3dDemoPlugin`` plugin, which implements the
``make-test-fixtures`` and ``copy-fixture-files`` entry points, which are useful for
testing-related tasks.
"""
from .__main__ import main

from .app import Dif3dDragonApp
