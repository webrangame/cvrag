# RAG Application with LangChain, Google Gemini, and MySQL

A complete Retrieval-Augmented Generation (RAG) application built with Docker, featuring:
- **LangChain** for RAG orchestration
- **Google Gemini** as the LLM
- **ChromaDB** for vector storage
- **MySQL** for metadata and chat history
- **Streamlit** for the web interface

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Gemini API key (already configured in docker-compose.yml)

### Running the Application

1. **Start the application:**
```bash
docker-compose up -d
```

2. **Access the application:**
   - Open your browser and go to: `http://localhost:8001`
   - The MySQL database will be accessible on port 3306

3. **Stop the application:**
```bash
docker-compose down
```

## 📝 Usage

### Uploading Documents

1. Use the sidebar to upload a PDF or TXT document
2. Click "Process and Store Document"
3. The document will be:
   - Split into chunks
   - Embedded using Google's embedding model
   - Stored in ChromaDB
   - Metadata saved to MySQL

### Querying Documents

1. Enter your question in the chat interface
2. The system will:
   - Retrieve relevant document chunks
   - Use Gemini to generate a response based on the context
   - Store the conversation in MySQL
3. Click "Show chat history" to view past conversations

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   Streamlit │────▶│   LangChain  │────▶│   Gemini   │
│     UI      │     │  (RAG Chain) │     │     LLM    │
└─────────────┘     └──────────────┘     └────────────┘
                            │
                            ├─────────────▶ ChromaDB (Embeddings)
                            │
                            └─────────────▶ MySQL (Metadata & History)
```

## 🔧 Configuration

### Environment Variables

Edit `docker-compose.yml` to configure:

- **GEMINI_API_KEY**: Your Gemini API key
- **MYSQL credentials**: Database connection details
- **Ports**: Default 8001 for app (mapped to 8000 in container), 3306 for MySQL

## 📂 Project Structure

```
.
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # App container definition
├── requirements.txt     # Python dependencies
├── init.sql            # Database initialization
├── app.py              # Main application
├── documents/          # Sample documents directory
│   └── sample.txt
├── chroma_db/          # Vector database (auto-created)
└── data/              # Application data
```

## 🗄️ Database Schema

### Documents Table
Stores document metadata and content chunks.

### Embeddings Table
Stores vector embeddings and related metadata.

### Chat History Table
Stores user queries and AI responses for history.

## 🛠️ Development

### Running Locally (Without Docker)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MySQL (or use remote database)

3. Set environment variables:
```bash
export GEMINI_API_KEY="your-key"
export MYSQL_HOST="localhost"
export MYSQL_USER="rag_user"
export MYSQL_PASSWORD="rag_password"
export MYSQL_DATABASE="rag_db"
```

4. Run the application:
```bash
streamlit run app.py
```

## 📊 Features

- ✅ Document upload (PDF, TXT)
- ✅ Automatic text chunking
- ✅ Vector embeddings with Google's model
- ✅ Semantic search in ChromaDB
- ✅ Context-aware responses with Gemini
- ✅ Chat history in MySQL
- ✅ Source document citations
- ✅ Web-based UI with Streamlit

## 🔒 Security Notes

- The Gemini API key is currently hardcoded in docker-compose.yml for convenience
- For production, use Docker secrets or environment variables
- Never commit API keys to version control

## 📚 Dependencies

- langchain: RAG pipeline orchestration
- langchain-google-genai: Gemini integration
- chromadb: Vector database
- mysql-connector-python: MySQL connectivity
- streamlit: Web interface
- PyPDF2: PDF processing

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

