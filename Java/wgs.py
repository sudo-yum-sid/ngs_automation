import os
import platform
osplat=platform.system()
print("Current OS is " + osplat)

#Taking input FASTQ files
print("Taking input FASTQ files")
Read1=input("Enter the Read1 FASTQ file\n")
Read2=input("Enter the Read2 FASTQ file\n")

#Input for BWA
#print("Taking input for BWA-MEM")
#gendir=input("Enter the Reference Genome Directory\n")
gendir="/mnt/d/Agilent\ CommonStorages/SureCall/GenomeReferences/hg38/hg38/hg38.fasta"
parameters=input("Enter BWA-MEM parameters from the help guide (no need to mention output file name)\n")

#Running FASTQC Sofware
print("Running FASTQC on the read files\n")
qc="fastqc" + " " + Read1 + " " + Read2
os.system(qc)

#Running BWA Software
print("BWA-MEM Process Started")
out="-o temp.sam"
align="bwa mem" + " " + gendir + " " + parameters + " " + Read1 + " " + Read2 + " " + out
os.system(align)

#Running Samtools to convert sam to bam
print("Converting SAM to BAM")
samfile="temp.sam"
conv="samtools view -S -b" + " " + samfile + " " + ">" + "aligned.bam"
os.system(conv)

#Running Picard's SortSam to sort the bam file
print("Sorting the BAM file")
bamfile="aligned.bam"
from subprocess import PIPE, Popen
process = Popen(['java', '-jar', 'picard.jar', 'SortSam', 'CREATE_INDEX=true', 'INPUT=',bamfile, 'OUTPUT=sorted.bam', 'SORT_ORDER=coordinate'], stdout=PIPE, stderr=PIPE)
result = process.communicate()
print(result[0].decode('utf-8'))

#Running Picard's MarkDuplicates to tag duplicate reads 
print("Tagging the duplicate reads")
bamfile="sorted.bam"
from subprocess import PIPE, Popen
process = Popen(['java', '-jar', 'picard.jar', 'MarkDuplicates', 'CREATE_INDEX=true', 'INPUT=',bamfile, 'OUTPUT=marked.bam', 'METRICS_FILE=dup_metrics.txt'], stdout=PIPE, stderr=PIPE)
result = process.communicate()
print(result[0].decode('utf-8'))

#Running Samtools mpileup
print("Generating pileup using samtools")
bamfile="marked.bam"
pileup="samtools  mpileup -B -f" + " " + gendir + " " + bamfile + " " + ">" + "mydata.pileup"
os.system(pileup)
