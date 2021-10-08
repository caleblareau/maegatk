import click
import os
import os.path
import sys
import shutil
import random
import string
import itertools
import time
import pysam

from pkg_resources import get_distribution
from subprocess import call, check_call
from .maegatkHelp import *
from ruamel import yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sqs
from multiprocessing import Pool

@click.command()
@click.version_option()
@click.option('--input', '-i', default = ".", required=True, help='Input; a singular, indexed bam file. ')
@click.option('--ncores', '-c', default = "detect", help='Number of cores to run the main job in parallel.')

def main(input):
	
	"""
	maegatk: a Maester genome toolkit. \n
	INDEL calling \n
	"""
	
	script_dir = os.path.dirname(os.path.realpath(__file__))
	cwd = os.getcwd()
	__version__ = get_distribution('maegatk').version
	click.echo(gettime() + "maegatk v%s" % __version__)
	
	# Determine cores
	if(ncores == "detect"):
		ncores = str(available_cpu_count())
	else:
		ncores = str(ncores)
