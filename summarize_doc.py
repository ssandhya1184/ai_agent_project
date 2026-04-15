from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import warnings
warnings.filterwarnings("ignore")
import os



def summarize(doc_path):
    print("Inside summrize")
    load_dotenv() 
    
    # 1. Load PDF    
    loader = PyPDFLoader(doc_path)
    documents = loader.load()
    for i, doc in enumerate(documents):
        print(f"Page {i} content length:", len(doc.page_content or ""))

    # 2. Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    docs = text_splitter.split_documents(documents)
    print("Loaded documents:", len(documents))
    print("After split:", len(docs))
    if not docs:
        raise ValueError("No text could be extracted from the PDF")
    
    # 3. Create embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    print("embeddings->",embeddings)

    # 4. Create FAISS vector store
    try:
        vectorstore = FAISS.from_documents(docs, embeddings)
        print("vectorstore->",vectorstore)
    except Exception as e:
        print("Embedding failed:", str(e))
        raise
    
    # 5. Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k":4})
    print("retriever->",retriever)

    # 6. Load local LLM   
    model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    # 7. Prompt template
    prompt = ChatPromptTemplate.from_template("""
    You are a helpful assistant.

    Use the context below to generate a clear summary.

    Context:
    {context}

    Provide a concise summary of the document.
    """)

    # 8. Format retrieved documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 9. LCEL pipeline
    chain = (
        {"context": retriever | format_docs}
        | prompt
        | model
        | StrOutputParser()
    )
    
    # 10. Run summarization
    summary = chain.invoke("Summarize the PDF")

    print("\nPDF SUMMARY:\n",summary)
    
    return summary

