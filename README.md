# maegatk | Mitochondrial Alteration Enrichment and Genome Analysis Toolkit

[![PyPI version](https://badge.fury.io/py/maegatk.svg)](https://pypi.python.org/pypi/mgaeatk)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/maegatk/month)](https://pepy.tech/project/maegatk)


[Source code is made freely available](http://github.com/caleblareau/maegatk)
and a packaged install version is provided through [PyPi](https://pypi.python.org/pypi/maegatk/).
<br>

## About
This repository houses the **maegatk** package, a python-based command line interface for
processing `.bam` files with mitochondrial reads and generating high-quality heteroplasmy 
estimation from sequencing data. This package places a special emphasis on
[MAESTER](https://www.biorxiv.org/content/10.1101/2021.03.08.434450v1) data but is applicable
to any UMI-based scRNA-seq dataset. **The key feature present in this package is the consensus base
inferene by collapsing reads with identical insert positions and UMIs**. This allows `maegatk` to 
produce robust, error corrected genotype calls in single cells. 
<br>

Check out the [**mgatk** documentation](https://github.com/caleblareau/maegatk/wiki) for more 
information and user guides. 

### Installation

With python3, simply install via `pip`

```
pip3 install maegatk
```

### Contact

Raise an issue on the repository with any issues getting this toolkit working. 
<br><br>


