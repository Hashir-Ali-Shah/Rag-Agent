# RAG.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import os

from DocReader import DocumentReader


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline:
    - Ingest documents
    - Chunk text
    - Store in vector database
    - Run similarity search
    - Provide context retrieval for pipeline wiring
    """

    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 chunk_size: int = 500, chunk_overlap: int = 50):
        # Initialize Hugging Face embeddings
        self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)

        # Setup text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        self.document_reader = DocumentReader()
        self.vectorstore: FAISS | None = None
    
    def read(self, path: str) -> list[str]:
        """Read document from path and return list of text chunks."""
        file_path = os.path.abspath(path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}") 
        # Use DocumentReader to read the file
        self.ingest(self.document_reader.read(file_path))

    def ingest(self, raw_texts: list[str] ,save:bool=False) -> None:
        """Takes list of raw texts, splits into chunks, and stores in FAISS vectorstore."""

        if os.path.exists("faiss_index") and save:
            self.load("faiss_index")

        docs = [Document(page_content=t) for t in raw_texts]
        chunks = self.text_splitter.split_documents(docs)
        if self.vectorstore:
            self.vectorstore.add_documents(chunks)
        else:
            self.vectorstore = FAISS.from_documents(chunks, self.embedding_model)
        if save:
            self.save("faiss_index")

    def save(self, path: str = "faiss_index") -> None:
        """Save FAISS index to disk."""
        if not self.vectorstore:
            raise ValueError("No vectorstore to save. Run ingest() first.")
        self.vectorstore.save_local(path)

    def load(self, path: str = "faiss_index") -> None:
        """Load FAISS index from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"No FAISS index found at {path}")
        self.vectorstore = FAISS.load_local(
            path, self.embedding_model, allow_dangerous_deserialization=True
        )

    def query(self, question: str, k: int = 3, initial_k: int = 20):
        """Run hybrid search with reranking over the vectorstore.
        
        Pipeline:
        1. Vector search to get initial candidates
        2. BM25 search on those candidates
        3. Cross-encoder reranking
        
        Args:
            question: Query string
            k: Final number of results to return
            initial_k: Number of candidates to retrieve initially (should be > k)
        
        Returns:
            List[Document]: List of Document objects with page_content attribute
        """
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Run ingest() or load() first.")
        
        dense_results = self.vectorstore.similarity_search(question, k=initial_k)
        
        if not dense_results:
            return []
     
        texts = [doc.page_content for doc in dense_results]
        tokenized_corpus = [text.split(" ") for text in texts]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = question.split(" ")
        bm25_scores = bm25.get_scores(tokenized_query)
        
        scored_docs = [(doc, score) for doc, score in zip(dense_results, bm25_scores)]

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        bm25_filtered_docs = [doc for doc, _ in scored_docs]
     
        if not hasattr(self, 'reranker'):
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
     
        pairs = [[question, doc.page_content] for doc in bm25_filtered_docs]
        rerank_scores = self.reranker.predict(pairs)
        
       
        reranked_docs = [(doc, score) for doc, score in zip(bm25_filtered_docs, rerank_scores)]
        reranked_docs.sort(key=lambda x: x[1], reverse=True)
        
 
        return [doc for doc, _ in reranked_docs[:k]]

    async def _retrieve_context(self, inputs: dict, k: int = 3) -> dict:
            """For pipeline: takes {'question': str}, injects retrieved context."""
            if not self.vectorstore:
                self.load()
            query = inputs["question"]
            docs = self.query(query, k=k) if self.vectorstore else []
            context = "\n".join(d.page_content for d in docs)
            return {**inputs, "context": context}


if __name__ == "__main__":
    rag = RAGPipeline()
    print("RAG pipeline initialized with HuggingFace embeddings ✅")
    rag.ingest([
        "my name is hashir"

        ])
    rag.save()


