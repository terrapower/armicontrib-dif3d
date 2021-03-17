.. _testing:

Test Report
===========
This section presents the verification of the
requirements described in :ref:`design-requirements`.

A test suite is generated based on a small SFR-like reactor model included in the ARMI
framework. The ``make-fixture-suite`` entry point to the ``dif3ddemo`` application
starts from that basis and builds a matrix of cases by modifying the relevant user
settings to cover all required features. Cases included in the matrix include:

.. list-table:: Test Matrix
   :header-rows: 1
   :stub-columns: 1

   * -
     - Real
     - Adjoint
     - Real and Adjoint
   * - Nodal
     - 1/3, Full Core
     - 1/3
     - 1/3
   * - Finite Difference
     - 1/3
     - 1/3
     - 1/3
   * - VARIANT P1P0
     - 1/3
     - 1/3
     - 1/3
   * - VARIANT P3P1
     - 1/3
     -
     -

The keffs from the successful execution of this case suite are as follows

.. code-block:: none

    Keff summary for all runs
                                real                adjoint             both
    --------------------------  ------------------  ------------------  ------------------
    DIF3D-FD-third periodic     1.0194843576319725  1.0194843483645764  1.0194843484808453
    DIF3D-Nodal-full            1.008301720451915   -                   -
    DIF3D-Nodal-third periodic  1.0083017198449564  1.0082980021162906  1.008298002103253
    VARIANTP1P0-third periodic  1.0046225859303046  1.0046350449098904  1.0046350449101311
    VARIANTP3P1-third periodic  1.0114942706448846  -                   -

This test suite will be referred to in the verification of several requirements below.

Input
-----
**Requirement:** :need:`R-write-input`

**Verification**:

The unit test :py:meth:`~armicontrib.dif3d.tests.test_dif3dInputWriter.TestInputWriter.testWriteInput`
writes an input from a sample case and compares it line-for-line with an included reference
input that has been determined to be valid.

Geometry
--------
**Requirement:** :need:`R-geom-types`

**Verification**:

This requirement is verified by running the ``make-fixture-suite`` entry point.

Spatial Approximation
---------------------
**Requirement:** :need:`R-spatial-approx`

**Verification**:

This requirement is verified by running the ``make-fixture-suite`` entry point.

Solver Modes
------------
**Requirement:** :need:`R-solver-modes`

**Verification**:

This requirement is verified by running the ``make-fixture-suite`` entry point.

Execution
---------
**Requirement:** :need:`R-execute`

**Verification**:

This requirement is verified by running the ``make-fixture-suite`` entry point.

Output
------

**Requirement:** :need:`R-read-output`

**Verification**:

Keff
^^^^
The output file lists

.. code-block:: none

    0          OUTER ITERATIONS COMPLETED AT ITERATION  19, ITERATIONS HAVE CONVERGED
    0          K-EFFECTIVE =   1.00830171984

The unit test :py:meth:`~armicontrib.dif3d.tests.test_dif3dOutputReader.TestOutputReader.test_readKeff`
confirms this.

Total and Peak Flux
^^^^^^^^^^^^^^^^^^^

Table says::

         REGION     ZONE  ZONE          VOLUME          TOTAL FLUX     PEAK FLUX (1)   TOTAL FAST FLUX PEAK FAST FLUX(1)
        NO.  NAME    NO.  NAME           (CC)       (NEUTRON-CM/SEC) (NEUTRON/CM2-SEC)(NEUTRON-CM/SEC) (NEUTRON/CM2-SEC)
        ...
        135  A3002E  135  Y0102E      1.82231E+04      3.05696E+18      3.81625E+14      1.55710E+18      2.45365E+14

The unit test
:py:meth:`~armicontrib.dif3d.tests.test_dif3dOutputReader.TestOutputReader.test_readTotalFlux`
confirms the total flux is read correctly into ``b.p.flux``. The
:py:meth:`~armicontrib.dif3d.tests.test_dif3dOutputReader.TestOutputReader.test_readPeakFlux`
confirms that the peak is read correctly.

Multigroup Flux
^^^^^^^^^^^^^^^

Multigroup printouts include

.. code-block:: none

    1DIF3D   11.0    01/01/12         dif3d-R-armiRun-0000-0-0                                                                PAGE 302
    0        REGION AND AREA REAL FLUX INTEGRALS FOR K-EFF  PROBLEM WITH ENERGY RANGE (EV)     =(1.100E-04,1.964E+07)
    0
     REGION     ZONE  ZONE           GROUP            GROUP            GROUP            GROUP            GROUP            GROUP
    NO.  NAME    NO.  NAME             1                2                3                4                5                6
    ...
    135  A3002E  135  Y0102E      1.47312E+14      2.30742E+15      1.53930E+16      2.54007E+16      6.25577E+16      1.44366E+17

     REGION     ZONE  ZONE           GROUP            GROUP            GROUP            GROUP            GROUP            GROUP
    NO.  NAME    NO.  NAME             7                8                9               10               11               12
    ...
    135  A3002E  135  Y0102E      1.97879E+17      4.38889E+17      3.41350E+17      3.64783E+17      2.39746E+17      2.56849E+17

     REGION     ZONE  ZONE           GROUP            GROUP            GROUP            GROUP            GROUP            GROUP
    NO.  NAME    NO.  NAME            13               14               15               16               17               18
    ...
    135  A3002E  135  Y0102E      2.73795E+17      1.71025E+17      1.11952E+17      8.32989E+16      3.26362E+16      2.98441E+16

     REGION     ZONE  ZONE           GROUP            GROUP            GROUP            GROUP            GROUP            GROUP
    NO.  NAME    NO.  NAME            19               20               21               22               23               24
    ...
    135  A3002E  135  Y0102E      7.66527E+16      5.52959E+16      5.77510E+16      3.08758E+16      1.98528E+16      1.15805E+16

     REGION     ZONE  ZONE           GROUP            GROUP            GROUP            GROUP            GROUP            GROUP
    NO.  NAME    NO.  NAME            25               26               27               28               29               30
    ...
    135  A3002E  135  Y0102E      5.43152E+15      3.75557E+15      1.38772E+15      6.75732E+14      9.02733E+14      2.31725E+14

     REGION     ZONE  ZONE           GROUP            GROUP            GROUP
    NO.  NAME    NO.  NAME            31               32               33
    ...
    135  A3002E  135  Y0102E      3.40262E+14      3.05077E+12      3.51154E+12

