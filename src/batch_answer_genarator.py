import csv
import chromadb
import sys
import pandas as pd
sys.path.append("src")
from query_module import HistoryQuestionAnswerer

def process_csv(input_csv_path, output_csv_path, collection_name):
    """
    Processes a CSV file containing questions, retrieves answers using HistoryQuestionAnswerer,
    and writes the results to a new CSV file, preserving all original columns and adding
    'Answer', 'Context', 'Sections', and 'Pages' columns.

    Args:
        input_csv_path (str): Path to the input CSV file.
        output_csv_path (str): Path to the output CSV file.
        collection_name (str): Name of the ChromaDB collection.
    """

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="processed_data/chroma_db")

    # Initialize HistoryQuestionAnswerer
    answerer = HistoryQuestionAnswerer(client=client, collection_name=collection_name)

    # Read the input CSV into a Pandas DataFrame
    df = pd.read_csv(input_csv_path)

    # Create new columns for 'Answer', 'Context', 'Sections', and 'Pages'
    df['Answer'] = ""
    df['Context'] = ""
    df['Sections'] = ""
    df['Pages'] = ""

    # Iterate through each row of the DataFrame
    for index, row in df.iterrows():
        question = row['Question']  # Assuming 'Question' is the column name
        try:
            answer_data = answerer.answer_question(question)
            df.at[index, 'Answer'] = answer_data['answer']
            df.at[index, 'Context'] = answer_data['context']
            df.at[index, 'Sections'] = ", ".join(answer_data['sections']) if answer_data['sections'] else ""
            df.at[index, 'Pages'] = ", ".join(map(str, answer_data['pages'])) if answer_data['pages'] else ""

        except Exception as e:
            df.at[index, 'Answer'] = f"Error: {str(e)}"
            df.at[index, 'Context'] = "N/A"
            df.at[index, 'Sections'] = "N/A"
            df.at[index, 'Pages'] = "N/A"

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)
    print(f"Processed data saved to {output_csv_path}")

if __name__ == "__main__":
    input_csv_path = 'data/questions.csv'  # Replace with your input CSV file path
    output_csv_path = 'processed_data/output(questions).csv'  # Replace with your desired output CSV file path
    collection_name = "textbook"  # Replace with your ChromaDB collection name
    process_csv(input_csv_path, output_csv_path, collection_name)
