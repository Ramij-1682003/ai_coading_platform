# 🚀 AI Coding Interview Platform

An AI-powered coding interview platform that allows users to write, run, and evaluate code in multiple programming languages with real-time feedback and automated test case validation.

---

## ✨ Features

* 🧠 AI-generated feedback on code (OpenAI API)
* 💻 Multi-language support:

  * Python
  * C
  * C++
  * Java
  * JavaScript
* ⚡ Real-time code execution
* ✅ Automated test case validation
* 📊 Execution time tracking
* 📝 Submission history tracking
* 🎯 Interview-style problem solving environment

---

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **Frontend:** HTML, CSS, JavaScript
* **Execution Engine:** Subprocess
* **AI Integration:** OpenAI API

---

## 📂 Project Structure

```
Backend/
│── main.py
│── requirements.txt
│
Frontend/
│── index.html
│── script.js
│── styles.css
```

---

## ⚙️ How to Run Locally

### 1. Clone the repository

```
git clone https://github.com/Ramij-1682003/ai-coding-platform.git
cd ai-coding-platform
```

### 2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Set API Key

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

### 5. Run backend

```
uvicorn main:app --reload
```

### 6. Open frontend

Open `index.html` in browser

---

## 🧠 How It Works

1. User writes code in the editor
2. Code is sent to FastAPI backend
3. Backend:

   * Compiles (if needed)
   * Executes code
   * Compares output with expected results
4. Returns:

   * Status (Accepted / Wrong Answer / Error)
   * Execution time
   * AI-generated feedback

---

## 🔒 Security Note

* Unsafe keywords are blocked
* Infinite loops are restricted using timeout
* Execution is controlled using subprocess

---

## 🚀 Future Improvements

* 🐳 Docker sandbox for secure execution
* 🔐 User authentication system
* 🌐 Online deployment
* 📈 Performance analytics dashboard
* 🧠 Advanced AI feedback (optimized solutions)

---
## 🌐 Live Demo
Frontend: https://your-netlify-link.netlify.app  
Backend: https://ai-coading-platform.onrender.com

## ⭐ If you like this project

Give it a ⭐ on GitHub!
