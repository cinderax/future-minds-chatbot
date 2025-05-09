import chromadb

# Initialize the client (use your persistent path if applicable)
client = chromadb.PersistentClient(path="processed_data/chroma_db")

# List all collection names
collections = client.list_collections()

print("Available collections:")
for name in collections:
    print(f" - {name}")
##use this to know what collection available in the chroma_db