# 🚀 AI-Powered Todo List with LLM Integration

An intelligent task management application that combines natural language processing with modern web technologies. Create, organize, and search tasks using conversational AI and semantic search capabilities.

## 🌐 Live Demo

- **Frontend**: [https://todo-llm-project.vercel.app](https://todo-llm-project.vercel.app)
- **Backend API**: [https://raka-1733-todo-llm.hf.space](https://raka-1733-todo-llm.hf.space)

## ✨ Features

### 🤖 AI-Powered Task Management
- **Natural Language Processing**: Create tasks using conversational prompts
- **Smart Task Parsing**: Automatically extracts priorities, categories, and due dates
- **Semantic Search**: Find tasks based on meaning, not just keywords
- **LLM Integration**: Powered by Groq API for intelligent task interpretation

### 📋 Core Functionality
- User authentication (Register/Login with JWT)
- Create, read, update, and delete tasks
- Task categorization (Work, Personal, Shopping, Health, Other)
- Priority levels (High, Medium, Low)
- Due date management with reminders
- Task status tracking (Pending, In Progress, Completed)
- Vector-based semantic search using FAISS

### 🎨 User Experience
- Clean, responsive UI with dark mode support
- Real-time task updates
- Toast notifications for user actions
- Intuitive task filtering and sorting

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI library
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **React Hot Toast** - Notification system
- **Deployed on**: Vercel

### Backend
- **FastAPI** - High-performance Python web framework
- **Uvicorn** - ASGI server
- **Groq API** - LLM integration
- **FAISS** - Vector similarity search
- **Sentence Transformers** - Text embeddings
- **JWT** - Authentication tokens
- **Passlib/Bcrypt** - Password hashing
- **Deployed on**: Hugging Face Spaces

  


## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Groq API key

### Frontend Setup

Navigate to frontend directory
cd frontend

Install dependencies
npm install

Create .env file
echo "VITE_API_URL=http://127.0.0.1:8000" > .env

Start development server
npm run dev


Frontend will be available at `http://localhost:5173`

### Backend Setup

Navigate to backend directory
cd backend

Create virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_for_jwt
EOF

Start the server
uvicorn app.main:app --reload

Backend will be available at `http://127.0.0.1:8000`

## 🔑 Environment Variables

### Frontend (.env)
VITE_API_URL=http://127.0.0.1:8000

### Backend (.env)
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_jwt_secret_key


## 📦 Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Import project on Vercel
3. Set root directory to `frontend`
4. Deploy

### Backend (Hugging Face Spaces)

1. Create a new Space on Hugging Face
2. Connect your GitHub repository
3. Add Secrets in Space settings:
   - `GROQ_API_KEY`
   - `SECRET_KEY`
4. Space will auto-deploy

## 🎯 Usage Examples

### Creating Tasks
"Add a task: Buy groceries"
"Create high priority task: Finish project report, due tomorrow"
"Add to work category: Team meeting at 3 PM"


## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Protected API routes
- CORS configuration for secure cross-origin requests
- Environment-based secrets management

## 🐛 Known Issues & Solutions

### Bcrypt Compatibility
If you encounter `bcrypt version error`, ensure:
passlib==1.7.4
bcrypt==4.0.1

### CORS Issues
Backend CORS is configured for:
- `http://localhost:5173` (local development)
- `https://todo-llm-project.vercel.app` (production)

## 📈 Future Enhancements

- [ ] Persistent database (PostgreSQL/MongoDB)
- [ ] Real-time collaboration
- [ ] Mobile app (React Native)
- [ ] Voice input for task creation
- [ ] Calendar integration
- [ ] Task analytics dashboard
- [ ] Email/SMS reminders
- [ ] Task sharing and collaboration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Rupankar Mondal
- GitHub: [@rupankar-1733]([https://github.com/your-username](https://github.com/rupankar-1733))
- LinkedIn: [Rupankar Mondal]([https://linkedin.com/in/your-profile](https://www.linkedin.com/in/rupankar-mondal-931bbb259/))

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for LLM API
- [Hugging Face](https://huggingface.co/) for deployment platform
- [Vercel](https://vercel.com/) for frontend hosting
- [FastAPI](https://fastapi.tiangolo.com/) for backend framework

---

⭐ If you found this project helpful, please consider giving it a star!
How to add this to your repository:
1. Create/replace README.md in your project root:
cd ~/newTry/todo_llm_project
nano README.md  # or use any text editor
# Paste the content above
2. Commit and push:
   git add README.md
git commit -m "docs: Add comprehensive README with deployment info"
git push

## 📁 Project Structure
todo_llm_project/
├── frontend/ # React frontend
│ ├── src/
│ │ ├── App.jsx # Main application component
│ │ ├── main.jsx # Entry point
│ │ └── index.css # Global styles
│ ├── package.json
│ └── vite.config.js
│
├── backend/ # FastAPI backend
│ ├── app/
│ │ ├── main.py # FastAPI application
│ │ ├── auth.py # Authentication utilities
│ │ ├── models.py # Pydantic models
│ │ ├── storage.py # Data storage
│ │ ├── vector_db.py # FAISS vector database
│ │ └── mcp_server.py # MCP tool registration
│ └── requirements.txt
│
└── README.md
