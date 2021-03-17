Implementation and Developer Guide
==================================

This project contains two main parts: an :doc:`ARMI-based <armi:index>` plugin, and a
simple ARMI-based application for demonstration and testing purposes.

Fundamentally, the ARMI DIF3D plugin works by filling in a template DIF3D input
file with data collected off of an ARMI reactor model, running the input file
through DIF3D, parsing DIF3D binary interface output files (and textual output
in some cases), and mapping the data in the output files back onto the ARMI
reactor model. The plugin houses all of the components that make the ARMI-DIF3D
interface work, including:

 * User-facing settings to control the plugin's behavior
   (:py:mod:`armicontrib.dif3d.settings`)
 * Components for preparing DIF3D input files from the ARMI reactor model
   (:py:mod:`armicontrib.dif3d.inputWriters`)
 * Components for executing DIF3D upon the generated input file
   (:py:mod:`armicontrib.dif3d.executers`)
 * Components for reading DIF3D outputs and applying read data to the ARMI reactor model
   (:py:mod:`armicontrib.dif3d.outputReaders`)
 * An ARMI :py:class:`Interface <armi.interfaces.Interface>`, which can be used to integrate
   DIF3D global flux solutions into an ARMI run
   (:py:mod:`armicontrib.dif3d.schedulers`)

Each of these are described in more detail in the above linked pages. The rest of the
API documentation describing the classes and functions that make up the DIF3D plugin can
be found :py:mod:`here <armicontrib.dif3d>`.

The demonstration application serves as a minimum viable ARMI application for
demonstrating the functionality of the DIF3D integration. It activates both the DIF3D
plugin, and TerraPower's open-source
`DRAGON plugin <https://github.com/terrapower/dragon-armi-plugin>`_, which produces
microscopic cross sections, which are necessary inputs to a DIF3D run. This application
is applied to a practical case and discussed in more detail in :doc:`results`.

The process for integrating this plugin into a new ARMI-based application is covered in
more detail in the ARMI documentation; the :doc:`main ARMI documentation on making apps
<armi:developer/making_armi_based_apps>` covers many aspects of building ARMI apps, and
the :doc:`app tutorial <armi:tutorials/making_your_first_app>` walks through a specific
example of making one. Going through this tutorial in particular will make the process
of creating an app that uses this DIF3D plugin more clear. The ``dif3ddemo`` application
(implemented in :py:mod:`dif3ddemo.app`)
that comes with this distribution is a very good example of a basic ARMI-based
application that makes use of the DIF3D plugin to perform simple analysis.
