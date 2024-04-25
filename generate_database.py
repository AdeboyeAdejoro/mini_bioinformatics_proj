import os
from Bio import SeqIO
import psycopg2

# Prompt user for source folder to fastq files and fixed length
source_folder = input("Enter the path to fastq source folder: ")
fixed_length = int(input("Enter the fixed length to be trimmed: "))

# Connect to the database I set up in psql
connection = psycopg2.connect(
    dbname="seq_db",
    user="adejoro",
    password="adeboye",
    host="localhost",
    port="5432"
)

# List files and sort them
files = os.listdir(source_folder)
sorted_files = sorted(files)

# Iterate over files in steps of 2
for i in range(0, len(sorted_files), 2):
    table_name = f"table_{i // 2 + 1}"  # Generate dynamic table name
    
    # Create table dynamically
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            sequence_id TEXT PRIMARY KEY,
            sequence TEXT NOT NULL,
            length INT NOT NULL,
            filename TEXT NOT NULL
        );
    """
    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
    
    # Process each file in the pair
    for file_name in sorted_files[i:i+2]:
        file_path = os.path.join(source_folder, file_name)
        
        # Process reads from the file
        for record in SeqIO.parse(file_path, "fastq"):
            sequence_id = record.id
            sequence = str(record.seq)[fixed_length:-fixed_length] if fixed_length > 0 else str(record.seq)
            length = len(sequence)
            
            # Insert record into the table
            insert_query = f"""
                INSERT INTO {table_name} (sequence_id, sequence, length, filename)
                VALUES (%s, %s, %s, %s);
            """
            with connection.cursor() as cursor:
                cursor.execute(insert_query, (sequence_id, sequence, length, file_name))
    
    # Commit the transaction
    connection.commit()

# Close the connection
connection.close()