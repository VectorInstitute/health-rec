import chromadb

chroma_client = chromadb.HttpClient(host="chromadb", port=8000)

collection = chroma_client.get_collection(name="test")
print(collection.count())
for k, v in collection.get(include=["documents", "embeddings", "metadatas"]).items():
    print(k)
    print(v)
    print(len(v), [len(i) for i in v])
    print("---")
    print()


# Tr

# chroma_client.delete_collection(name="test")

# print("Collection 'test' has been deleted.")
