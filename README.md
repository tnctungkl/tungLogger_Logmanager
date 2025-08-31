# TungLogger — Pro Log Manager

TungLogger is a **desktop log management tool** that combines; a **modern Tkinter/ttkbootstrap GUI**, a **PostgreSQL backend** for persistence, a **FastAPI Server** for API integration, can **exports** to JSON, CSV, PDF, and DOCX, and a Python Modern UI tool.
Also, Logs can be exported in multiple formats for reporting or archival. Logs are inserted into PostgreSQL with timestamp and hostname. Logs can be fetched from external APIs and bulk-imported. 
In addition, Users can input log messages via GUI, selecting type (INFO, WARNING, ERROR, DEBUG). GUI supports local filtering and real-time refresh from DB.

---

## 📂 Project Structure:

```
tunglogger/
├─ runner.py #(main)
├─ gui.py
├─ logger.py
├─ database.py
├─ save.py
├─ uis.py
├─ client_api.py
├─ server_api.py
└─ tunglogger_slq.sql
└── .gitignore
```
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-brightgreen?logo=windows)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## ✨ Essential Key Features:

  ### Log Management Tool:
- 💾 **Internal Logger Tool** for SMEs.
- 👁‍🗨 Local **Multi-Action** Filtering.
- 🔁 **Real-time** Refresh.
- 🔰 FastAPI-based **RESTful Server** for Logs.
  ### Modern Python UI Design:
- 🖥️ **Desktop UI (Tk + ttkbootstrap)** to create, filter, and view logs.
- 🌗 **Light theme/Dark theme toggle**.
  ### Secure SQL Connetion: 
- 🗄️ **PostgreSQL persistence** with connection pooling and retries.
- 📜 Real-time **Log Synchronizer** between SQL and Program.
- 📃 Sequence & Trigger management for **clean log handling**.
  ### Fetch Multi-Logs From Server API-Client API: 
- 🌐 **FastAPI demo server** (health check, list logs, bulk insert).
  ### API Import:  
- 🔗 **API import** from endpoints returning list or `{ "data": [...] }`.
  ### Multi-format and Simple Export (Saved as..) Buttons:  
- 📤 **One-click exports** → JSON / CSV / PDF / DOCX.
  - 📄 JSON  (`.json`)
  - 📊 Excel (`.xlsx`)  
  - 📑 PDF  (`.pdf`)
  - 📝 Word (`.docx`) 

---

## ⚙️ Installation & Setup:

### Requirements:
- Python **3.10+**
- PostgreSQL **17+**
- (Demo Server for training in this project) **FastAPI**
- Dependencies listed in `requirements.txt`
- Dependencies:
  ```
  pip install -r requirements.txt
  ```
  
  ---

## 🔒 Security Notes:
  
  ```
     If you plan to be inspired this project in the future, don't forget to do these things;
     
     Credentials come only from .env.
     Demo FastAPI server has no auth (add API keys/JWT before exposing).
     SQL information and SQL Auth is another security issue that requires attention.
     Exports include hostname → anonymize before sharing publicly.
     API client should only fetch from trusted HTTPS endpoints.
```
     
---

## 📦 Database Configuration:

- Create a PostgreSQL database (e.g. **tunglogger_db**).
- Run the provided **tunglogger_sql.sql** file to create required tables, functions and triggers.
- Update database credentials inside **database.py** and **logger.py** in the **database configuration section** block with dotenv secure protection.

---

## 💥 Important Reminder:

- Don't forget to change the database information in the code!

---


## 👑 Author:

        Tunç KUL
    Computer Engineer
