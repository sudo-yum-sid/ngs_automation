import os
import platform
osplat=platform.system()
print("Current OS is "+ osplat)

#Taking input FASTQ files
print("Taking input FASTQ files")
Read1=input("Enter the Read1 FASTQ file\n")
Read2=input("Enter the Read2 FASTQ file\n")

#Input for BWA
print("Taking Input for BWA-MEM")
gendir=input("Enter the Reference Genome Directory\n")
parameters=input("Enter BWA-MEM parameters from the help guide (no need to mention output file name)\n")

#Running FASTQC Software
fastqc="fastqc"
print("Running FASTQC on the read files\n")
qc=fastqc + " " + Read1 + " " + Read2
os.system(qc)

#Running BWA Software
print("BWA-MEM Process Started")
out="-o temp.sam"
align="bwa mem" + " " +