Attribution
===========
This work was initially sponsored by Battelle Energy Alliance, LLC Under Amendment No 06
to Release No 01 Under Blanket Master Contract No. 00212114 with scope defined in
SOW-15678, effective 8/25/2020.

Executive Summary
=================

The ANL DIF3D global flux code [DIF3D]_ was integrated with TerraPower's ARMI\ :sup:`®`
open-source reactor analysis automation framework [ARMI]_ in a new software plugin
developed and delivered to Idaho National Laboratory (INL) for use in the Versatile Test
reactor (VTR) experimental program. The plugin represents an important step toward the
significant improvements in engineering efficiency and quality, as well as the
reductions in cascading risks, targeted by the overall INL digital engineering efforts.
This project extends the digital thread bidirectionally between a central reactor
analysis data model and sophisticated 3D neutronics analysis. This builds upon previous
work to integrate the [BISON]_ fuel performance code into the ARMI-based analysis
ecosystem.

The new ARMI-DIF3D plugin was verified to meet its defined requirements using the
included automated test suite, which uses a meaningful but small and fast-running sample
reactor model. In addition, the practical use case of the plugin was demonstrated
computing keff, reaction rates, flux distributions, and power distributions in a
full-core 3D model of the Fast Flux Test Facility (FFTF) as defined in an
internationally-recognized benchmark problem. A sample ARMI-based application is
included in this package. It can be executed using readily available dependencies, and
is intended to assist in adapting the code for VTR-specific analysis application.

In the previous BISON integration work, the ARMI application used to demonstrate the new
BISON coupling employed TerraPower's proprietary plugins for ANL's MC²-3 [MC2]_ and
DIF3D codes. In this work, a modernized DIF3D ARMI plugin was designed and implemented
to INL's specifications. Subsequently, this open-source release of the DIF3D plugin is
expected to enhance collaboration in the future.

Introduction
============

Objectives and Scope
--------------------

Progress in digital engineering is expected to bring schedule reductions, increases
in productivity, improved quality, and other cost avoidances realized in other
industries to the nuclear field. Digital connections of engineering information within
and across domains help move us towards these realizations.  For the VTR, this project
aimed to enable:

* Increased efficiency of the analysis of proposed experiments by seamlessly integrating
  past operational history and anticipated future operations into coupled physics
  analysis
* More detailed results while remaining usably fast
* Rapid response to unexpected programmatic or operational changes
* Crystallization of institutional knowledge related to analysis methodologies

In this work, a new ARMI integration to the ANL DIF3D neutron diffusion code was
developed to provide whole-core neutron flux and eigenvalue solutions to coupled
multi-physics ARMI calculations. Global flux calculations are critical for numerous
follow-on analyses, such as fuel performance, thermal-hydraulics, reactivity
coefficients, and transient analysis.  Pursuant to the scope of work defined in
SOW-15678, the DIF3D ARMI integration

* is capable of performing neutronics analysis of a VTR-like reactor;
* supports bidirectional connections between the ARMI data model and the DIF3D code,
  including:

  * preparation of DIF3D input files,
  * execution of the DIF3D code using those input files,
  * reading of key results from the DIF3D output files;
* supports hexagonal reactor geometries of 1/3- and full-core domains; and
* supports running DIF3D in nodal and finite-difference mode.

These requirements have been more formally distilled in :ref:`design-requirements`. In
addition to satisfying the defined requirements, the DIF3D plugin also supports the
VARIANT mode of DIF3D for capturing transport effects.

Beyond the development of the ARMI plugin itself, a simple ARMI-based application was
developed and applied to a VTR-like reactor model to demonstrate the DIF3D integration.
Analyses using this demonstration application can be found in :ref:`sec-results`.

Background
----------

TerraPower has invested heavily in automation of nuclear analysis for SFR systems since
2009. The [ARMI]_ system was created originally to design fuel management operations,
and evolved to facilitate nuclear calculations covering neutronics, thermal/hydraulics,
fuel performance, fuel mechanical, and safety analysis.

ARMI provides the hub-and-spoke architecture shown in :numref:`armifig`, where a central
representation of a reactor is held in an abstract data model.  Analysis routines are
developed that translate this data model into forms appropriate for individual physics
kernels. The analysis routines send ARMI-derived input to the physics kernels, run the
physics kernels, parse the output, and bring the desired information into the central
reactor model. With new physics data on the central model, the next physics kernel may
be executed.  For example, a neutronics calculation may provide a power distribution to
be used as input for a thermal/hydraulics calculation. The thermal/hydraulics
kernel computes temperatures, flow rates, and pressures which feed into both fuel
performance and core mechanical calculations.

ARMI provides a *reactor at your fingertips*, meaning that with a few lines of code, a
user can quickly view or manipulate the entire reactor model. The high-level nature of
the system has enabled reactor engineers at TerraPower to automate the entire analysis
process from adjusting the outer diameter of a pin to determining the impact of that
change on the peak cladding temperature in a series of design-basis transients.

.. figure:: https://terrapower.github.io/armi/_static/armiSchematicView.png
   :figclass: align-center
   :name: armifig

   A schematic representation of the ARMI data model.

In 2019, TerraPower released the ARMI framework (containing the central reactor model
and many associated functionalities) as an open source product on GitHub.  The intent is
to allow additional collaboration on analysis routines and physics kernels while
focusing efforts across institutions and companies on fewer data models in an attempt to
increase the overall efficiency and capabilities of the nuclear industry as a whole. For
example, if one FFTF benchmark model can be shared across institutions, that (largely
public) information does not have to be processed by many individuals. We as a community
can improve quality and rigor of our proprietary models by sharing information in a
platform like this.

.. [BISON] https://bison.inl.gov/
.. [DIF3D] https://www.ne.anl.gov/codes/dif3d/
.. [ARMI] https://terrapower.github.io/armi/
.. [MC2] https://www.ne.anl.gov/codes/mc2-2/
