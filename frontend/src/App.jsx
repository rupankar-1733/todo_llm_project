import { useState, useEffect } from "react";
import toast, { Toaster } from "react-hot-toast";
import Chat from "./Chat";

const API = import.meta.env.VITE_API_URL || "https://raka-1733-todo-llm.hf.space";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [loginError, setLoginError] = useState("");
  const [token, setToken] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  const [tasks, setTasks] = useState([]);
  const [displayTasks, setDisplayTasks] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState(null);
  const [dueSoon, setDueSoon] = useState(null);
  const [filterCategory, setFilterCategory] = useState("");
  const [filterPriority, setFilterPriority] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [sortBy, setSortBy] = useState("none");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedToken = localStorage.getItem("todo_token");
    const savedDarkMode = localStorage.getItem("darkMode") === "true";
    setDarkMode(savedDarkMode);
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
    } else {
      setShowLoginModal(true);
    }
  }, []);

  useEffect(() => {
    if (token && isAuthenticated) {
      loadTasks();
      loadStats();
      loadDueSoon();
    }
  }, [token, isAuthenticated]);

  useEffect(() => {
    if (token && tasks.length > 0) loadDueSoon();
  }, [tasks.length]);

  useEffect(() => {
    let filtered = [...tasks];
    if (searchQuery) {
      filtered = filtered.filter(
        (t) =>
          t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    if (sortBy === "due_date") {
      filtered.sort((a, b) => {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date) - new Date(b.due_date);
      });
    } else if (sortBy === "priority") {
      const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
      filtered.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    } else if (sortBy === "created") {
      filtered.sort((a, b) => b.id - a.id);
    }
    setDisplayTasks(filtered);
  }, [tasks, searchQuery, sortBy]);

  // --------- AUTH ---------
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError("");
    setLoading(true);
    try {
      const endpoint = isSignup ? "/register" : "/login";
      const res = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginForm),
      });
      if (!res.ok) {
        let errorMsg = "Authentication failed";
        try {
          const errorData = await res.json();
          errorMsg = errorData.detail || errorMsg;
        } catch {
          errorMsg = await res.text();
        }
        throw new Error(errorMsg);
      }
      const data = await res.json();
      if (isSignup) {
        setIsSignup(false);
        setLoginError("");
        toast.success("Account created! Please login.");
      } else {
        localStorage.setItem("todo_token", data.access_token);
        setToken(data.access_token);
        setIsAuthenticated(true);
        setShowLoginModal(false);
        setLoginForm({ username: "", password: "" });
        toast.success("Welcome back!");
      }
    } catch (e) {
      setLoginError((e && e.message) || "Login failed");
      toast.error((e && e.message) || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("todo_token");
    setToken("");
    setIsAuthenticated(false);
    setTasks([]);
    setStats(null);
    setDueSoon(null);
    setShowLoginModal(true);
    toast.success("Logged out successfully");
  };

  // --------- CHAT AI ---------
  const sendChatMessage = async (userInput) => {
    if (!token) return "You are not logged in.";
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ messages: [{ role: "user", content: userInput }] }),
      });
      if (!res.ok) {
        let error = await res.text();
        return "AI Error: " + error;
      }
      const data = await res.json();
      // Try to refresh tasks after a chat command
      loadTasks();
      return data.reply || data.message || "AI responded, but no text found.";
    } catch (e) {
      return "Connection error: " + (e.message || String(e));
    }
  };

  // --------- TASK REST API ---------
  const loadTasks = async () => {
    if (!token) return;
    try {
      const params = new URLSearchParams();
      if (filterCategory) params.append("category", filterCategory);
      if (filterPriority) params.append("priority", filterPriority);
      if (filterStatus) params.append("status", filterStatus);

      const res = await fetch(`${API}/tasks?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setTasks(data.tasks || []);
    } catch (e) {
      // Optionally: toast.error("Load tasks failed");
    }
  };

  const loadStats = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/stats`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setStats(await res.json());
    } catch (e) {}
  };

  const loadDueSoon = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/due-soon?days=7`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setDueSoon(data);
      }
    } catch (e) {}
  };

  const updateTaskStatus = async (taskId, status) => {
    try {
      const res = await fetch(`${API}/tasks/${taskId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error(await res.text());
      await loadTasks();
      await loadStats();
      await loadDueSoon();
      toast.success(`Task marked as ${status.replace("_", " ")}`);
    } catch (e) {
      toast.error("Failed to update task");
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm("Delete this task?")) return;
    try {
      const res = await fetch(`${API}/tasks/${taskId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(await res.text());
      await loadTasks();
      await loadStats();
      await loadDueSoon();
      toast.success("Task deleted");
    } catch (e) {
      toast.error("Failed to delete task");
    }
  };

  const getPriorityGradient = (priority) => {
    const gradients = {
      urgent: "bg-gradient-to-r from-red-500 to-red-600",
      high: "bg-gradient-to-r from-orange-500 to-orange-600",
      medium: "bg-gradient-to-r from-blue-500 to-blue-600",
      low: "bg-gradient-to-r from-gray-400 to-gray-500",
    };
    return gradients[priority] || gradients.medium;
  };

  const getCategoryEmoji = (category) => {
    const emojis = {
      work: "💼",
      personal: "👤",
      shopping: "🛒",
      health: "❤️",
      education: "📚",
      finance: "💰",
      travel: "✈️",
      home: "🏠",
      other: "📋",
    };
    return emojis[category] || "📋";
  };

  const bgGradient = darkMode
    ? "bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"
    : "bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-600";

  // --------- RENDER ---------
  if (!isAuthenticated) {
    return (
      <div className={`min-h-screen ${bgGradient} flex items-center justify-center p-4`}>
        <Toaster position="top-right" />
        <div className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-2xl p-8 backdrop-blur-lg max-w-md w-full animate-fadeIn">
          <div className="text-center mb-6">
            <div className="bg-gradient-to-br from-yellow-400 to-pink-500 p-3 rounded-xl inline-block mb-3">
              <span className="text-4xl">✨</span>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Todo LLM</h1>
            <p className="text-white text-opacity-90">AI-powered task management</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-white text-sm font-medium mb-2">Username</label>
              <input
                type="text"
                required
                className="w-full bg-white bg-opacity-30 border border-white border-opacity-40 text-white placeholder-white placeholder-opacity-60 rounded-xl px-4 py-3 focus:ring-2 focus:ring-white focus:ring-opacity-50 focus:outline-none transition-all"
                placeholder="Enter username"
                value={loginForm.username}
                onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-white text-sm font-medium mb-2">Password</label>
              <input
                type="password"
                required
                className="w-full bg-white bg-opacity-30 border border-white border-opacity-40 text-white placeholder-white placeholder-opacity-60 rounded-xl px-4 py-3 focus:ring-2 focus:ring-white focus:ring-opacity-50 focus:outline-none transition-all"
                placeholder="Enter password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
              />
            </div>
            {loginError && (
              <div className="p-3 bg-red-500 bg-opacity-30 border border-red-400 border-opacity-50 rounded-xl text-sm text-white">
                {loginError}
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 text-white font-medium hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 transition-all shadow-lg transform hover:scale-105"
            >
              {loading ? "⏳ Please wait..." : isSignup ? "📝 Sign Up" : "🚀 Login"}
            </button>
            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setIsSignup(!isSignup);
                  setLoginError("");
                }}
                className="text-white text-sm hover:underline transition-all"
              >
                {isSignup ? "Already have an account? Login" : "Don't have an account? Sign up"}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${bgGradient} relative`}>
      <Toaster position="top-right" />
      {/* Glass Header */}
      <div className="bg-white bg-opacity-10 border-b border-white border-opacity-20 backdrop-blur-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-yellow-400 to-pink-500 p-2 rounded-xl">
                <span className="text-2xl">✨</span>
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-white">Todo LLM</h1>
                <p className="text-sm text-white text-opacity-90 hidden sm:block">
                  AI-powered task management
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setDarkMode(dm => !dm)}
                className="px-4 py-2 rounded-xl text-sm font-medium bg-white bg-opacity-20 text-white border border-white border-opacity-30 hover:bg-opacity-30 transition-all"
              >
                {darkMode ? "☀️ Light" : "🌙 Dark"}
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-xl text-sm font-medium bg-red-500 bg-opacity-30 text-white border border-red-400 border-opacity-50 hover:bg-opacity-40 transition-all"
              >
                🚪 Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Alerts */}
            {dueSoon && (dueSoon.overdue_count > 0 || dueSoon.due_soon_count > 0) && (
              <div className="bg-gradient-to-br from-yellow-400 to-orange-500 bg-opacity-30 border border-orange-300 border-opacity-50 rounded-2xl p-4 backdrop-blur-md animate-slideIn">
                <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
                  <span className="text-xl">⚠️</span> Alerts
                </h3>
                {dueSoon.overdue_count > 0 && (
                  <p className="text-sm text-white font-medium mb-1">
                    🔴 {dueSoon.overdue_count} overdue
                  </p>
                )}
                {dueSoon.due_soon_count > 0 && (
                  <p className="text-sm text-white font-medium">
                    🟠 {dueSoon.due_soon_count} due soon
                  </p>
                )}
              </div>
            )}
            {/* Stats */}
            {stats && (
              <div className="space-y-3">
                <div className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-2xl p-4 backdrop-blur-md transform transition-all hover:scale-105">
                  <div className="text-4xl font-bold text-white">{stats.total_tasks}</div>
                  <div className="text-sm text-white text-opacity-90">Total Tasks</div>
                </div>
                <div className="bg-gradient-to-br from-green-400 to-emerald-500 bg-opacity-40 border border-green-300 border-opacity-50 rounded-2xl p-4 backdrop-blur-md transform transition-all hover:scale-105">
                  <div className="text-4xl font-bold text-white">{stats.completed}</div>
                  <div className="text-sm text-white text-opacity-90">✓ Completed</div>
                </div>
                <div className="bg-gradient-to-br from-blue-400 to-cyan-500 bg-opacity-40 border border-blue-300 border-opacity-50 rounded-2xl p-4 backdrop-blur-md transform transition-all hover:scale-105">
                  <div className="text-4xl font-bold text-white">{stats.in_progress}</div>
                  <div className="text-sm text-white text-opacity-90">⏳ In Progress</div>
                </div>
                <div className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-2xl p-4 backdrop-blur-md transform transition-all hover:scale-105">
                  <div className="text-4xl font-bold text-white">{stats.pending}</div>
                  <div className="text-sm text-white text-opacity-90">📋 Pending</div>
                </div>
              </div>
            )}
          </div>
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* --- The new Chat UI below replaces the old textarea chat section --- */}
            <div className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-2xl p-6 backdrop-blur-lg animate-fadeIn">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-xl">💬</span> Chat with AI
              </h2>
              <Chat onSend={sendChatMessage} />
            </div>
            {/* --- Rest of your existing dashboard/card design stays the same --- */}
            {/* Search & Sort */}
            <div className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-2xl p-6 backdrop-blur-lg">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    🔍 Search Tasks
                  </label>
                  <input
                    type="text"
                    className="w-full bg-white bg-opacity-30 border border-white border-opacity-40 text-white placeholder-white placeholder-opacity-60 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-white focus:ring-opacity-50 focus:outline-none transition-all"
                    placeholder="Search by title or description..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-white text-sm font-medium mb-2">🔽 Sort By</label>
                  <select
                    className="w-full bg-white bg-opacity-30 border border-white border-opacity-40 text-white rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-white focus:ring-opacity-50 focus:outline-none transition-all"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="none" className="text-gray-900">
                      No sorting
                    </option>
                    <option value="due_date" className="text-gray-900">
                      Due Date
                    </option>
                    <option value="priority" className="text-gray-900">
                      Priority
                    </option>
                    <option value="created" className="text-gray-900">
                      Recently Created
                    </option>
                  </select>
                </div>
              </div>
            </div>
            {/* Filters */}
            <div className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-2xl p-6 backdrop-blur-lg">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-xl">🔍</span> Filters
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
                <select
                  className="bg-white bg-opacity-30 border border-white border-opacity-40 text-white rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-white focus:ring-opacity-50 focus:outline-none backdrop-blur-sm transition-all"
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                >
                  <option value="" className="text-gray-900">
                    All Categories
                  </option>
                  <option value="work" className="text-gray-900">
                    💼 Work
                  </option>
                  <option value="personal" className="text-gray-900">
                    👤 Personal
                  </option>
                  <option value="shopping" className="text-gray-900">
                    🛒 Shopping
                  </option>
                  <option value="health" className="text-gray-900">
                    ❤️ Health
                  </option>
                  <option value="other" className="text-gray-900">
                    📋 Other
                  </option>
                </select>
                <select
                  className="bg-white bg-opacity-30 border border-white border-opacity-40 text-white rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-white focus:ring-opacity-50 focus:outline-none backdrop-blur-sm transition-all"
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                >
                  <option value="" className="text-gray-900">
                    All Priorities
                  </option>
                  <option value="urgent" className="text-gray-900">
                    🔴 Urgent
                  </option>
                  <option value="high" className="text-gray-900">
                    🟠 High
                  </option>
                  <option value="medium" className="text-gray-900">
                    🔵 Medium
                  </option>
                  <option value="low" className="text-gray-900">
                    ⚪ Low
                  </option>
                </select>
                <select
                  className="bg-white bg-opacity-30 border border-white border-opacity-40 text-white rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-white focus:ring-opacity-50 focus:outline-none backdrop-blur-sm transition-all"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="" className="text-gray-900">
                    All Status
                  </option>
                  <option value="pending" className="text-gray-900">
                    📋 Pending
                  </option>
                  <option value="in_progress" className="text-gray-900">
                    ⏳ In Progress
                  </option>
                  <option value="completed" className="text-gray-900">
                    ✅ Completed
                  </option>
                </select>
              </div>
              <button
                onClick={loadTasks}
                className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium hover:from-indigo-600 hover:to-purple-700 transition-all shadow-lg transform hover:scale-105"
              >
                Apply Filters
              </button>
            </div>
            {/* Tasks */}
            <div className="bg-white bg-opacity-20 border border-white border-opacity-30 rounded-2xl p-6 backdrop-blur-lg">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-xl">📝</span> Tasks ({displayTasks.length})
              </h2>
              {displayTasks.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📭</div>
                  <p className="text-white text-opacity-90 font-medium">
                    No tasks found. Create one using chat!
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {displayTasks.map((t, idx) => (
                    <div
                      key={t.id}
                      className="bg-white rounded-xl p-4 shadow-lg hover:shadow-2xl transition-all hover:scale-105 animate-slideIn"
                      style={{ animationDelay: `${idx * 0.1}s` }}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2 flex-wrap">
                            <span className="text-2xl">{getCategoryEmoji(t.category)}</span>
                            <h3 className="font-bold text-gray-900 text-lg">{t.title}</h3>
                            <span
                              className={`text-xs px-3 py-1 rounded-full text-white font-medium ${getPriorityGradient(
                                t.priority
                              )}`}
                            >
                              {t.priority.toUpperCase()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 mb-3">{t.description}</p>
                          <div className="flex flex-wrap gap-2 text-xs">
                            <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full font-medium">
                              {t.category}
                            </span>
                            <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
                              {t.status.replace("_", " ")}
                            </span>
                            {t.due_date && (
                              <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full font-medium">
                                📅 {t.due_date}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex sm:flex-col gap-2">
                          {t.status !== "in_progress" && t.status !== "completed" && (
                            <button
                              onClick={() => updateTaskStatus(t.id, "in_progress")}
                              className="flex-1 sm:flex-none text-xs px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 font-medium shadow-md whitespace-nowrap transition-all transform hover:scale-110"
                            >
                              ▶️ Start
                            </button>
                          )}
                          {t.status !== "completed" && (
                            <button
                              onClick={() => updateTaskStatus(t.id, "completed")}
                              className="flex-1 sm:flex-none text-xs px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 font-medium shadow-md whitespace-nowrap transition-all transform hover:scale-110"
                            >
                              ✓ Done
                            </button>
                          )}
                          <button
                            onClick={() => deleteTask(t.id)}
                            className="flex-1 sm:flex-none text-xs px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg hover:from-red-600 hover:to-pink-600 font-medium shadow-md whitespace-nowrap transition-all transform hover:scale-110"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        {/* Footer */}
        <div className="mt-8 text-center text-sm text-white text-opacity-80 pb-4">
          <p>Built with FastAPI · React · Groq LLM · FAISS Vector DB</p>
        </div>
      </div>
    </div>
  );
}
