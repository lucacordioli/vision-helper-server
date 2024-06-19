import fitz
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Knowledge:
    def __init__(self, path="/Users/lucacordioli/Documents/Lavori/polimi/TESI/visionHelperSrv/data"):
        self.huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.chroma_client = chromadb.PersistentClient(path=path)
        collections = self.chroma_client.list_collections()
        if "knowledge_collection" in [collection.name for collection in collections]:
            self.knowledge_collection = self.chroma_client.get_collection(name="knowledge_collection")
        else:
            self.knowledge_collection = self.chroma_client.create_collection(name="knowledge_collection",
                                                                             embedding_function=self.huggingface_ef)

    def add_pdf(self, pdf_path, pdf_id):
        try:
            doc = fitz.open(pdf_path)
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=150, chunk_overlap=20)
            for i in range(len(doc)):
                page = doc.load_page(i)
                page_text = page.get_text()
                doc_splits = text_splitter.split_text(page_text)
                self.knowledge_collection.add(
                    documents=doc_splits,
                    metadatas=[{'page': i + 1, 'source': pdf_id} for _ in doc_splits],
                    ids=[f"id_{pdf_id}_{i}_{j}" for j in range(len(doc_splits))]
                )
        except Exception as e:
            print(f"An error occurred while processing the PDF: {e}")

    def delete_item(self, item_id):
        try:
            all_docs = self.knowledge_collection.get()
            ids_to_del = []
            for idx in range(len(all_docs['ids'])):
                doc_id = all_docs['ids'][idx]
                metadata = all_docs['metadatas'][idx]
                if metadata['source'] == item_id:
                    ids_to_del.append(doc_id)
            if len(ids_to_del) > 0:
                self.knowledge_collection.delete(ids_to_del)
            else:
                print(f"No documents found with source ID: {item_id}")
        except Exception as e:
            print(f"An error occurred while deleting the item: {e}")

    def get_all_documents(self):
        res = self.knowledge_collection.get()
        sources = set([metadata['source'] for metadata in res['metadatas']])
        return sources

    def query(self, query_string, n_results=3):
        results = self.knowledge_collection.query(
            query_texts=[query_string],
            n_results=n_results,
            include=["documents", "metadatas"]
        )
        return results

    def create_elements_collection(self, elements):
        collections = self.chroma_client.list_collections()
        if "elements_collection" in [collection.name for collection in collections]:
            self.chroma_client.delete_collection(name="elements_collection")
        elements_collection = self.chroma_client.create_collection(name="elements_collection",
                                                                   embedding_function=self.huggingface_ef)
        for obj in elements:
            elements_collection.add(
                documents=[str(obj)],
                metadatas=[{"source": "json"}],
                ids=[f"id_{obj['id']}"]
            )

    def query_elements_collection(self, query_string, n_results=3):
        collections = self.chroma_client.list_collections()
        if "elements_collection" in [collection.name for collection in collections]:
            elements_collection = self.chroma_client.get_collection(name="elements_collection")
        else:
            return
        results = elements_collection.query(
            query_texts=[query_string],
            n_results=n_results,
            include=["documents", "metadatas"]
        )
        return results
