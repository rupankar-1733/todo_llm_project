# ��� Todo LLM - AI-Powered Task Management

> An intelligent todo list application powered by Groq's Llama 3 70B, featuring natural language task creation, semantic search with FAISS vector database, and modern glassmorphism UI design.

[![Live Demo](https://img.shields.io/badge/demo-live-success.svg)](https://todo-llm-frontend.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)

---

## ✨ Features

- ��� **AI Chat Interface** - Create tasks using natural language with Groq LLM
- �� **Semantic Search** - Find tasks intelligently using FAISS vector similarity search
- ��� **Modern UI** - Beautiful glassmorphism design with smooth animations
- ��� **Dark Mode** - Eye-friendly dark theme with persistent preferences
- ��� **Task Analytics** - Real-time statistics and insights dashboard
- ⚠️ **Smart Alerts** - Automatic overdue and due-soon notifications
- ���️ **Categories & Priorities** - Organize tasks with 9 categories and 4 priority levels
- ��� **Secure Authentication** - JWT-based user authentication system
- ��� **Fully Responsive** - Seamless experience across desktop, tablet, and mobile
- ��� **Real-time Updates** - Instant task status changes and notifications

---

## ��� Demo

��� **Live Demo:** Coming Soon!

### Demo Credentials

Username: demo
Password: demo123


> **Note:** Free tier deployment may take ~30 seconds to wake up if idle.

---

## ���️ Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance Python web framework
- **[Groq](https://groq.com/)** - Llama 3 70B with function calling capabilities
- **[FAISS](https://github.com/facebookresearch/faiss)** - Facebook AI Similarity Search for vector operations
- **[MCP](https://modelcontextprotocol.io/)** - Model Context Protocol for tool integration
- **[JWT](https://jwt.io/)** - JSON Web Tokens for secure authentication
- **Python 3.10+** - Modern Python features

### Frontend
- **[React 18](https://react.dev/)** - Modern UI library with hooks
- **[Vite](https://vitejs.dev/)** - Lightning-fast build tool
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[React Hot Toast](https://react-hot-toast.com/)** - Beautiful toast notifications

---

## ��� Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Groq API Key ([Get one free](https://console.groq.com/))

### Backend Setup


Clone the repository
git clone https://github.com/rupankar-1733/todo_llm_project.git
cd todo_llm_project/backend

Create virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Configure environment variables
cp .env.example .env

Edit .env and add your GROQ_API_KEY
Generate a secret key for JWT
python -c "import secrets; print(secrets.token_urlsafe(32))"

Add the output to SECRET_KEY in .env
Start the backend server
uvicorn app.main:app --reload


Backend will run at: `http://127.0.0.1:8000`

### Frontend Setup

Navigate to frontend directory
cd ../frontend

Install dependencies
npm install

Start development server
npm run dev


Frontend will run at: `http://localhost:5173`

---

## ��� Usage Examples

### Creating Tasks with Natural Language

Simply type in the chat interface:

"Create a high priority work task to finish project documentation by tomorrow"
"Add a personal reminder to call dentist at 3 PM"
"Schedule a team meeting next Friday at 10 AM"
"Buy groceries this weekend - milk, eggs, bread"


The AI will automatically:
- ✅ Extract task title and description
- ✅ Identify category (work, personal, shopping, etc.)
- ✅ Set priority level (low, medium, high, urgent)
- ✅ Parse due dates from natural language
- ✅ Create the task with proper formatting

### Smart Search

Use semantic search to find tasks:
- `"Find all urgent work items"`
- `"Show me tasks due this week"`
- `"What do I need to buy?"`
- `"Meetings scheduled for next month"`

---

## ��� Project Structure

todo_llm_project/
├── backend/ # FastAPI Backend
│ ├── app/
│ │ ├── init.py
│ │ ├── main.py # API endpoints & routes
│ │ ├── auth.py # Authentication logic
│ │ ├── llm_service.py # Groq LLM integration
│ │ ├── mcp_server.py # MCP tools & functions
│ │ ├── vector_db.py # FAISS operations
│ │ ├── storage.py # Data persistence
│ │ └── models.py # Pydantic models
│ ├── .env.example # Environment template
│ └── requirements.txt # Python dependencies
│
├── frontend/ # React Frontend
│ ├── src/
│ │ ├── App.jsx # Main application component
│ │ ├── main.jsx # React entry point
│ │ └── index.css # Tailwind styles
│ ├── public/ # Static assets
│ ├── package.json # Node dependencies
│ ├── vite.config.js # Vite configuration
│ └── tailwind.config.js # Tailwind configuration
│
├── data/ # Local storage (not in git)
│ ├── tasks.json
│ └── users.json
│
├── .gitignore # Git ignore rules
└── README.md # Documentation


---

## ��� Environment Variables

### Backend (`backend/.env`)

Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200


**Get your Groq API key:** https://console.groq.com/keys

**Generate SECRET_KEY:**
python -c "import secrets; print(secrets.token_urlsafe(32))"


### Frontend (`frontend/.env`)

Backend API URL
VITE_API_URL=http://127.0.0.1:8000


---

## ���️ Architecture

┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ │ │ │ │ │
│ React Frontend │◄───────►│ FastAPI Backend │◄───────►│ Groq LLM API │
│ (Vite + React) │ REST │ (Python 3.10+) │ HTTP │ (Llama 3 70B) │
│ │ │ │ │ │
└─────────────────┘ └──────────────────┘ └─────────────────┘
│
│
┌────────▼─────────┐
│ │
│ FAISS Vector DB │
│ (Semantic Search)│
│ │
└──────────────────┘


**Request Flow:**
1. User types natural language in chat
2. Frontend sends request to FastAPI backend
3. Backend uses Groq LLM to parse intent
4. LLM calls MCP tools (create_task, search_tasks, etc.)
5. Vector embeddings stored in FAISS for semantic search
6. Response returned to frontend with task data
7. UI updates with smooth animations

---

## ��� Key Features Explained

### AI-Powered Task Creation

The app uses **Groq's Llama 3 70B model** with function calling to:
- Parse natural language input
- Extract task details (title, description, due date)
- Classify category and priority automatically
- Handle complex date expressions ("tomorrow", "next Friday", "in 3 days")

### Semantic Search with FAISS

Traditional keyword search vs. our semantic search:

❌ **Keyword Search:** `"urgent tasks"` → only finds tasks with word "urgent"

✅ **Semantic Search:** `"urgent tasks"` → finds:
- Tasks marked as urgent priority
- Tasks with keywords: critical, important, ASAP
- Tasks due today or overdue
- Tasks with urgent-related context

### Model Context Protocol (MCP)

MCP provides structured tools for the LLM:

tools = [
"create_task", # Create new tasks
"update_task", # Modify existing tasks
"get_tasks", # Retrieve tasks with filters
"search_tasks", # Semantic search
"delete_task", # Remove tasks
"get_user_stats", # Analytics
"get_due_soon" # Alert system
]

---

## ��� Task Categories & Priorities

### Categories (9 total)
- ��� **Work** - Professional tasks and projects
- ��� **Personal** - Personal errands and reminders
- ��� **Shopping** - Shopping lists and purchases
- ❤️ **Health** - Medical appointments and fitness
- ��� **Education** - Learning and courses
- ��� **Finance** - Bills and financial tasks
- ✈️ **Travel** - Trip planning and bookings
- ��� **Home** - Household chores and maintenance
- ��� **Other** - Miscellaneous tasks

### Priority Levels (4 total)
- ��� **Urgent** - Critical, needs immediate attention
- ��� **High** - Important, do soon
- ��� **Medium** - Normal priority
- ⚪ **Low** - Can wait

---

## ��� UI Features

- **Glassmorphism Design** - Modern frosted glass effect
- **Smooth Animations** - Fade-in, slide-in, hover effects
- **Dark Mode** - Persistent theme preference
- **Gradient Backgrounds** - Beautiful purple/indigo gradients
- **Toast Notifications** - Non-intrusive success/error messages
- **Responsive Grid** - Adapts to all screen sizes
- **Loading States** - Clear feedback during operations

---

## ��� Security Features

- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - Bcrypt for secure storage
- **API Key Protection** - Environment variables only
- **CORS Configuration** - Restricted origins
- **Input Validation** - Pydantic models for type safety
- **Secret Scanning** - GitHub protection enabled

---

## ��� API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - Authenticate and get JWT token

### Tasks
- `GET /tasks` - List all tasks with filters
- `POST /tasks` - Create new task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `GET /tasks/search` - Semantic search

### Analytics
- `GET /stats` - User statistics
- `GET /due-soon` - Overdue and upcoming tasks

### AI Chat
- `POST /chat` - Natural language interface

---

## ��� Performance

- **LLM Response Time:** ~1-2 seconds
- **Task Creation:** < 500ms
- **Search Query:** < 100ms
- **Vector Similarity:** < 50ms
- **Frontend Load:** < 1 second

---

## ��� Roadmap

- [x] AI-powered task creation
- [x] Semantic search with FAISS
- [x] Dark mode support
- [x] Task analytics dashboard
- [x] Due date alerts
- [ ] Email notifications
- [ ] Calendar integration (Google, Outlook)
- [ ] Recurring tasks
- [ ] Task attachments
- [ ] Collaboration features
- [ ] Mobile app (React Native)
- [ ] Voice input

---

## ��� Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ��� License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ��� Author

**Rupankar**

- GitHub: [@rupankar-1733](https://github.com/rupankar-1733)
- LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/your-profile)
- Email: your.email@example.com

---

## ��� Acknowledgments

- [Groq](https://groq.com/) for the amazing LLM API
- [Meta AI](https://ai.facebook.com/) for Llama 3
- [Facebook Research](https://github.com/facebookresearch/faiss) for FAISS
- [FastAPI](https://fastapi.tiangolo.com/) community
- [React](https://react.dev/) team
- [Tailwind CSS](https://tailwindcss.com/) team

---

## ��� Support

If you have any questions or issues, please:
1. Check existing [Issues](https://github.com/rupankar-1733/todo_llm_project/issues)
2. Create a new issue with detailed description
3. Contact via email or LinkedIn

---

## ⭐ Show Your Support

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ by Rupankar**

