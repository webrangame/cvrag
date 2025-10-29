import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import mysql.connector
from mysql.connector import Error
import time

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBrzQBlC9MIU1MfqDU_hpViZ_qFR9Vggs0')
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'rag_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'rag_password'),
    'database': os.getenv('MYSQL_DATABASE', 'rag_db')
}

# Initialize embeddings - Using free HuggingFace model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7,
    convert_system_message_to_human=True
)

def init_db_connection():
    """Initialize MySQL database connection"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**MYSQL_CONFIG)
            if connection.is_connected():
                print(f"Successfully connected to MySQL database on attempt {attempt + 1}")
                return connection
        except Error as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    return None

def save_to_db(connection, filename, chunks):
    """Save document chunks to MySQL database"""
    try:
        cursor = connection.cursor()
        for i, chunk in enumerate(chunks):
            # Insert document chunk
            insert_query = """
                INSERT INTO documents (filename, title, content, chunk_index)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (filename, filename, chunk.page_content, i))
        connection.commit()
        cursor.close()
        print(f"Saved {len(chunks)} chunks to database")
    except Error as e:
        print(f"Error saving to database: {e}")
        connection.rollback()

def save_chat_history(connection, query, response):
    """Save chat history to MySQL"""
    try:
        cursor = connection.cursor()
        insert_query = "INSERT INTO chat_history (query, response) VALUES (%s, %s)"
        cursor.execute(insert_query, (query, response))
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error saving chat history: {e}")

def get_chat_history(connection, limit=10):
    """Retrieve chat history from MySQL"""
    try:
        cursor = connection.cursor()
        query = "SELECT query, response, created_at FROM chat_history ORDER BY created_at DESC LIMIT %s"
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        cursor.close()
        return results
    except Error as e:
        print(f"Error retrieving chat history: {e}")
        return []

def get_document_count(connection):
    """Get total number of documents in the database"""
    try:
        cursor = connection.cursor()
        query = "SELECT COUNT(DISTINCT filename) as doc_count FROM documents"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0
    except Error as e:
        print(f"Error getting document count: {e}")
        return 0

# Streamlit app
def main():
    st.set_page_config(page_title="RAG Application", page_icon="🤖")
    st.title("🤖 RAG Application")
    
    # Initialize session state
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = init_db_connection()
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📄 Document Management")
        
        uploaded_file = st.file_uploader("Upload a document (PDF or TXT)", type=['pdf', 'txt'])
        
        if uploaded_file is not None:
            file_name = uploaded_file.name
            content = uploaded_file.read()
            
            # Process PDF
            if file_name.endswith('.pdf'):
                import PyPDF2
                from io import BytesIO
                pdf_reader = PyPDF2.PdfReader(BytesIO(content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            else:
                text = content.decode('utf-8')
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.create_documents([text])
            
            if st.button("Process and Store Document"):
                with st.spinner("Processing document..."):
                    try:
                        # Create document objects with metadata
                        documents = [Document(page_content=chunk.page_content, metadata={"source": file_name}) 
                                   for chunk in chunks]
                        
                        # Create vector store
                        if 'vectorstore' not in st.session_state or st.session_state.vectorstore is None:
                            st.session_state.vectorstore = Chroma.from_documents(
                                documents=documents,
                                embedding=embeddings,
                                persist_directory="./chroma_db"
                            )
                        else:
                            # Add to existing vector store
                            st.session_state.vectorstore.add_documents(documents)
                            st.session_state.vectorstore.persist()
                        
                        # Save to MySQL
                        if 'db_connection' in st.session_state and st.session_state.db_connection:
                            save_to_db(st.session_state.db_connection, file_name, chunks)
                        
                        st.success(f"Document processed! {len(chunks)} chunks created.")
                    except Exception as e:
                        st.error(f"Error processing document: {e}")
        
        st.header("📊 Database Status")
        if 'db_connection' in st.session_state and st.session_state.db_connection:
            st.success("✓ MySQL Connected")
            # Display document count
            doc_count = get_document_count(st.session_state.db_connection)
            st.info(f"📄 **Documents stored: {doc_count}**")
        else:
            st.error("✗ MySQL Disconnected")
    
    # Main chat interface
    st.header("💬 Chat with your documents")
    
    # Load vectorstore if not in session
    if 'vectorstore' not in st.session_state or st.session_state.vectorstore is None:
        try:
            st.session_state.vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=embeddings
            )
        except:
            st.session_state.vectorstore = None
    
    if 'vectorstore' not in st.session_state or st.session_state.vectorstore is None:
        st.info("👆 Please upload a document to get started!")
    else:
        # Custom prompt template
        template = """You are a helpful AI assistant. Use the following pieces of context to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Provide a detailed answer:"""
        
        QA_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True
        )
        
        # Chat input
        user_query = st.text_input("Ask a question about your documents:")
        
        if user_query:
            with st.spinner("Thinking..."):
                try:
                    result = qa_chain({"query": user_query})
                    
                    # Display answer
                    st.write("### Answer")
                    st.write(result['result'])
                    
                    # Display source documents
                    with st.expander("View source documents"):
                        for i, doc in enumerate(result['source_documents']):
                            st.write(f"**Source {i+1}:**")
                            st.write(doc.page_content[:500] + "...")
                    
                    # Save to chat history
                    if 'db_connection' in st.session_state and st.session_state.db_connection:
                        save_chat_history(st.session_state.db_connection, user_query, result['result'])
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Display chat history
        if st.checkbox("Show chat history"):
            if 'db_connection' in st.session_state and st.session_state.db_connection:
                history = get_chat_history(st.session_state.db_connection, limit=10)
                for query, response, created_at in reversed(history):
                    with st.expander(f"Q: {query} ({created_at})"):
                        st.write(response)

if __name__ == "__main__":
    main()

