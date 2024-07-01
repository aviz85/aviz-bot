import os
import io
import requests
import csv
import json
import faiss
import numpy as np
import pickle
from typing import Union, List, Dict, Any
from cohere import Client
from docx import Document
from PyPDF2 import PdfReader
from llama_index.core import Document as LlamaDocument
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import MetadataMode
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class VectorDB:
    # Configuration constants
    CHUNK_SIZE = 100
    CHUNK_OVERLAP = 20
    COHERE_EMBED_MODEL = "embed-multilingual-v3.0"
    COHERE_RERANK_MODEL = "rerank-multilingual-v3.0"
    INITIAL_SEARCH_K = 100  # Number of initial results to fetch from FAISS
    RERANK_TOP_N = 5  # Number of results to return after reranking
    
    def __init__(self, file_path_or_url: str):
        print("Initializing VectorDB...")
        cohere_api_key = os.getenv('COHERE_API_KEY')
        if not cohere_api_key:
            raise ValueError("COHERE_API_KEY not found in environment variables")
        
        self.cohere_client = Client(cohere_api_key)
        print("Cohere client initialized.")
        
        self.file_path = file_path_or_url
        self.chunks_file = f"{self.file_path}.chunks"
        self.embeddings_file = f"{self.file_path}.embeddings"
        self.index_file = f"{self.file_path}.index"
        
        if self._load_existing_data():
            print("Loaded existing data.")
        else:
            self.file_content = self._load_file(file_path_or_url)
            print(f"File loaded. Content length: {len(self.file_content)} characters")
            
            self.chunks = self._split_text()
            print(f"Text split into {len(self.chunks)} chunks")
            
            self.embeddings = self._create_embeddings()
            print(f"Embeddings created. Shape: {self.embeddings.shape}")
            
            self.index = self._create_faiss_index()
            print("FAISS index created")
            
            self._save_data()
            print("Data saved for future use.")
        
        print("VectorDB initialization complete")

    def _load_existing_data(self) -> bool:
        if os.path.exists(self.chunks_file) and os.path.exists(self.embeddings_file) and os.path.exists(self.index_file):
            with open(self.chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)
            with open(self.embeddings_file, 'rb') as f:
                self.embeddings = np.load(f)
            self.index = faiss.read_index(self.index_file)
            return True
        return False

    def _save_data(self):
        with open(self.chunks_file, 'wb') as f:
            pickle.dump(self.chunks, f)
        with open(self.embeddings_file, 'wb') as f:
            np.save(f, self.embeddings)
        faiss.write_index(self.index, self.index_file)

    def _load_file(self, file_path_or_url: str) -> str:
        print(f"Loading file from: {file_path_or_url}")
        if file_path_or_url.startswith(('http://', 'https://')):
            response = requests.get(file_path_or_url)
            content = response.content
            print("File loaded from URL")
            return self._process_file_content(content, file_path_or_url)
        else:
            file_extension = os.path.splitext(file_path_or_url)[1].lower()
            if file_extension == '.docx':
                return self._process_docx(file_path_or_url)
            else:
                reader = SimpleDirectoryReader(input_files=[file_path_or_url])
                documents = reader.load_data()
                content = documents[0].get_content()
                print("File loaded using SimpleDirectoryReader")
                return content

    def _process_docx(self, file_path: str) -> str:
        print(f"Starting to process DOCX file: {file_path}")
        try:
            doc = Document(file_path)
            print(f"DOCX file loaded successfully. Number of paragraphs: {len(doc.paragraphs)}")
            
            paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
            print(f"Number of non-empty paragraphs: {len(paragraphs)}")
            
            content = "\n".join(paragraphs)
            print(f"DOCX processed. Result length: {len(content)} characters")
            
            if not content.strip():
                print("Processed DOCX content is empty")
            else:
                print(f"First 100 characters of content: {content[:100]}")
            
            return content
        except Exception as e:
            print(f"Error processing DOCX file: {str(e)}")
            raise


    def _process_file_content(self, content: bytes, file_name: str) -> str:
        file_extension = os.path.splitext(file_name)[1].lower()
        if file_extension == '.docx':
            return self._process_docx_content(content)
        elif file_extension == '.txt':
            return content.decode('utf-8')
        elif file_extension == '.pdf':
            return self._process_pdf(content)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _process_docx_content(self, content: bytes) -> str:
        print("Processing DOCX content")
        doc = Document(io.BytesIO(content))
        processed_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        print(f"DOCX content processed. Result length: {len(processed_content)} characters")
        return processed_content
        
    def _split_text(self) -> List[str]:
        print("Splitting text into chunks")
        document = LlamaDocument(text=self.file_content)
        parser = SimpleNodeParser.from_defaults(chunk_size=self.CHUNK_SIZE, chunk_overlap=self.CHUNK_OVERLAP)
        nodes = parser.get_nodes_from_documents([document])
        chunks = [node.get_content(metadata_mode=MetadataMode.EMBED) for node in nodes]
        print(f"Text split into {len(chunks)} chunks")
        return chunks

    def _create_embeddings(self) -> np.ndarray:
        print("Creating embeddings")
        embeddings = self.cohere_client.embed(
            texts=self.chunks,
            model=self.COHERE_EMBED_MODEL,
            input_type="search_document"
        ).embeddings
        embeddings_array = np.array(embeddings, dtype=np.float32)
        print(f"Embeddings created. Shape: {embeddings_array.shape}")
        return embeddings_array

    def _create_faiss_index(self) -> faiss.IndexFlatL2:
        print("Creating FAISS index")
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(self.embeddings)
        print(f"FAISS index created with {index.ntotal} vectors")
        return index

    def _rerank(self, queries: List[str], initial_results: List[str]) -> List[Dict[str, Any]]:
        print(f"Starting reranking process for {len(queries)} queries and {len(initial_results)} initial results")
        
        try:
            all_reranked_results = []
            for query in queries:
                print(f"Reranking for query: {query}")
                
                if not initial_results:
                    print("Initial results list is empty")
                    continue
                
                rerank_results = self.cohere_client.rerank(
                    model=self.COHERE_RERANK_MODEL,
                    query=query,
                    documents=initial_results,
                    top_n=self.RERANK_TOP_N,
                    return_documents=False  # We don't need the API to return documents
                )
                
                print(f"Rerank API response: {rerank_results}")
                
                if rerank_results is None or not hasattr(rerank_results, 'results'):
                    print(f"Unexpected rerank response structure: {rerank_results}")
                    continue
                
                for result in rerank_results.results:
                    if result is None:
                        print("Encountered None result in reranked results")
                        continue
                    if not hasattr(result, 'index') or not hasattr(result, 'relevance_score'):
                        print(f"Unexpected result structure: {result}")
                        continue
                    all_reranked_results.append({
                        'text': initial_results[result.index],  # Get the text from our original list
                        'index': result.index,
                        'relevance_score': result.relevance_score
                    })
            
            print(f"Total reranked results: {len(all_reranked_results)}")
            
            # Deduplicate results based on the text
            unique_results = {result['text']: result for result in all_reranked_results}
            
            sorted_results = sorted(unique_results.values(), key=lambda x: x['relevance_score'], reverse=True)
            
            print(f"Reranking complete. Top {len(sorted_results)} unique results returned")
            return sorted_results[:self.RERANK_TOP_N]
        
        except Exception as e:
            print(f"Error in reranking process: {str(e)}")
            return []
            
            
    def search(self, queries: Union[str, List[str]], do_rerank: bool = True) -> List[Dict[str, Any]]:
        if isinstance(queries, str):
            queries = [queries]
        
        print(f"Searching for queries: {queries}")
        
        # Step 1: Get initial results from FAISS
        print("Step 1: Getting initial results from FAISS")
        query_embeddings = self.cohere_client.embed(
            texts=queries,
            model=self.COHERE_EMBED_MODEL,
            input_type="search_query"
        ).embeddings
        print("Query embeddings created")
        
        all_indices = []
        all_distances = []
        for query_embedding in query_embeddings:
            distances, indices = self.index.search(np.array([query_embedding]), self.INITIAL_SEARCH_K)
            all_indices.extend(indices[0])
            all_distances.extend(distances[0])
        
        # Remove duplicates while preserving order
        unique_indices = []
        seen = set()
        for index in all_indices:
            if index not in seen:
                seen.add(index)
                unique_indices.append(index)
        
        initial_results = [self.chunks[i] for i in unique_indices[:self.INITIAL_SEARCH_K]]
        print(f"Initial search complete. Found {len(initial_results)} unique results")
        
        if not do_rerank:
            print("Skipping rerank process as per the flag")
            return [{"text": initial_results[i], "relevance_score": all_distances[i], "original_index": int(unique_indices[i])} for i in range(min(len(initial_results), self.RERANK_TOP_N))]
        
        # Step 2: Rerank the initial results
        print("Step 2: Reranking initial results")
        reranked_results = self._rerank(queries, initial_results)
        
        # Step 3: Return the reranked results with original indices
        print("Step 3: Preparing final results")
        final_results = []
        
        if not reranked_results:
            print("No results to process after reranking")
            return []
        
        for result in reranked_results:
            final_results.append({
                "text": result['text'],
                "relevance_score": result['relevance_score'],
                "original_index": int(unique_indices[result['index']])
            })
        
        print(f"Search complete. Returning {len(final_results)} final results")
        return final_results
if __name__ == "__main__":
    print("Starting VectorDB example")
    db = VectorDB("path/to/your/multilingual_file.txt")
    results = db.search(["Query 1 here", "Query 2 here", "Query 3 here"], skip_rerank=True)
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"Text: {result['text']}")
        print(f"Relevance Score: {result['relevance_score']}")
        print(f"Original Index: {result['original_index']}")
        print("---")
    print("VectorDB example complete")
