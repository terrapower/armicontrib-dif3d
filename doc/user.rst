User Guide
==========

This section describes the installation and use of the DIF3D ARMI plugin and its demo
application.

Installation
------------

Installation of ARMI plugins involves configuring the plugin package and its dependencies
to be importable from a Python environment. This often involves creating a Python virtual
environment and installing the package using the ``pip`` Python package manager, though
other options may be acceptable depending on the user's environment.  In this section, the
recommended installation instructions are provided.

Prerequisites
^^^^^^^^^^^^^
The DIF3D ARMI plugin depends on ARMI itself, and a collection of other publicly-available
Python packages. It is recommended to install all of these within a Python virtual
environment. The :doc:`ARMI Installation Documentation <armi:installation>` provides good
guidance on how to create a virtual environment and install ARMI into it.

In addition to the dependencies needed to make ARMI and the DIF3D plugin run, there are
some optional dependencies that are needed to run the tests and generate these
documents. These extra dependencies are expressed in the ``dev`` package extras, and can
be installed by appending ``[dev]`` to the ``pip`` install target. Examples of this are
shown below.

Installing the code
^^^^^^^^^^^^^^^^^^^
The plugin is written in pure Python and does not need to be compiled. Once the code
is extracted in a folder, there are several options for installing it. The easiest
way to do this is to install it in "editable" mode; run::

    > pip install -e .

to install it into your virtual environment. The ``-e`` flag tells ``pip`` to place a
link to the code in ``site-packages``, rather than copying the files themselves.
If it is desired to generate the documentation or run unit tests, the above can be
modified to install the extra dependencies::

    > pip install -e .[dev]

Alternatively, the code can be packaged and installed. One way to do this is to install
the ``wheel`` package, build a `wheel <https://wheel.readthedocs.io/en/stable/>`_, and
install that wheel into your environment. The following commands would accomplish this::

    > pip install wheel
    > python setup.py bdist_wheel
    > pip install dist/inl_dif3d-1.0-py3-none-any.whl

At this point it should be possible to import the DIF3D plugin modules, and to run the
main demonstration application, ``dif3ddemo``.

External physics codes
^^^^^^^^^^^^^^^^^^^^^^
In addition to the Python code that makes ARMI and the DIF3D plugin operate, the `Dragon
<https://www.polymtl.ca/merlin/version5.htm>`_ and `DIF3D
<https://www.ne.anl.gov/codes/dif3d/>`_ codes will need to be present on the system in
order to actually run them. Obtaining, compiling, and installing these is beyond
the scope of this document. Once installed, it is recommended that they be available via
the system ``PATH`` to avoid needing to define their precise locations through the
``dragonExePath`` and ``dif3dExePath`` settings.

.. note:: DRAGON is used in the demo application to generate multigroup cross sections.
    Other lattice physics codes may be used in its place if desired.


Running the test suite
----------------------

Unit tests
^^^^^^^^^^
The plugin comes with several self-contained unit tests. To run them, execute the
following in the root folder::

    > pytest

The tests themselves rely on a handful of `unit test fixtures`, which are essentially
binary and ASCII output files from DIF3D that the units tests operate upon. These are
committed to the source repository, and should already be present. In the event that
they need to be updated, this can be done by running the ``dif3ddemo`` application with
its ``make-fixture-suite`` and ``copy-fixture-files`` entry points. It is recommended to
do this somewhere outside of the main source tree::

    > dif3ddemo make-fixture-suite
        --dragonDataPath=/path/to/dragon/data/draglibendfb8r0SHEM361
        --dragonExePath=/path/to/dragon.exe
        --dif3dExePath=/path/to/dif3d.exe

.. tip:: On Windows you may have to eliminate or escape the line breaks to get that to
    execute.

From the same working directory that the test fixture cases were run above, they can be
copied to their appropriate location with::

    > dif3ddemo copy-fixture-files

This will divine the appropriate target location relative to the ``dif3ddemo``
application itself.


User settings
-------------

