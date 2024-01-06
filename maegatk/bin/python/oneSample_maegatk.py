#!/usr/bin/python

from os.path import join
import os
import subprocess
import sys
import shutil
import pysam
from ruamel import yaml

configFile = sys.argv[1]
inputbam = sys.argv[2]
outputbam = sys.argv[3]
sample = sys.argv[4]

with open(configFile, 'r') as stream:
	config = yaml.load(stream, Loader=yaml.Loader)

# Parse the configuration variables
indir = config["input_directory"]
outdir = config["output_directory"]
script_dir = config["script_dir"]

mito_genome = config["mito_chr"]
mito_length = str(config["mito_length"])
fasta_file = config["fasta_file"]

umi_barcode = config["umi_barcode"]

base_qual = str(config["base_qual"])
alignment_quality = config["alignment_quality"]
NHmax = config["NHmax"]
NMmax = config["NMmax"]
min_reads = str(config["min_reads"])

max_javamem  = config["max_javamem"]

# Software paths
java = "java"
python = "python"

# Script locations
filtclip_py = script_dir + "/bin/python/filterClipBam.py"
detailedcall_py = script_dir + "/bin/python/detailedCalls.py"
sumstatsBP_py = script_dir + "/bin/python/sumstatsBP.py"
fgbio = java + " -Xmx"+max_javamem+"  -jar " + script_dir + "/bin/fgbio.jar"

# Prepare filepath locations
rmlog = outputbam.replace(".qc.bam", ".rmdups.log").replace("/temp/ready_bam/", "/logs/rmdupslogs/")
filtlog = outputbam.replace(".qc.bam", ".filter.log").replace("/temp/ready_bam/", "/logs/filterlogs/")
temp_bam0 = outputbam.replace(".qc.bam", ".temp0.bam").replace("/temp/ready_bam/", "/temp/temp_bam/")
temp_bam1 = outputbam.replace(".qc.bam", ".temp1.bam").replace("/temp/ready_bam/", "/temp/temp_bam/")
temp_sam15 = outputbam.replace(".qc.bam", ".temp1.5.sam").replace("/temp/ready_bam/", "/temp/temp_bam/")
temp_bam15 = outputbam.replace(".qc.bam", ".temp1.5.bam").replace("/temp/ready_bam/", "/temp/temp_bam/")
temp_bam2 = outputbam.replace(".qc.bam", ".temp2.bam").replace("/temp/ready_bam/", "/temp/temp_bam/")
temp_fastq = outputbam.replace(".qc.bam", ".temp0.fastq").replace("/temp/ready_bam/", "/temp/temp_bam/")


prefixSM = outdir + "/temp/sparse_matrices/" + sample
outputdepth = outdir + "/qc/depth/" + sample + ".depth.txt"

# 1) Filter bam files
proper_paired = "False"
pycall = " ".join([python, filtclip_py, inputbam, filtlog, mito_genome, proper_paired, NHmax, NMmax]) + " > " + temp_bam0
os.system(pycall)

# 2) Sort the filtered bam file
fgcallone =  fgbio + " GroupReadsByUmi -s Identity -e 0 -i " + temp_bam0 + " -o " + temp_bam1 + " -t "+ umi_barcode
os.system('echo "'+fgcallone+'"')
os.system(fgcallone)

# 2.5) Modify the UB tag
samtoolscall = 'samtools view -H ' + temp_bam1 + '> ' + temp_sam15 + '; samtools view ' + temp_bam1 + '| awk \'OFS="\t" {$13=$13""$4; print $0}\' >> ' + temp_sam15 + '; samtools view -b ' + temp_sam15 + '> ' + temp_bam15
os.system('echo "'+samtoolscall+'"')
os.system(samtoolscall)

# 3) Call consensus reads
fgcalltwo = fgbio + " CallMolecularConsensusReads -t "+umi_barcode+" -i "+temp_bam15+" -o " + temp_bam2 +" -M " + min_reads
os.system(fgcalltwo)
print(fgcalltwo)

# 4) Convert consensus bam to fastq
# bedtools_call = "bedtools bamtofastq -i "+ temp_bam2 +" -fq " + temp_fastq # Bedtools stopped working for some reason, replacing it with samtools fastq
samtoolscall2 = 'samtools fastq -T cM ' + temp_bam2 + " | sed 's/\tcM:i:/_/g' > " + temp_fastq
os.system(samtoolscall2)

# 5) Remap + sort bam files
bwa_call = "bwa mem " + fasta_file + " " + temp_fastq + " | samtools sort -o "+ outputbam +" -"
os.system(bwa_call)
pysam.index(outputbam)

# 6) Get allele counts per sample / base pair and per-base quality scores
alleleCountcall = " ".join([python, sumstatsBP_py, outputbam, prefixSM, mito_genome, mito_length, base_qual, sample, fasta_file, alignment_quality])
os.system(alleleCountcall)

# 7) Get depth from the coverage sparse matrix
with open(prefixSM + ".coverage.txt", 'r') as coverage:
	depth = 0
	for row in coverage:
		s = row.split(",")
		depth += int(s[2].strip())
with open(outputdepth, 'w') as d:
	d.write(sample + "\t" + str(round(float(depth)/float(mito_length),2)) + "\n")
