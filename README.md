# 🤖 Restaurant Customer Support AI Agent

An intelligent, autonomous AI agent backend built for the food and hospitality industry. Unlike traditional rule-based chatbots, this system leverages Large Language Models (LLMs) with **Agentic Function Calling** to dynamically take orders, book tables, and modify cart details by autonomously interacting with a SQL database.

## 🚀 Key Features

* **Agentic Tool Calling:** Powered by Llama-3, the agent autonomously triggers internal backend functions (`place_order`, `book_table`, `cancel_order`, `modify_order`) when the user provides complete necessary information.
* **Conversational Order Flow:** Intelligently extracts user details (Name, Phone, Address) in natural language before processing transactions.
* **Real-time Database Integration:** Connected to a SQLAlchemy database to perform live menu checks, track order statuses, and manage table reservations securely.
* **Dynamic Memory Management:** Maintains a sliding context window of recent chat history to keep token usage optimized without losing conversation context.
* **Robust Error Handling:** Strict system prompting and parameter casting to ensure accurate JSON payloads and prevent tool-leakage in the frontend.
* **Payment Processing Logic:** Naturally handles Cash-on-Delivery (COD) agreements and calculates total bills in real-time.

## 🛠️ Tech Stack

* **Language:** Python
* **Framework:** FastAPI
* **LLM Engine:** Llama-3 8B-Instant (via Groq API)
* **Database:** SQLite / SQLAlchemy (ORM)
* **Architecture:** Agentic Function Calling / AI Customer Service

## ⚙️ How to Run Locally

### 1. Clone the repository
```bash
git clone [https://github.com/AsadRiaz045/restaurant-customer-support-ai-agent.git](https://github.com/AsadRiaz045/restaurant-customer-support-ai-agent.git)
cd restaurant-customer-support-ai-agent
2. Create a virtual environment & install dependencies
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

pip install fastapi uvicorn sqlalchemy groq python-dotenv
3. Environment Setup
Create a .env file in the root directory and securely add your API key:
GROQ_API_KEY=your_groq_api_key_here
4. Run the server
uvicorn main:app --reload
The FastAPI backend will start running on http://127.0.0.1:8000. You can test the endpoints via Postman or integrate them with a React/Next.js frontend.
👨‍💻 Author
Asad Riaz

Software Engineer specializing in Python, Agentic AI, and robust backend architectures
