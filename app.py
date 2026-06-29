import streamlit as st
import google.generativeai as genai
import database as db
from document_utils import create_word_document

# Initialize database
db.init_db()

st.set_page_config(page_title="Teacher Assistant Agent", layout="wide", page_icon="👨‍🏫")

# Sidebar for Settings
with st.sidebar:
    st.header("⚙️ Settings")
    st.write("Configure your AI Agent here.")
    
    # Explain how to get an API Key
    with st.expander("ℹ️ How to get an API Key?"):
        st.write("""
        1. Go to [Google AI Studio](https://aistudio.google.com/).
        2. Sign in with your Google account.
        3. Click **Get API key** on the left menu.
        4. Click **Create API key** and copy the generated key here.
        """)
    
    # Load saved settings
    saved_api_key = db.get_setting("gemini_api_key", "")
    saved_model = db.get_setting("gemini_model", "gemini-1.5-flash")
    
    api_key = st.text_input("Google Gemini API Key:", type="password", value=saved_api_key)
    
    # Model Selection
    model_options = ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-pro-latest"]
    try:
        model_index = model_options.index(saved_model)
    except ValueError:
        model_index = 0
        
    selected_model = st.selectbox("Select AI Model:", model_options, index=model_index)
    
    if st.button("Save Settings"):
        db.save_setting("gemini_api_key", api_key)
        db.save_setting("gemini_model", selected_model)
        st.success("Settings saved successfully!")

# Main Content
st.title("👨‍🏫 Teacher Assistant Agent")
st.write("Turn your rough notes into formal, professionally formatted documents in seconds.")

task_options = [
    "Official Memos (บันทึกข้อความ)",
    "Lesson Plans (แผนการสอน)",
    "Letters to Parents (จดหมายแจ้งผู้ปกครอง)",
    "Project Proposals (โครงการ)",
    "Meeting Minutes (รายงานการประชุม)"
]
task_type = st.selectbox("What would you like to create?", task_options)

rough_notes = st.text_area("Paste your rough notes or ideas here:", height=200, placeholder="Type your casual notes here...")

if st.button("Generate Document"):
    if not api_key:
        st.error("Please enter your Google Gemini API Key in the settings sidebar. Don't forget to click Save Settings.")
    elif not rough_notes:
        st.warning("Please provide some rough notes.")
    else:
        with st.spinner("Agent is drafting your document..."):
            try:
                genai.configure(api_key=api_key)
                
                # System instructions based on task type
                system_instruction = f"""
                You are an expert Thai Teacher Assistant. Your job is to take rough notes and generate a highly professional, well-structured document.
                The task type is: {task_type}.
                You MUST use formal Thai official language (ภาษาราชการ). Ensure proper bureaucratic terminology, polite phrasing, and standard structural formatting suitable for Thai schools or government.
                Output ONLY the final document in Markdown format. Do not include extra conversational text like 'Here is your document'.
                """
                
                # Initialize model
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(rough_notes)
                final_document = response.text
                
                # Save to database
                db.save_document(task_type, rough_notes, final_document)
                
                st.session_state['generated_doc'] = final_document
                st.success("Document generated and saved successfully!")
                
            except Exception as e:
                st.error(f"An error occurred with the API: {e}")

# Display generated content if it exists
if 'generated_doc' in st.session_state:
    st.subheader("Preview")
    st.markdown(st.session_state['generated_doc'])
    
    # Export button
    doc_io = create_word_document(st.session_state['generated_doc'])
    st.download_button(
        label="📄 Export to Word (.docx)",
        data=doc_io,
        file_name="generated_document.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
