import os
import logging
from .tools.rag import VectorDB

class KnowledgeManager:
    def __init__(self, app, knowledge_files=None):
        self.app = app
        self.rag = None
        self.initialize_knowledge_base(knowledge_files)

    def initialize_knowledge_base(self, knowledge_files):
        with self.app.app_context():
            if knowledge_files is None:
                uploads_dir = os.path.join(self.app.config['BOT_DIRECTORY'], 'uploads')
                knowledge_files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) 
                                   if os.path.isfile(os.path.join(uploads_dir, f))]
            
            if not isinstance(knowledge_files, list):
                knowledge_files = [knowledge_files]
            
            print(f"Initializing knowledge base with files: {knowledge_files}")
            
            valid_files = [f for f in knowledge_files if os.path.exists(f)]
            
            if valid_files:
                try:
                    self.rag = VectorDB(valid_files)
                    print(f"Successfully created VectorDB instance with {len(valid_files)} file(s)")
                except Exception as e:
                    print(f"Error initializing VectorDB: {str(e)}")
                    self.app.logger.error(f"Error initializing VectorDB: {str(e)}")
            else:
                print("No valid knowledge files found. VectorDB not initialized.")

    def get_knowledge(self, queries):
        print(f"Getting knowledge for queries: {queries}")
        if self.rag:
            try:
                results = self.rag.search(queries)
                print(f"Search results: {results}")
                if not results:
                    print("No results found in knowledge base")
                    return ["No relevant information found in the knowledge base."]
                return [result['text'] for result in results]
            except Exception as e:
                print(f"Error retrieving knowledge: {str(e)}")
                return [f"Error retrieving knowledge: {str(e)}"]
        else:
            print("RAG not initialized, using mock data")
            return [f"Relevant information for '{query}': chunk {i}" for i, query in enumerate(queries, 1)]

    def append_knowledge(self, file_path):
        print(f"appending file: {file_path}")
        try:
            logging.info(f"Attempting to append knowledge from file: {file_path}")
            
            self.rag = VectorDB(file_path)
            logging.info(f"Successfully created VectorDB instance with file: {file_path}")
            return f"Knowledge from {file_path} has been successfully appended."
        except Exception as e:
            logging.error(f"Error appending knowledge: {str(e)}")
            raise