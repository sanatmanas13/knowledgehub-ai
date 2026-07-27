import chromadb
from utils.embedding import generate_embeddings
from chromadb.api.types import QueryResult
# Create the client once
client = chromadb.PersistentClient(path="./chroma_db")

# Get or create the collection once
collection = client.get_or_create_collection(
    name="documents"
)


def store_embeddings(chunks, embeddings, filename):
    ids = []
    documents = []
    embedding_list = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        ids.append(f"{filename}_chunk_{index}")
        documents.append(chunk)
        embedding_list.append(embeddings[index])
        metadatas.append(
            {
                "filename": filename,
                "chunk": index
            }
        )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embedding_list,
        metadatas=metadatas
    )

    return len(ids)

def retrieve_chunks(question: str,top_k: int = 5) -> QueryResult:
    query_embedding = generate_embeddings([question])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ],
    )
    
    return results
