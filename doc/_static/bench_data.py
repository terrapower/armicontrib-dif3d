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
Published benchmark results for plotting in spectra.py

For the most part, these were just scraped straight out of the benchmark report:
https://digital.library.unt.edu/ark:/67531/metadc1013078/m2/1/high_res_d/983334.pdf

The only addition is that of the extra energy group bounds at the lower end to
give proper bins. We use this to help prune the ARMI energy domain to that in the
report, and to make the step plots look right. The spacing of the energy groups is
intentionally based on constant lethargy widths, so it's easy to whip up the N+1th group
bound.
"""

BENCH_MIDPLANE_FLUX = [
    2633000,
    2906000,
    3057000,
    3210000,
    3368000,
    3967000,
    4082000,
    3967000,
    4197000,
    4540000,
    4317000,
    4250000,
    4357000,
    4094000,
    4339000,
    4648000,
    4974000,
    5229000,
    5423000,
    5703000,
    6253000,
    6415000,
    6870000,
    7121000,
    7130000,
    7236000,
    7436000,
    7458000,
    7450000,
    6838000,
    6179000,
    5786000,
    5858000,
    6473000,
    6804000,
    7068000,
    7602000,
    8112000,
    8479000,
    8535000,
    8710000,
    8556000,
    8610000,
    8372000,
    6826000,
    8075000,
    8985000,
    8305000,
    7418000,
    7747000,
    7950000,
    8267000,
    8611000,
    8169000,
    7664000,
    7810000,
    9539000,
    10500000,
    9471000,
    8888000,
    7606000,
    6772000,
    6349000,
    6009000,
    6211000,
    6888000,
    7908000,
    7539000,
    7332000,
    7021000,
    6319000,
    6174000,
    6357000,
    5622000,
    4742000,
    4275000,
    4326000,
    5335000,
    5449000,
    4919000,
    4739000,
    4101000,
    3830000,
    3652000,
    3248000,
    2733000,
    2089000,
    2123000,
    3030000,
    4834000,
    5271000,
    4988000,
    4291000,
    3730000,
    3693000,
    3387000,
    3031000,
    2781000,
    2468000,
    2445000,
    2457000,
    2649000,
    2689000,
    2665000,
    2806000,
    2780000,
    2576000,
    2860000,
    3021000,
    2713000,
    2415000,
    2080000,
    1899000,
    1770000,
    1643000,
    1620000,
    1701000,
    1812000,
    1485000,
    1494000,
    1513000,
    1629000,
    1322000,
    1213000,
    1238000,
    1164000,
    1115000,
    1065000,
    873000,
    866100,
    853000,
    963400,
    889400,
    822300,
    640500,
    521200,
    424300,
    445500,
    481000,
    455000,
    419800,
    307800,
    446300,
    459600,
    437300,
    414200,
    375200,
    518000,
    460700,
    477600,
    546800,
    642500,
    646100,
]

BENCH_MIDPLANE_ENERGY = [
    1903.548,
    1812.903,
    1725.574,
    1644.356,
    1566.054,
    1491.48,
    1420.457,
    1352.816,
    1288.396,
    1227.044,
    1168.613,
    1112.965,
    1059.967,
    1009.492,
    961.421,
    915.639,
    872.037,
    830.512,
    790.964,
    753.299,
    717.427,
    683.264,
    650.728,
    619.741,
    590.229,
    562.123,
    535.355,
    509.862,
    485.583,
    462.46,
    440.438,
    419.465,
    399.49,
    380.467,
    362.349,
    345.095,
    328.662,
    313.011,
    298.106,
    283.91,
    270.391,
    257.515,
    245.252,
    233.574,
    222.451,
    211.858,
    201.77,
    192.162,
    183.011,
    174.296,
    165.996,
    158.092,
    150.564,
    143.394,
    136.566,
    130.063,
    123.869,
    117.971,
    112.353,
    107.003,
    101.907,
    97.055,
    92.433,
    88.031,
    83.84,
    79.847,
    76.045,
    72.424,
    68.975,
    65.69,
    62.562,
    59.583,
    55.746,
    54.044,
    51.47,
    49.019,
    46.685,
    44.462,
    42.345,
    40.328,
    38.408,
    36.579,
    34.837,
    33.178,
    31.598,
    30.094,
    28.661,
    27.296,
    25.996,
    24.758,
    23.579,
    22.456,
    21.387,
    20.368,
    19.399,
    18.475,
    17.696,
    16.757,
    15.959,
    15.199,
    14.476,
    13.786,
    13.13,
    12.504,
    11.909,
    11.342,
    10.802,
    10.287,
    9.793,
    9.331,
    8.887,
    8.464,
    8.061,
    7.677,
    7.311,
    6.963,
    6.631,
    6.316,
    6.015,
    5.728,
    5.456,
    5.196,
    4.948,
    4.713,
    4.488,
    4.275,
    4.071,
    3.877,
    3.693,
    3.517,
    3.349,
    3.19,
    3.038,
    2.893,
    2.755,
    2.624,
    2.499,
    2.38,
    2.267,
    2.159,
    2.056,
    1.958,
    1.865,
    1.776,
    1.692,
    1.611,
    1.534,
    1.461,
    1.392,
    1.325,
    1.262,
    1.202,
    1.145,
    1.090476369,
]

BENCH_LOWER_FLUX = [
    2.817000e05,
    3.041000e05,
    3.736000e05,
    5.023000e05,
    5.060000e05,
    5.681000e05,
    6.032000e05,
    6.292000e05,
    7.576000e05,
    8.470000e05,
    8.849000e05,
    9.742000e05,
    1.221000e06,
    1.172000e06,
    1.118000e06,
    1.329000e06,
    1.442000e06,
    1.489000e06,
    1.484000e06,
    1.568000e06,
    1.625000e06,
    1.689000e06,
    1.898000e06,
    2.085000e06,
    2.464000e06,
    2.665000e06,
    2.530000e06,
    2.851000e06,
    3.146000e06,
    3.278000e06,
    3.426000e06,
    3.728000e06,
    3.672000e06,
    3.632000e06,
    3.737000e06,
    4.035000e06,
    4.616000e06,
    5.081000e06,
    5.432000e06,
    5.971000e06,
    6.362000e06,
    6.671000e06,
    6.662000e06,
    6.826000e06,
    6.396000e06,
    6.791000e06,
    6.319000e06,
    6.662000e06,
    6.634000e06,
    6.902000e06,
    6.539000e06,
    6.375000e06,
    6.195000e06,
    6.459000e06,
    7.233000e06,
    7.569000e06,
    8.470000e06,
    1.087000e07,
    1.070000e07,
    9.248000e06,
    8.062000e06,
    7.187000e06,
    6.441000e06,
    6.785000e06,
    7.524000e06,
    8.112000e06,
    9.046000e06,
    8.809000e06,
    8.228000e06,
    8.127000e06,
    7.602000e06,
    7.551000e06,
    7.240000e06,
    6.278000e06,
    5.489000e06,
    5.980000e06,
    6.060000e06,
    6.550000e06,
    6.397000e06,
    6.042000e06,
    5.618000e06,
    4.827000e06,
    4.058000e06,
    3.477000e06,
    2.830000e06,
    2.671000e06,
    3.458000e06,
    4.903000e06,
    7.308000e06,
    8.503000e06,
    8.149000e06,
    7.628000e06,
    6.637000e06,
    5.971000e06,
    5.434000e06,
    5.244000e06,
    4.664000e06,
    3.972000e06,
    3.276000e06,
    3.636000e06,
    4.211000e06,
    4.094000e06,
    4.031000e06,
    3.802000e06,
    4.205000e06,
    4.129000e06,
    4.521000e06,
    4.583000e06,
    4.844000e06,
    4.443000e06,
    3.326000e06,
    3.199000e06,
    2.509000e06,
    2.321000e06,
    2.069000e06,
    1.936000e06,
    2.021000e06,
    2.169000e06,
    2.230000e06,
    1.878000e06,
    1.618000e06,
    1.249000e06,
    8.704000e05,
    8.323000e05,
    5.033000e05,
    3.011000e05,
    2.821000e05,
    4.739000e05,
    4.090000e05,
    4.035000e05,
    8.565000e05,
    1.015000e06,
    1.010000e06,
]

BENCH_LOWER_ENERGY = [
    1903.548,
    1812.903,
    1725.574,
    1644.356,
    1566.054,
    1491.48,
    1420.457,
    1352.816,
    1288.396,
    1227.044,
    1168.613,
    1112.965,
    1059.967,
    1009.492,
    961.421,
    915.639,
    872.037,
    830.512,
    790.964,
    753.299,
    717.427,
    683.264,
    650.728,
    619.741,
    590.229,
    562.123,
    535.355,
    509.862,
    485.583,
    462.46,
    440.438,
    419.465,
    399.49,
    380.467,
    362.349,
    345.095,
    328.662,
    313.011,
    296.106,
    283.91,
    270.391,
    257.515,
    245.252,
    233.574,
    222.451,
    211.858,
    201.77,
    192.162,
    183.011,
    174.296,
    165.996,
    158.092,
    150.564,
    143.394,
    136.566,
    130.063,
    123.869,
    117.971,
    112.353,
    107.003,
    101.907,
    97.055,
    92.433,
    88.031,
    83.84,
    79.847,
    76.045,
    72.424,
    68.975,
    65.69,
    62.562,
    59.583,
    56.746,
    54.044,
    51.47,
    49.019,
    46.685,
    44.462,
    42.345,
    40.328,
    38.408,
    36.579,
    34.837,
    33.178,
    31.598,
    30.094,
    28.661,
    27.296,
    25.996,
    24.758,
    23.579,
    22.456,
    21.387,
    20.368,
    19.399,
    18.475,
    17.595,
    16.757,
    15.959,
    15.199,
    14.476,
    13.786,
    13.13,
    12.504,
    11.909,
    11.342,
    10.802,
    10.287,
    9.798,
    9.331,
    8.887,
    8.464,
    8.061,
    7.677,
    7.311,
    6.963,
    6.631,
    6.316,
    6.015,
    5.728,
    5.456,
    5.196,
    4.948,
    4.713,
    4.488,
    4.275,
    4.071,
    3.877,
    3.693,
    3.517,
    3.349,
    3.19,
    3.038,
    2.893333909,
]

MCNP_MIDPLANE_FLUX = [
    1.656,
    1.737,
    1.869,
    1.947,
    1.964,
    1.951,
    1.945,
    1.907,
    1.766,
    1.653,
    1.453,
    1.241,
    1.003,
    0.778,
    0.554,
    0.382,
    0.24,
    0.156,
    0.126,
    0.153,
    0.227,
    0.344,
    0.487,
    0.636,
    0.805,
    0.943,
    1.07,
    1.21,
    1.336,
    1.44,
    1.569,
    1.666,
    1.722,
    1.818,
    1.887,
    1.943,
    1.974,
    1.899,
    1.817,
    1.737,
    1.794,
    2.001,
    2.283,
    2.587,
    2.803,
    2.957,
    3.04,
    3.03,
    2.882,
    2.874,
    3.019,
    3.126,
    2.894,
    2.633,
    2.811,
    3.24,
    3.649,
    4.025,
    4.239,
    4.382,
    4.717,
    5.034,
    5.556,
    5.715,
    4.48,
    2.768,
    2.516,
    3.186,
    3.969,
    4.414,
    4.666,
    4.967,
    5.218,
    5.496,
    5.798,
    6.171,
    5.687,
    4.396,
    3.591,
    4.476,
    5.801,
    6.172,
    6.033,
    6.118,
    6.476,
    6.393,
    6.862,
    7.003,
    6.452,
    6.598,
    6.425,
    6.271,
    6.665,
    7.207,
    7.738,
    8.172,
    8.632,
    8.8,
    7.771,
    6.829,
    7.436,
    7.958,
    8.355,
    8.661,
    7.651,
    6.411,
    6.402,
    6.753,
    6.753,
    6.625,
    7.389,
    8.57,
    8.569,
    8.36,
    8.17,
    7.43,
    7.064,
    6.933,
    6.17,
    5.403,
    5.103,
    5.356,
    6.271,
    7.436,
    8.227,
    8.249,
    7.658,
    7.178,
    6.708,
    6.087,
    5.502,
    4.965,
    4.621,
    4.499,
    4.324,
    4.189,
    3.831,
    3.511,
    3.361,
    3.341,
    3.497,
    3.714,
    3.691,
    3.434,
    3.318,
    3.254,
    3.192,
    3.031,
    2.906,
    2.792,
    2.644,
    2.572,
]
MCNP_MIDPLANE_FLUX.reverse()

MCNP_LOWER_FLUX = [
    0.224,
    0.338,
    0.483,
    0.632,
    0.776,
    0.915,
    1.046,
    1.178,
    1.31,
    1.411,
    1.535,
    1.61,
    1.658,
    1.746,
    1.843,
    1.892,
    1.936,
    1.879,
    1.743,
    1.709,
    1.792,
    1.966,
    2.245,
    2.565,
    2.797,
    2.949,
    2.986,
    2.931,
    2.84,
    2.847,
    3.007,
    3.065,
    2.815,
    2.591,
    2.74,
    3.185,
    3.599,
    3.939,
    4.172,
    4.374,
    4.622,
    4.944,
    5.5,
    5.658,
    4.43,
    2.767,
    2.492,
    3.182,
    3.89,
    4.333,
    4.592,
    4.915,
    5.194,
    5.407,
    5.762,
    6.082,
    5.664,
    4.343,
    3.546,
    4.411,
    5.672,
    6.127,
    5.928,
    6.112,
    6.457,
    6.344,
    6.809,
    6.996,
    6.382,
    6.475,
    6.393,
    6.243,
    6.636,
    7.108,
    7.682,
    8.083,
    8.512,
    8.8,
    7.66,
    6.785,
    7.287,
    7.907,
    8.259,
    8.507,
    7.619,
    6.353,
    6.365,
    6.685,
    6.567,
    6.488,
    7.355,
    8.484,
    8.392,
    8.152,
    8.129,
    7.39,
    7.045,
    6.854,
    6.195,
    5.346,
    5.055,
    5.256,
    6.22,
    7.406,
    8.17,
    8.201,
    7.597,
    7.083,
    6.58,
    6.083,
    5.525,
    4.939,
    4.582,
    4.535,
    4.376,
    4.213,
    3.866,
    3.579,
    3.337,
    3.362,
    3.546,
    3.765,
    3.779,
    3.506,
    3.321,
    3.319,
    3.191,
    3.061,
    2.932,
    2.794,
    2.704,
    2.578,
]
MCNP_LOWER_FLUX.reverse()
