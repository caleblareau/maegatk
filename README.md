# maegatk | Mitochondrial Alteration Enrichment and Genome Analysis Toolkit

[![PyPI version](https://badge.fury.io/py/maegatk.svg)](https://pypi.python.org/pypi/mgaeatk)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/maegatk/month)](https://pepy.tech/project/maegatk)

[Source code is made freely available](http://github.com/caleblareau/maegatk)
and a packaged install version is provided through [PyPi](https://pypi.python.org/pypi/maegatk/).
<br>

## About
This repository houses the **maegatk** package, a python-based command line interface for processing `.bam` files with mitochondrial reads and generating high-quality heteroplasmy estimation from sequencing data. This package places a special emphasis on [MAESTER](https://www.biorxiv.org/content/10.1101/2021.03.08.434450v1) data but is applicable to any UMI-based scRNA-seq dataset. **The key feature present in this package is the consensus base inference by collapsing reads with identical insert positions and UMIs**. This allows `maegatk` to produce robust, error corrected genotype calls in single cells. 
<br>

## Install maegatk

**Recommended:**
First, create a `python` virtual environment in some working directory to keep things tidy:

```
python3 -m venv venv3
source venv3/bin/activate
```

Next, install `maegatk` from [PyPi](https://pypi.org/project/maegatk/):

```
pip3 install maegatk
```

This should be all that you need. To verify: 

```
maegatk --version
```

Available options:
<pre>
  maegatk --help
Usage: maegatk [OPTIONS] [bcall|support]

  maegatk: a Maester genome toolkit.

  MODE = ['bcall', 'support']

Options:
  --version                       Show the version and exit.
  -i, --input TEXT                Input; a singular, indexed bam file.
                                  [required]

  -o, --output TEXT               Output directory for genotypes.
  -n, --name TEXT                 Prefix for project name
  -g, --mito-genome TEXT          mitochondrial genome configuration. Requires
                                  bwa indexed fasta file or `rCRS` (built-in)
                                  [required]

  -c, --ncores TEXT               Number of cores to run the main job in
                                  parallel.

  --cluster TEXT                  Message to send to Snakemake to execute jobs
                                  on cluster interface; see documentation.

  --jobs TEXT                     Max number of jobs to be running
                                  concurrently on the cluster interface.

  -bt, --barcode-tag TEXT         Read tag (generally two letters) to separate
                                  single cells; valid and required only in
                                  `bcall` mode.

  -b, --barcodes TEXT             File path to barcodes that will be
                                  extracted; useful only in `bcall` mode.

  -mb, --min-barcode-reads INTEGER
                                  Minimum number of mitochondrial reads for a
                                  barcode to be genotyped; useful only in
                                  `bcall` mode; will not overwrite the
                                  `--barcodes` logic.

  --NHmax INTEGER                 Maximum number of read alignments allowed as
                                  governed by the NH flag. Default = 2.

  --NMmax INTEGER                 Maximum number of paired mismatches allowed
                                  represented by the NM/nM tags. Default = 15.

  -mr, --min-reads INTEGER        Minimum number of supporting reads to call a
                                  consensus UMI/rread. Default = 1.

  -ub, --umi-barcode TEXT         Read tag (generally two letters) to specify
                                  the UMI tag when removing duplicates for
                                  genotyping.

  -jm, --max-javamem TEXT         Maximum memory for java for running
                                  duplicate removal. Default = 4000m.

  -q, --base-qual INTEGER         Minimum base quality for inclusion in the
                                  genotype count. Default = 0.

  -aq, --alignment-quality INTEGER
                                  Minimum alignment quality to include read in
                                  genotype. Default = 0.

  -ns, --nsamples INTEGER         The number of samples / cells to be
                                  processed per iteration; default is all.

  -k, --keep-samples TEXT         Comma separated list of sample names to
                                  keep; ALL (special string) by default.
                                  Sample refers to basename of .bam file

  -x, --ignore-samples TEXT       Comma separated list of sample names to
                                  ignore; NONE (special string) by default.
                                  Sample refers to basename of .bam file

  -z, --keep-temp-files           Keep all intermediate files.
  -sr, --skip-R                   Generate plain-text only output. Otherwise,
                                  this generates a .rds obejct that can be
                                  immediately read into R for downstream
                                  analysis.

  -so, --snake-stdout             Write snakemake log to sdout rather than a
                                  file.

  --help                          Show this message and exit.
</pre>

### Dependencies
`java`, `bwa` (tested with v0.7.17-r1188), `samtools` (tested with v1.15.1), `freebayes` (for indel calling), `R` should be available in the environment.
`dplyr`, `data.table`, `Matrix`, `GenomicRanges`, and `SummarizedExperiment` packages should be installed in R. **Note**: if you specify the flag `--skip-R`, you can avoid the internal R execution but will have plain text enumerations of the mitochondrial genetic data.

### fgbio
We use [fgbio](https://github.com/fulcrumgenomics/fgbio) for PCR duplicate removal. Thus, `java` is by default a required dependency. While not recommended, you can avoid this dependency by throwing the `--keep-duplicates` flag, which will circumvent the `java` call (but retain likely PCR duplicates, which we've found decreases the interpretability of variants by introducing additional false positives). If you retain duplicates, then maegatk isn't doing anything for you, and you should consider running [mgatk](https://github.com/caleblareau/mgatk).

We recommend specifying a custom tmp directory for **fgbio**, as the default directory can easily get overflown on your system. This can be done by modifying the **fgbio** command in [maegatk/bin/python/oneSample_maegatk.py](https://github.com/caleblareau/maegatk/blob/master/maegatk/bin/python/oneSample_maegatk.py) (located in `~/.local/lib/python3.9/site-packages/maegatk/bin/python/`) by adding the `-Djava.io.tmpdir` option:
<pre> fgbio = java + " -Djava.io.tmpdir=/some/directory/"  + " -Xmx" + max_javamem + " -jar " + script_dir + "/bin/fgbio.jar" </pre>

## Test run
<pre>maegatk bcall -i tests/data/test_maester.bam -o tests/test_maester -z</pre>

## Output files
The ultimate result of **maegatk** is an `.rds` file in `final/` which represents a SingleCellExperiment object with multiple assays, containing information on the support of every possible single-nucleotide variant at every possible genome position. The same information is contained in the five 'txt.gz' files in `final`, which are the final output files if `--skip-R` is used.

The entire pipeline is coordinated in [maegatk/cli.py](https://github.com/caleblareau/maegatk/blob/master/maegatk/cli.py). The input BAM file is first split into smaller .bam files corresponding to individual cell barcodes in `temp/barcoded_bams/`. The first snakemake file, [Snakefile.maegatk.Scatter](https://github.com/caleblareau/maegatk/blob/master/maegatk/bin/snake/Snakefile.maegatk.Scatter), is then executed for each cell independently; it runs `oneSample_maegatk.py` and creates a series of files per cell barcode in `temp/temp_bam/`, `temp/ready_bam/` and `temp/sparse_matrices`. Once all the cell barcodes have been processed, the second snakemake file, [Snakefile.maegatk.Gather](https://github.com/caleblareau/maegatk/blob/master/maegatk/bin/snake/Snakefile.maegatk.Gather), combines `temp/sparse_matrices` results into five `.txt.gz` files in `final`. Finally, [toRDS.R](https://github.com/caleblareau/maegatk/blob/master/maegatk/bin/R/toRDS.R) creates a SingleCellExperiment object out of `.txt.gz` files.

An error at any stage of the pipeline will result in a generic R error. It is recommended to keep intermediate files with option `-z` and explore snakemake logs in `logs/` and intermediate files in `temp_bam,ready_bam,sparse_matrices` to troubleshoot the case of error.

## BAM file preparation
Input `.bam` files should be modified to contain extra tags corresponding to cell barcode and UMI (see [test_maester.bam](https://github.com/caleblareau/maegatk/blob/master/tests/data/test_maester.bam)). If non-standard, these tags should be specified to `maegatk` through `-bt` and `-ub` options. 

## Should I use maegatk or mgatk? 
We previously developed the [mgatk package](https://github.com/caleblareau/mgatk) for genotyping single-cell datasets. The key feature distinctly present in `maegatk` is the consensus collapsing of sequencing reads using [fgbio's CallMolecularConsensusRead](http://fulcrumgenomics.github.io/fgbio/tools/latest/CallMolecularConsensusReads.html). Thus, if you have multiple PCR duplicates per unique molecule (defined by position x UMI x cell), maegatk provides a unique processing workflow to determine the molecular consensus of bases across these duplicate sequencing reads. In contrast, `mgatk` utilizing [picard's MarkDuplicates](https://gatk.broadinstitute.org/hc/en-us/articles/360037052812-MarkDuplicates-Picard-), which selects the singular read with the best mean base quality, which may be suboptimal particularly with deep-sequencing data. Otherwise, the tools produce virtually identical results. One note: `mgatk` has a optimized workflow for large (>10,000 cells) datasets in the `tenx` mode. If you have exceptionally large datasets, mgatk may be the better tool for computational feasibility out-of-the-box. Otherwise, consider just pre-splitting your `.bam` file into smaller pieces. 

## Indel calling
### Step 1 - normal maegatk execution
After successfully running `maegatk` with the `-qc` flag, all quality-controlled per-cell bam files will be retained in the output folder. 

### Step 2 - indel calling
`maegatk-indel` can be called on the folder containing all per-cell bam files to call indels for each cell. Under the hood, `maegatk-indel` calls [freebayes](https://github.com/freebayes/freebayes) on each bam file to generate a vcf file. It then collects indel information from all per-cell vcf files and merges them into the final `indel_summary.csv` file in the user-specified output directory. User can run `maegatk-indel` with `-k` flag to keep the intermediate vcf files, which by default will be removed after execution. The `-m` option specifies minimal number of reads in each cell required to support an indel, which by default is 5 and passed to freebayes.

### Step 3 - output interpretation
In the output `indel_summary.csv` file, each row corresponds to a cell/indel combination and contains information specific to that combination. The quality score comes from freebayes.

## Interpreting variants
maegatk provides matrices of mtDNA variant counts from which the user can select informative variants to reconstruct cellular relationships. The functional impact of mtDNA variants that are selected for further analysis can be assessed using predictions and annotations: amino acid changes (if any), which features these changes affect, predicted consequences (with SIFT and PolyPhen scores), associated diseases, and the frequency of these variants in the general population. This information can simply be determined from subsetting `rev_table.txt` for [the selected variants](https://github.com/EDePasquale/Mitochondrial_variants). Thoughtful interpretation of variants that are used to establish clonal relationships requires assessment of variant frequencies and their potential impact on fitness of the host cell.

## Contact
Raise an issue on the repository with any issues getting this toolkit working. 
<br><br>


