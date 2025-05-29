# EduMate AI 🧠📘

**EduMate AI** is a personalized teaching assistant bot tailored for Year 1 CSE students. It helps students learn Python and other subjects through AI-powered roadmaps, topic explanations, study plans, progress tracking, and assignment management.

---

## 🚀 Overview

- **Purpose**: Deliver personalized educational support, primarily for Python programming.
- **Tech Stack**: Python 3.11, Flask, Gemini 1.5 Flash, Qdrant Cloud, MySQL
- **Target Users**: First-year CSE students

---

## 🧩 Features

- Generate personalized learning roadmaps (e.g., Python phases)
- Explain key topics with examples (e.g., loops, data types)
- Create dynamic study plans based on schedule
- Track progress and manage assignments
- Store chat history with `conversation_id` for follow-up context (e.g., "Welcome back!")
- User authentication and data storage via MySQL

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/DigiDARATechnologies/EduMate.git EduMate
cd EduMate
```

### 2. Create .env File
Create a .env file in the root:
```env
GEMINI_API_KEY=your_gemini_api_key  ## enter your API key
QDRANT_URL=https://bb433c34-ebbf-4efb-ac53-6299a6e83718.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key  ## enter your API key
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user  ## enter your MySQL user name
MYSQL_PASSWORD=your_mysql_password ## enter your MySQL Password
MYSQL_DATABASE=edumate
```

### 3. MySQL Database Setup
Install MySQL from: https://dev.mysql.com/downloads/
```sql
CREATE DATABASE edumate;
USE edumate;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50),
    year INT,
    department VARCHAR(50)
);
```

### 4. Create Virtual Environment & Install Requirements
```sh
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5. Verify Qdrant Connection
```sh
curl -X GET "https://bb433c34-ebbf-4efb-ac53-6299a6e83718.us-east4-0.gcp.cloud.qdrant.io:6333/collections/edu_mate_chats" -H "api-key: your_qdrant_api_key"
```

## 🧪 Usage & Testing
### Start the App
```bash
python -m src.main
```

### Test Examples
#### Roadmap:
"Generate a roadmap for Python"
➝ Follow-up: "Have you started Phase 1: Getting Started (Weeks 1-2)?"

#### Explanation:
"Explain Python loops"
➝ Output: for and while loop examples

#### Study Plan:
"Create a study plan for 2 hours daily, exam on 2025-06-01, subjects Python"

#### Follow-Up After Re-Login:
"Hi"
➝ Output: "Welcome back! Last time, we were working on your Python roadmap..."

## 📇 Contact
For questions or support, contact:
Digidaratechnologies@gmail.com
