import os
import platform
import subprocess
osplat=platform.system()
print("Current OS is " + osplat)

#Taking input FASTQ files
print("Taking input FASTQ files")
Read1=input("Enter the Read1 FASTQ file\n")
Read2=input("Enter the Read2 FASTQ file\n")

#creating output folder
# Define the directory path
directory_path = 'output'

# Create the directory (if it doesn't exist)
if not os.path.exists(directory_path):
    os.makedirs(directory_path)
    print(f"Directory '{directory_path}' created.")


    #Running HISAT2 Software
    print("HISAT2 Process Started")
    # Define paths to input files and output
    hisat2_index = 'reference_genome/grch38/genome'  # Path to HISAT2 index
    output_sam = 'output/aligned.sam'  # Path to output SAM file

    # Build the HISAT2 command as a list of arguments
    hisat2_command = [
        'hisat2',                # HISAT2 command
        '-p', '10',              # Number of threads
        '-x', hisat2_index,      # HISAT2 index base
        '-1', Read1,      # Forward read file
        '-2', Read2,      # Reverse read file
        '-S', output_sam         # Output SAM file
    ]

    # Execute the HISAT2 command
    subprocess.run(hisat2_command, check=True)
    print(f"Alignment complete. Output SAM file saved to {output_sam}")

    #Running featurecounts Software
    print("FeatureCounts Process Started")
    # Define the paths
    sam_file = 'output/aligned.sam'
    gtf_file = 'reference_genome/Homo_sapiens.GRCh38.104.gtf'
    output_file = 'output/featurecounts.txt'

    # Run the featureCounts command using subprocess
    featurecounts_command = [
        'featureCounts',
        '-p',                    # Paired-end reads
        '-T', '10',               # Number of threads
        '-t', 'exon',             # Focus on exons
        '-g', 'gene_id',          # Group by gene_id
        '-a', gtf_file,           # GTF annotation file
        '-o', output_file,        # Output file for counts
        sam_file                  # Input SAM file
    ]
    subprocess.run(featurecounts_command, check=True)
    print(f"Alignment complete. Count file saved to {output_file}")

    #removing the first line from the counts file
    def delete_first_line(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        with open(filename, 'w') as file:
            file.writelines(lines[1:])  # Write the file back, excluding the first line

    delete_first_line('output/featurecounts.txt')

    #extracting geneid and counts columns from the featurecounts output
    import pandas as pd
    file_path = "output/featurecounts.txt"
    df = pd.read_csv(file_path, sep='\t', comment='!', header=0)

    #extracting the geneid and counts columns   
    gene_column = 'Geneid'
    count_column = df.columns[6]
    results = df[[gene_column, count_column]]

    #saving the extracted columns to a new csv file
    results.to_csv('output/gene_counts.csv', index=False)

else:
    print(f"Directory '{directory_path}' already exists.")
