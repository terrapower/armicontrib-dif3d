.. _design-requirements:

Requirements
============

This page shows the software requirements of the DIF3D-ARMI plugin. Demonstration that
the below requirements are satisfied by the implementation is presented in
:ref:`testing`.

Summary
-------

.. needtable::
   :style: table
   :columns: id;title

Details
-------

.. req:: Write valid DIF3D input files based on ARMI state
    :id: R-write-input

    The code shall produce DIF3D 11.0 input files derived entirely from state
    information stored on the ARMI reactor model.  This ensures that the DIF3D runs
    can be coupled with anything else that is represented in ARMI.

    **Verification Method**: VTR-like ARMI inputs will be loaded in ARMI and passed to this plugin to generate inputs.
    Verification requires that DIF3D can execute the inputs without error.


.. req:: Support 3-D hexagonal geometry in 1/3 or full core symmetry
    :id: R-geom-types

    The code shall support both 1/3 symmetric and full core hex geometry models.
    While DIF3D does support other geometry options, this plugin does not need to
    support them, but it could be designed in such a way to allow later extension
    to other geometries.

    Test cases in the required geometries will be built and included.

.. req:: Support nodal and finite-difference spatial approximations
    :id: R-spatial-approx

    Both nodal and finite difference modes of DIF3D shall be selectable by user
    input.

    .. note:: The VARIANT options shall not be precluded by design, but are not
        necessary for the initial implementation.

    **Verification Method**
    Test cases in the required modes will be built and included.

.. req:: Support real and adjoint calculations
    :id: R-solver-modes

    Real and adjoint calculations must be possible with the system. 

    .. warning:: DIF3D nodal mode does not work in adjoint unless certain acceleration
        options are disabled

    **Verification Method**
    Test cases in the required modes will be built and included.
    


.. req:: Execute a given DIF3D executable
    :id: R-execute
    
    To support workflow automation, the code must be able to execute DIF3D given an
    ARMI-derived input and save the output files.

    .. note:: Temporary scratch files generated during a run may be discarded

    **Verification Method**

    An integration test script that includes DIF3D execution will be built and included.


.. req:: Read DIF3D output information back onto the ARMI state
    :id: R-read-output

    Given a successful DIF3D execution from this plugin, the plugin shall parse
    DIF3D output files and load the state information back onto the ARMI model,
    including:

    * k-effective
    * Multigroup and scalar real and/or adjoint flux
    * Power distribution in Watts
    * Power density in Watts/cc

    **Verification Method**

    Known information from a test output file will be loaded into ARMI and verified 
    to match with unit tests.