Many settings can be configured by the user at runtime and are accessible to developers
through the :py:class:`armi.settings.caseSettings.Settings` object, which is typically
stored in a variable named ``cs``. Interfaces have access to a simulation's settings
through ``self.cs``. :numref:`table-settings` lists all settings that are provided by the
DIF3D ARMI plugin. Additional settings, :doc:`defined by the ARMI Framework and its
built-in global-flux plugin <armi:user/inputs/settings_report>` also affect the behavior
of this plugin, as it implements the :py:class:`GlobalFluxInterface
<armi:armi.physics.neutronics.globalFlux.globalFluxInterface.GlobalFluxInterface>`
interface. Of these, the ``neutronicsKernel`` setting is the most important, as it must be
set to ``"DIF3D-Nodal"``, ``"DIF3D-FD"``, or ``"VARIANT"`` for the interface to be
activated.

.. exec::
    from armicontrib.dif3d.plugin import settings as d3dSettings
    from armi.settings import setting
    import textwrap

    subclassTables = {}
    settingsObjs = [so for so in d3dSettings.defineSettings() if isinstance(so, setting.Setting)]
    # User textwrap to split up long words that mess up the table.
    wrapper = textwrap.TextWrapper(width=35, subsequent_indent='')
    content = '\n.. _table-settings:\n.. list-table:: DIF3D Plugin Settings\n   :header-rows: 1\n   :class: longtable\n   :widths: 45 35 20\n    \n'
    content += '   * - Name\n     - Description\n     - Default\n'

    for setting in sorted(settingsObjs, key=lambda s: s.name):
        content += '   * - ``{}``\n'.format(' '.join(wrapper.wrap(setting.name)))
        content += '     - | {}\n'.format('\n       | '.join(wrapper.wrap(setting.description or '')))
        content += '     - {}\n'.format(' '.join(['``{}``'.format(wrapped) for wrapped in wrapper.wrap(str(getattr(setting,'default','') or ''))]))

    content += '\n'

    return content

Input Data
----------

State information required on the ARMI data model before this plugin can operate
includes the following:

* A ``Core`` system populated with `Blocks` that have number-density compositions
  (typically provided by user input and/or depletion modules). Any reactor model that is
  loaded from an ARMI Blueprints file will contain a ``.core`` member that functions in
  this capacity.
* A microscopic cross section library provided by the user or a lattice physics plugin,
  in ISOTXS format. In all of the examples presented, this was produced by the
  open-source ARMI `DRAGON plugin <https://github.com/terrapower/dragon-armi-plugin>`_,
  which is included in the ``dif3ddemo`` app. Running the ``dif3ddemo`` ``run`` entry
  point will lead to the creation of such an ISOTXS file before attempting to run DIF3D.

Output Data
-----------
The DIF3D plugin writes the DIF3D neutronics results to the ARMI data model on
the following Parameters.

Core parameters
^^^^^^^^^^^^^^^
A subset of the core parameters provided by the :ref:`generic neutronics plugin
<armi:neutronicsplugin-core-param-table>` are written by this plugin.
Specifically:

* ``keff``

Block parameters
^^^^^^^^^^^^^^^^
A subset of the block parameters provided by the :ref:`generic neutronics
plugin <armi:neutronicsplugin-block-param-table>` are written by this plugin.
Specifically:

* ``pdens``
* ``ppdens``
* ``power``
* ``flux``
* ``fluxPeak``
* ``mgFlux``
* ``fluxAdj``
* ``adjMgFlux``

In addition to the parameters supplied directly from the DIF3D output, several other
flux-derived parameters are also calculated when the DIF3D solution is mapped from the
DIF3D mesh back to the as-input ARMI mesh. Re-calculated values include:

* ``rateCap``
* ``rateFis``
* ``rateProdN2n``
* ``rateProdFis``
* ``rateAbs``

The exact behavior of the mapped and recalculated parameter values is governed by the
:py:func:`armi:armi.physics.neutronics.globalFlux.globalFluxInterface.calcReactionRates`
function and
:py:class:`armi:armi.reactor.converters.uniformMesh.NeutronicsUniformMeshConverter`
class. This behavior is demonstrated in :ref:`sec-results`.
