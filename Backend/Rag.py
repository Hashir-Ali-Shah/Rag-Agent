# RAG.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
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
            chunk_overlap=chunk_overlap
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

    def ingest(self, raw_texts: list[str]) -> None:
        """Takes list of raw texts, splits into chunks, and stores in FAISS vectorstore."""

        if os.path.exists("faiss_index") and not self.vectorstore:
            self.load("faiss_index")

        docs = [Document(page_content=t) for t in raw_texts]
        chunks = self.text_splitter.split_documents(docs)
        if self.vectorstore:
            self.vectorstore.add_documents(chunks)
        else:
            self.vectorstore = FAISS.from_documents(chunks, self.embedding_model)
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

    def query(self, question: str, k: int = 3):
        """Run similarity search over the vectorstore."""
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Run ingest() or load() first.")
        return self.vectorstore.similarity_search(question, k=k)

    def _retrieve_context(self, inputs: dict, k: int = 3) -> dict:
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
        "LangChain is a framework for developing applications powered by language models.",
        "It provides modular components for building LLM applications.",
        "You can use it to create chatbots, question-answering systems, and more."
        ])
    rag.save()


