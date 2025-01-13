import os
import datetime
import platform
import subprocess
import pandas as pd

osplat=platform.system()
print("Current OS is " + osplat)
current_time = datetime.datetime.now()
print("Process started at ",current_time)

#Taking input FASTQ files
print("Taking input FASTQ files of control samples")
Read1=input("Enter the Read1 FASTQ file\n")
Read2=input("Enter the Read2 FASTQ file\n")
print("Taking input FASTQ files of experiment samples ")
Read3=input("Enter the Read1 FASTQ file\n")
Read4=input("Enter the Read2 FASTQ file\n")
file_path1=""
file_path2=""
hisat2_index = 'reference_genome/grch38/genome'  # Path to HISAT2 index
gtf_file = 'reference_genome/Homo_sapiens.GRCh38.104.gtf' #Path to gtf index
dir_path = 'Analysis_' + current_time.strftime("%d_%m_%Y")
os.mkdir(dir_path)
dir_path='Analysis_13_01_2025'

#Using a loop 2 times for Control and Experminet samples
i=1
while(i<3):
    
    #Running HISAT2 Software
    print("HISAT2 Process Started")
    # Naming the input files and output
    file_name = os.path.basename(Read1)
    sample_name = file_name.replace("_1.fastq", "")
    base_name, extension = os.path.splitext(sample_name)
    print("Sample Name:", base_name)
    
    output_sam = dir_path + '/' + base_name + '_aligned.sam'  # Path to output SAM file
    # Build the HISAT2 command as a list of arguments
    hisat2_command = [
        'hisat2',                # HISAT2 command
        '-p', '10',              # Number of threads
        '-x', hisat2_index,      # HISAT2 index base
        '-1', Read1,      # Forward read file
        '-2', Read2,      # Reverse read file
        '-S', output_sam         # Output SAM file
    ]
    # Executing the HISAT2 command
    subprocess.run(hisat2_command, check=True)
    
    Read1=Read3
    Read2=Read4
    print(f"Alignment complete. Output SAM file saved to {output_sam}")
    
    #Running featurecounts Software
    print("FeatureCounts Process Started")
    # Defining the paths
    sam_file = dir_path + '/' + base_name + '_aligned.sam'
    output_file = dir_path + '/' + base_name + '_featurecounts.txt'

    # Running the featureCounts command using subprocess
    featurecounts_command = [
        'featureCounts',
        '-p',                    # Paired-end reads
        '-T', '10',               # Number of threads
        '-t', 'exon',             # Focus on exons
        '-g', 'gene_id',          # Group by gene_id
        '-a', gtf_file,           # GTF annotation file
        '-o', output_file,        # Output file for counts
        sam_file                 # Input SAM file
    ]
    subprocess.run(featurecounts_command, check=True)
    print(f"Alignment complete. Count file saved to {output_file}")

    #removing the first line from the counts file
    def delete_first_line(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        with open(filename, 'w') as file:
            file.writelines(lines[1:])  # Writting the file back, excluding the first line

    delete_first_line(dir_path + '/' + base_name + '_featurecounts.txt')
    if i==1:
        file_path1 = dir_path + '/' + base_name + '_featurecounts.txt'
        print(file_path1)
    elif i==2:
        file_path2 = dir_path + '/' + base_name + '_featurecounts.txt'
        print(file_path2)
    else:
        print("Error in file path")
    i+=1

#extracting geneid and counts columns from the featurecounts output
df = pd.read_csv(file_path1, sep='\t', comment='!', header=0)
df2 = pd.read_csv(file_path2, sep='\t', comment='!', header=0)

#extracting the geneid and counts columns   
gene_column = 'Geneid'
count_columnC = df.columns[6]
count_columnE = df2.columns[6]

# Creating new DataFrames with selected columns
df_selected = df[[gene_column, count_columnC]].copy()
df2_selected = df2[[gene_column, count_columnE]].copy()

# Merging the DataFrames on the 'Geneid' column
combined_df = pd.merge(df_selected, df2_selected, on=gene_column, how='inner')

# Renaming the columns
combined_df.columns = [gene_column, 'Control', 'Experiment']

# Save the combined DataFrame to a CSV file
combined_df.to_csv(dir_path + '/combined_output.csv', index=False)

print("Combined DataFrame saved to 'combined_output.csv'")

#Performing Differential Gene Expression Analysis using the bioconductor package edgeR using Rpy2
print("Performing Differential Gene Expression Analysis using the bioconductor package edgeR using Rpy2")
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector, StrVector
from rpy2.robjects import pandas2ri

# Import edgeR
edgeR = importr("edgeR")

#importing the counts file
pandas2ri.activate()

# Define the directory and file name in Python
file_path = f"{dir_path}/combined_output.csv"

# Passing the file path to R and loading the CSV
r_code = f"""read.csv("{file_path}", row.names = 'Geneid')
"""
print(r_code)

# Execute the R code
counts_df = robjects.r(r_code)
group = StrVector(["Control", "Experiment"])

# Create a DGEList object
dge = edgeR.DGEList(counts=counts_df, group=group)
print(dge)