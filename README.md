# 👨‍🏫 Teacher Assistant Agent

A smart, AI-powered Streamlit web application designed specifically for Thai teachers. It takes your rough, casual notes and instantly transforms them into beautifully formatted, ready-to-print official government documents (such as Official Memos, Lesson Plans, and Letters to Parents) using formal Thai official language (ภาษาราชการ).

## ✨ Features
* **Multi-Model Support:** Connects to Google Gemini, OpenAI (ChatGPT), and Anthropic (Claude).
* **"Bring Your Own Key" (BYOK):** Users enter their own API keys in the sidebar, which are saved securely to a local SQLite database, meaning the app host doesn't pay for usage!
* **Knowledge Base:** Upload `.txt`, `.pdf`, `.docx`, and `.xlsx` files as reference context (similar to NotebookLM).
* **Strict Thai Formatting:** Uses `python-docx` and HTML templates to rigorously enforce Thai government document standards (TH Sarabun font, exact margins, correct Krut/Header sizes).
* **Export Options:** 
  - Download as `.docx` (Microsoft Word)
  - Download as `.html` (Perfect A4 print preview to save as PDF via Ctrl+P)

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd Teacher-Assistant-Agent
   ```
2. **Create a virtual environment (Optional but recommended):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate # On Mac/Linux
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```bash
   streamlit run app.py
   ```
*(Alternatively, on Windows, just double-click the `run.bat` file!)*

## ☁️ Deploying to Streamlit Cloud

Deploying this app so your friends can use it over the internet is incredibly easy and **free**!

1. Push this folder to a new **Public Repository** on your GitHub account.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **"New app"**.
4. Select your newly created repository, set the branch to `main`, and the main file path to `app.py`.
5. Click **"Deploy!"**

### 🔐 Note on Streamlit Cloud "Secrets"
You **do not** need to configure any Advanced Settings or Secrets for API keys on Streamlit Cloud for this app! 
Because the app features a UI sidebar where users type their own API keys, your friends can simply visit your Streamlit link, open the sidebar, type their own free API key, and start generating. 
*(Note: Streamlit Cloud occasionally resets the virtual server when idle, which will clear the `documents.db` database and forget the saved API keys. Users will just have to paste their key again when that happens).*
