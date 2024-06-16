import cohere
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.schema import TextNode
from llama_index.embeddings.cohere import CohereEmbedding
from pathlib import Path
from .document_processor import process_documents

class RetrieverWithRerank:
    def __init__(self, api_key, model_name="embed-multilingual-v3.0"):
        self.api_key = api_key
        self.model_name = model_name
        self.co = cohere.Client(api_key=api_key)
        self.embed_model = CohereEmbedding(cohere_api_key=self.api_key, model_name=self.model_name)
        self.path_index = Path("./vector_index")

    def build_index(self, document_paths):
        documents = process_documents(document_paths)
        text_nodes = [TextNode(text=doc) for doc in documents]
        self.index = VectorStoreIndex(text_nodes, embed_model=self.embed_model)
        storage_context = self.index.storage_context
        storage_context.persist(self.path_index)

    def retrieve(self, query, top_k=60, top_n=20):
        if not self.path_index.exists():
            raise ValueError("Index does not exist. Build the index first.")
        
        storage_context = StorageContext.from_defaults(persist_dir=self.path_index)
        index = load_index_from_storage(storage_context, embed_model=self.embed_model)

        retriever = index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        nodes = [{"text": node.node.text, "llamaindex_id": node.node.id_} for node in nodes]

        reranked = self.co.rerank(query=query, documents=nodes, model="rerank-multilingual-v3.0", top_n=top_n)
        return [nodes[node.index] for node in reranked.results]