These flux values are verified in
:py:meth:`~armicontrib.dif3d.tests.test_dif3dOutputReader.TestOutputReader.test_readMGFlux`

Power
^^^^^
Region totals table shows

.. code-block:: none

    0                                                       REGION TOTALS

         REGION      127  A2002B  128  A2002C  129  A2002D  130  A2002E  131  A3002A  132  A3002B  133  A3002C  134  A3002D  135  A3002E
     REGION ID          CORE         CORE         CORE                                   CORE         CORE         CORE
     VOLUME(LITERS)  6.07436E+00  6.07436E+00  6.07436E+00  1.82231E+01  6.07436E+00  6.07436E+00  6.07436E+00  6.07436E+00  1.82231E+01
     POWER(WATTS)    4.05141E+05  5.85634E+05  4.26733E+05  0.00000E+00  0.00000E+00  6.77304E+05  9.94134E+05  7.34698E+05  0.00000E+00
     FISS. SOURCE/K  3.13266E+16  4.53250E+16  3.29891E+16  0.00000E+00  0.00000E+00  5.22692E+16  7.67903E+16  5.67014E+16  0.00000E+00
     CONVERSN RATIO  8.04092E-01  7.99336E-01  8.04290E-01  0.00000E+00  0.00000E+00  3.84466E-01  3.81377E-01  3.84341E-01  0.00000E+00
     BREEDING RATIO  9.64224E-03  1.37430E-02  1.01820E-02  0.00000E+00  0.00000E+00  8.08373E-03  1.16904E-02  8.76783E-03  0.00000E+00
     FISS MASS(KG)   4.34924E+00  4.34924E+00  4.34924E+00  0.00000E+00  0.00000E+00  7.69059E+00  7.69059E+00  7.90770E+00  0.00000E+00
     HVY METAL(KG)   3.95385E+01  3.95385E+01  3.95385E+01  0.00000E+00  0.00000E+00  3.84530E+01  3.84530E+01  3.95385E+01  0.00000E+00
     ENRICHMENT, %   1.10000E+01  1.10000E+01  1.10000E+01  0.00000E+00  0.00000E+00  2.00000E+01  2.00000E+01  2.00000E+01  0.00000E+00
     PEAK FISS DENS  2.06761E+12  2.98874E+12  2.17780E+12  0.00000E+00  0.00000E+00  3.45657E+12  5.07349E+12  3.74947E+12  0.00000E+00
     AVE FISS DENS   2.06761E+12  2.98874E+12  2.17780E+12  0.00000E+00  0.00000E+00  3.45657E+12  5.07349E+12  3.74947E+12  0.00000E+00
     PEAK POWER DEN  9.49624E+01  1.04466E+02  9.74648E+01  0.00000E+00  0.00000E+00  1.60242E+02  1.76085E+02  1.69977E+02  0.00000E+00
     AVE POWER DEN   6.66970E+01  9.64108E+01  7.02515E+01  0.00000E+00  0.00000E+00  1.11502E+02  1.63661E+02  1.20951E+02  0.00000E+00
     PEAK/AVE POWER  1.42379E+00  1.08355E+00  1.38737E+00  0.00000E+00  0.00000E+00  1.43712E+00  1.07591E+00  1.40535E+00  0.00000E+00
     CAP POWER FRAC  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
     PEAK FLUX       8.73006E+14  9.62471E+14  8.94007E+14  3.88734E+14  3.43874E+14  9.15807E+14  1.00985E+15  9.42752E+14  3.81625E+14
     FLUX VOLUME     3.74077E+18  5.45884E+18  3.92061E+18  3.22998E+18  1.16187E+18  3.87403E+18  5.73850E+18  4.07078E+18  3.05696E+18
     %FLUX>100 KEV   7.05877E+01  7.14295E+01  7.02912E+01  5.06302E+01  6.18791E+01  7.43978E+01  7.52939E+01  7.42421E+01  5.09362E+01
    0FISSILE ABS     2.61865E+16  3.75530E+16  2.76310E+16  9.42250E+14  2.30504E+14  3.46970E+16  5.06005E+16  3.75991E+16  8.92606E+14
     FISSILE SOURCE  3.15867E+16  4.57013E+16  3.32630E+16  0.00000E+00  0.00000E+00  5.27032E+16  7.74278E+16  5.71721E+16  0.00000E+00
     FERTILE BONUS   0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
     PARASITIC ABS   0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
        STRUCTURE    0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
        FISS. PROD.  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
        COOLANT      0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00
        OTHER        0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00  0.00000E+00

The peak and average power values are verified in
:py:meth:`~armicontrib.dif3d.tests.test_dif3dOutputReader.TestOutputReader.test_power`


