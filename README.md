# AI CSV Agent 🚀

An AI-powered agent built with **FastAPI**, **LangChain**, **Postgres + pgvector**, and **OpenAI**,
designed to answer questions strictly based on a predefined dataset (`data/data.txt`).

This project is structured with a focus on **professionalism, scalability, and maintainability**,
featuring clean architecture, centralized logging, consistent error handling, and typed schemas.

---

## 📂 Project Structure

```
ai-csv-agent/
├── app/
│   ├── config/              # Environment configuration
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API routes (agent, health, logs)
│   ├── schemas/             # Pydantic schemas for requests/responses
│   ├── services/            # Business logic services (e.g., logs persistence)
│   └── utils/               # Utilities (db, logger, error handler, vectorstore, llm)
├── data/                    # Dataset folder
│   └── data.txt             # Knowledge base for embeddings
├── Dockerfile               # Docker build file
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Requirements

- Python **3.11+**
- PostgreSQL with **pgvector** extension
- [OpenAI API Key](https://platform.openai.com/)
- (Optional) Docker + Docker Compose

---

## 🚀 Local Setup

1. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/jorgechavarriaga/ai-csv-agent.git
   cd ai-csv-agent
   python -m venv .venv-ai-agent
   source .venv-ai-agent/bin/activate   # Linux/Mac
   .venv-ai-agent\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:

   ```env
   POSTGRES_USER=ai_user
   POSTGRES_PASSWORD=super_secret
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=ai_agent
   
   OPENAI_API_KEY=sk-xxxx
   ```

3. Load your dataset into:

   ```
   data/data.txt
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🛠️ API Endpoints

### 1. Health Check

**GET** `/api/v1/status`  
Verifies the API is alive.

✅ Example response:

```json
{
  "status": "success",
  "data": {
    "status": "ok"
  }
}
```

---

### 2. Ask Agent

**POST** `/api/v1/ask`  
Send a question to the AI Agent.

📩 Request body:

```json
{
  "question": "What is Jorge's professional background?"
}
```

✅ Example response:

```json
{
  "status": "success",
  "data": {
    "question": "What is Jorge's professional background?",
    "answer": "Jorge's professional background includes roles as a Full Stack Developer, Security Engineer, Logistic Manager, and Mechanical Engineer."
  }
}
```

---

### 3. Logs

**GET** `/api/v1/logs?limit=50`  
Retrieve the most recent interaction logs.

✅ Example response:

```json
{
  "status": "success",
  "data": {
    "logs": [
      {
        "id": 1,
        "question": "What is Jorge's professional background?",
        "answer": "Full Stack Developer...",
        "created_at": "2025-09-10T14:30:35.863554"
      }
    ]
  }
}
```

---

## ⚠️ Error Handling

All error responses follow a **standard JSON format**:

```json
{
  "status": "error",
  "error": {
    "code": 404,
    "message": "Endpoint not found"
  }
}
```

### Handled errors include:

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `405 Method Not Allowed`
- `413 Payload Too Large`
- `422 Validation Failed`
- `429 Too Many Requests`
- `500 Unexpected Error`
- `503 Vector store not available`
- `504 Gateway Timeout`

---

## 📝 Roadmap

- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

---

## 👨‍💻 Author

Developed by **Jorge Chavarriaga**  
📍 Canada | Full Stack Developer  
🔗 [LinkedIn](https://www.linkedin.com/in/jorge-chava/) | [GitHub](https://github.com/jorgechavarriaga/)
