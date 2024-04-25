### Read Me

## mock_data
The mock_data folder contains fastq files. Enter the path to the mock_data as the source_folder to the source folder prompt in the `generate_database.py` script.

## generate_database.py
This script will prompt for:
1. source folder, a path to the folder that contains fastq files whose reads are to be uploaded to the database
2. fixed length, if your fastq files have adapters that require trimming. For this mock data, fixed length is 0.

The script takes the files in the source folder, parses the reads inside, and uploads them to a postgreSQL database. Each paired end data (forward and reverse) gets its own table.

## query_database.py
This script will proompt for:
1. path to forward query file
2. path to reverse query file
3. fixed length
4. threshold

The files R3_R1.fastq and R3_R2.fastq should be passed as forward query file and reverse query file respectively. They are dummy fastq files creating with biopython. Fixed length should be 0 and threshold should be 30.
This script queries the reads in the query files against the database and generates a csv file. The first column in the csv file is the query_sequence, the other columns are filenames like R1_R1, R1_R2 etc. This way, we can keep track of how many times within a file a hit for the query_sequence is found (intra-frequence) and across how many files the hit is found (inter-frequency)

If a query sequence fails to get any hits, it is written into a fasta file.
