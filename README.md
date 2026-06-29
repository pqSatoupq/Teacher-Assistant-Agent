# 👨‍🏫 Teacher Assistant Agent

A lightweight Streamlit web application designed specifically for Thai teachers and document workers. This tool leverages the Google Gemini API to transform rough, casual notes into highly formal, perfectly structured documents (using formal Thai official language - ภาษาราชการ).

## ✨ Features

- **Multiple Document Types**: Generate Official Memos (บันทึกข้อความ), Lesson Plans (แผนการสอน), Letters to Parents (จดหมายแจ้งผู้ปกครอง), Project Proposals (โครงการ), and Meeting Minutes (รายงานการประชุม).
- **Formal Thai Language**: Automatically enforces correct bureaucratic terminology and polite phrasing suitable for Thai schools.
- **Export to Word**: Download generated documents as Microsoft Word (`.docx`) files for easy printing, signing, and submission.
- **API Key Management**: Securely save your Google Gemini API key and select your preferred model (e.g., `gemini-1.5-flash`, `gemini-1.5-pro`) directly in the app.
- **Local History**: Automatically saves a history of your generated documents to a local SQLite database.

## 🚀 Quick Start (Local Windows)

If you have Python installed, you can easily run this locally:
1. Double click on `run.bat`
2. The script will automatically install dependencies and launch the app in your default web browser.

## 💻 Manual Installation

1. Clone this repository.
2. Open your terminal in the project folder and install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## ☁️ Deploying to Streamlit Community Cloud

This app is ready to be hosted on Streamlit Community Cloud so anyone can access it via a web link.
1. Push this repository to your GitHub account.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Log in with your GitHub account, click **Deploy an app**, and select this repository.
4. Set the "Main file path" to `app.py`.
5. Click **Deploy!**

*(Note: Because this app uses a local SQLite database (`documents.db`), the document history will reset periodically when the Streamlit Cloud server restarts. The app will still function perfectly for generating new documents!)*

## 🔑 Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** on the left menu and create a new key.
4. Paste the key into the Settings sidebar inside the application.
