import chromadb
import vertexai
import os

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location="us-central1"
)

def get_chroma_client():
    return chromadb.PersistentClient(
        path="/Users/aindrilkar/notebooks/workforce_management/chromadb_vector"
    )
