import os
from Bio import SeqIO
from Bio import pairwise2
import pandas as pd
import psycopg2

def create_dataframe(filenames):
    columns = ['query_sequence'] + filenames
    df = pd.DataFrame(columns=columns)
    df = df.fillna(0)  
    return df

connection = psycopg2.connect(
    dbname="seq_db",
    user="adejoro",
    password="adeboye",
    host="localhost",
    port="5432"
)

def get_all_filenames(connection):
    filenames = []
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            table_name = row[0]
            query = f"SELECT DISTINCT filename FROM {table_name}"
            cursor.execute(query)
            filenames.extend(filename[0] for filename in cursor.fetchall())
    return filenames

def remove_extension(filenames):
    return [filename.replace('.fastq', '') for filename in filenames]


# Prompt user for query file paths, threshold, and fixed length
forward_query_file = input("Enter the path to the forward query file: ")
reverse_query_file = input("Enter the path to the reverse query file: ")
threshold = float(input("Enter the threshold for sequence alignment: "))
fixed_length = int(input("Enter the fixed length for trimming adapters: "))

print("Retrieving filenames from the database...")
filenames = get_all_filenames(connection)
print("Filenames retrieved:", filenames)

print("Removing '.fastq' extension from filenames...")
filenames = remove_extension(filenames)
print("Filenames without extension:", filenames)

print("Creating dataframe with columns for filenames...")
df = create_dataframe(filenames)
print("Dataframe created:", df)

non_matching_sequences = []

for query_file in [forward_query_file, reverse_query_file]:
    print(f"Processing query file: {query_file}")
    for record in SeqIO.parse(query_file, "fastq"):
        query_sequence = str(record.seq)[fixed_length:-fixed_length] if fixed_length > 0 else str(record.seq)
        row_values = {'query_sequence': query_sequence}
        row_values.update({filename: 0 for filename in filenames})  
        df = pd.concat([df, pd.DataFrame.from_records([row_values])], ignore_index=True) #This sets up a basic skeleton for a row entry to be updated later
        
        with connection.cursor() as cursor:
            print("Fetching table names from the database...")
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            table_names = cursor.fetchall()
            print("Table names fetched:", table_names)
            
            for table_name in table_names:
                table_name = table_name[0]  
                print("Processing table:", table_name)

                
                cursor.execute(f"SELECT sequence,filename FROM {table_name}")
                rows = cursor.fetchall() #Fetch sequence and corresponding filename from the database

                for row in rows:
                    database_sequence = row[0]
                    filename = row[1]
                    filename = filename.replace('.fastq', '')
                    alignment_score = pairwise2.align.globalxx(query_sequence, database_sequence, score_only=True)
                    print("Alignment score:", alignment_score)
                    print("Query sequence:", query_sequence)
                    print("Filename:", filename)
                    if alignment_score >= threshold:
                        df.at[df.index[df['query_sequence'] == query_sequence][0], filename] += 1
                        
                    else: 
                        non_matching_sequences.append(query_sequence)
                        
                

print("Final DataFrame:")
print(df)
df.to_csv('alignment_results.csv', index=False)

with open('non_matching_sequences.fasta', 'w') as fasta_file:
    for i, sequence in enumerate(non_matching_sequences, start=1):
            fasta_file.write(f'>Query_{i}\n{sequence}\n')