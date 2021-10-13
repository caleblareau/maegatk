import click
import os
import os.path
import sys
import glob
import shutil
import random
import string
import itertools
import time
import pysam
import pandas as pd

from pkg_resources import get_distribution
from subprocess import call, check_call
from .maegatkHelp import *
from ruamel import yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sqs
from joblib import Parallel, delayed

@click.command()
@click.version_option()
@click.option('--input-dir', '-i', default = ".", required=True, help='Input; a directory containing individual .bam files')
@click.option('--output-dir', '-o', default="mgatk_out", help='Output directory for analysis.')

@click.option('--mito-genome', '-g', default = "rCRS", required=True, help='mitochondrial genome configuration. Requires bwa indexed fasta file or `rCRS` (built-in)')
@click.option('--min-reads-per-indel', '-m', default='5', required=True, help='minimum # of reads supporting a called indel by freebayes')
@click.option('--keep-intermediate', '-k', is_flag=True, help='whether to keep intermediate per-cell vcf files.')
@click.option('--ncores', '-c', default = "detect", help='Number of cores to run the main job in parallel.')

def main(input_dir, output_dir, mito_genome, min_reads_per_indel, ncores, keep_intermediate):
	
	"""
	maegatk: a Maester genome toolkit. \n
	INDEL calling \n
	"""
	
	script_dir = os.path.dirname(os.path.realpath(__file__))
	cwd = os.getcwd()
	__version__ = get_distribution('maegatk').version
	click.echo(gettime() + 'maegatk v%s' % __version__)

	# Determine which genomes are available
	rawsg = os.popen('ls ' + script_dir + '/bin/anno/fasta/*.fasta').read().strip().split("\n")
	supported_genomes = [x.replace(script_dir + '/bin/anno/fasta/', '').replace('.fasta', '') for x in rawsg]  
	
	# Determine cores
	if(ncores == 'detect'):
		ncores = str(available_cpu_count())
	else:
		ncores = str(ncores)

	# -------------------------------
	# Determine samples for analysis
	# -------------------------------
	bams = glob.glob(input_dir + '/*.bam')

	if len(bams) == 0:
		sys.exit('ERROR: Could not import any samples from the user specification; check --input parameter; QUITTING')

	# -------------------------------
	# Locate the mito genome
	# -------------------------------
	if any(mito_genome in s for s in supported_genomes):
		mito_fastaf = script_dir + '/bin/anno/fasta/' + mito_genome + '.fasta'
	elif os.path.exists(mito_genome):
		mito_fastaf = mito_genome
	else:
		sys.exit('ERROR: Could not find file ' + mito_genome + '; QUITTING')

	# -------------------------------
	# Run freebayes on all bam files
	# -------------------------------
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)
	if not os.path.exists(output_dir+'/vcf'):
		os.mkdir(output_dir+'/vcf')

	def run_freebayes(cell_bam_file):
		cell_name = cell_bam_file.split('/')[-1].replace('.qc.bam', '')
		cur_out_file = output_dir + '/vcf/{}.vcf'.format(cell_name)
		os.system('freebayes -C {} -f {} {} > {}'.format(min_reads_per_indel, mito_fastaf, cell_bam_file, cur_out_file))

	Parallel(n_jobs=int(ncores))(delayed(run_freebayes)(cbf) for cbf in bams)

    # very janky, could use parallelization if speed becomes an issue
	#for cell_bam_file in bams:
	#	cell_name = cell_bam_file.split('/')[-1].replace('.qc.bam', '')
	#	cur_out_file = output_dir + '/vcf/{}.vcf'.format(cell_name)
	#	os.system('freebayes -C {} -f {} {} > {}'.format(min_reads_per_indel, mito_fastaf, cell_bam_file, cur_out_file))

	# -------------------------------
	# Collapse the vcf files into one summary file
	# -------------------------------
	vcfs = glob.glob(output_dir + '/vcf/*.vcf')
	vcf_summary = []
	for cell_vcf_file in vcfs:
		cell_name = cell_vcf_file.split('/')[-1].replace('.vcf', '')
		cur_content = [x.split('\t') for x in open(cell_vcf_file, 'r').readlines() if x[0] != '#']  # remove documentation lines

		# keep only position x[1], ref x[3], alt x[4], quality score x[5], and other supporting info x[-2]
		cur_content = [[x[1], x[3], x[4], x[5], x[-3]] for x in cur_content if len(x[3]) != len(x[4]) and ',' not in x[4]]  # choose indels only
		extra_info = []
		for cur_entry in cur_content:
			extra_info.append(dict([x.split('=') for x in cur_entry[-1].split(';')]))
		summarized_entry = [[cell_name] + x[:-1] + [extra_info[i]['RO'], extra_info[i]['AO']] for i, x in enumerate(cur_content)]
		vcf_summary += summarized_entry
	vcf_summary = pd.DataFrame(vcf_summary)
	vcf_summary.columns = ['cell_barcode', 'pos', 'ref', 'alt', 'score', 'ref_reads', 'alt_reads']
	vcf_summary.to_csv(output_dir + '/indel_summary.csv')

	if not keep_intermediate:
		os.system('rm -r {}/vcf'.format(output_dir))
