import streamlit as st
import google.generativeai as genai
import openai
import anthropic
import database as db
import file_parser
import template_engine
import json
import re

# Initialize database
db.init_db()

st.set_page_config(page_title="Teacher Assistant Agent", layout="wide", page_icon="👨‍🏫")

# Initialize session state for selected sources
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = {}

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    with st.expander("ℹ️ How to get an API Key?"):
        st.write("""
        **Google Gemini:** Go to [Google AI Studio](https://aistudio.google.com/), sign in, and click 'Get API key'.
        **OpenAI:** Go to [OpenAI Platform](https://platform.openai.com/api-keys) and generate a new key.
        **Anthropic:** Go to [Anthropic Console](https://console.anthropic.com/settings/keys).
        """)
        
    provider_options = ["Google Gemini", "OpenAI (ChatGPT)", "Anthropic (Claude)"]
    saved_provider = db.get_setting("selected_provider", "Google Gemini")
    try:
        provider_index = provider_options.index(saved_provider)
    except ValueError:
        provider_index = 0
        
    selected_provider = st.selectbox("Select AI Provider:", provider_options, index=provider_index)
    
    # Dynamic settings based on provider
    if selected_provider == "Google Gemini":
        api_key_key = "gemini_api_key"
        model_options = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.1-pro-preview", "gemini-flash-latest", "gemini-pro-latest"]
    elif selected_provider == "OpenAI (ChatGPT)":
        api_key_key = "openai_api_key"
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    else:
        api_key_key = "anthropic_api_key"
        model_options = ["claude-3-5-sonnet-latest", "claude-3-haiku-20240307", "claude-3-opus-20240229"]
        
    saved_api_key = db.get_setting(api_key_key, "")
    saved_model = db.get_setting(f"{selected_provider}_model", model_options[0])
    
    api_key = st.text_input(f"{selected_provider} API Key:", type="password", value=saved_api_key)
    
    try:
        model_index = model_options.index(saved_model)
    except ValueError:
        model_index = 0
    selected_model = st.selectbox("Select Model:", model_options, index=model_index)
    
    if st.button("Save Settings"):
        db.save_setting("selected_provider", selected_provider)
        db.save_setting(api_key_key, api_key)
        db.save_setting(f"{selected_provider}_model", selected_model)
        st.success("Settings saved successfully!")


# --- MAIN CONTENT ---
st.title("👨‍🏫 Teacher Assistant Agent")
st.write("Turn your rough notes into beautifully formatted, ready-to-print official documents in seconds.")

# --- KNOWLEDGE BASE / SOURCES ---
with st.expander("📚 Reference Sources (Optional Knowledge Base)"):
    st.write("Upload documents to use as context (like curriculum guides, previous reports, or data).")
    uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'docx', 'xlsx'])
    
    if uploaded_file is not None:
        if st.button("Add to Knowledge Base"):
            with st.spinner("Parsing file..."):
                extracted_text = file_parser.extract_text(uploaded_file, uploaded_file.name)
                db.save_source(uploaded_file.name, extracted_text)
                st.success(f"Added {uploaded_file.name} to sources!")
                
    st.divider()
    st.subheader("Your Sources")
    sources = db.get_all_sources()
    
    if not sources:
        st.info("No sources added yet.")
    else:
        for source in sources:
            source_id, filename, content = source
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                # Checkbox to include this source
                is_checked = st.checkbox(f"Include: {filename}", value=st.session_state.selected_sources.get(source_id, False), key=f"check_{source_id}")
                st.session_state.selected_sources[source_id] = is_checked
            with col2:
                if st.button("Delete", key=f"del_{source_id}"):
                    db.delete_source(source_id)
                    if source_id in st.session_state.selected_sources:
                        del st.session_state.selected_sources[source_id]
                    st.rerun()

# --- DOCUMENT GENERATION ---
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
        st.error(f"Please enter your {selected_provider} API Key in the settings sidebar and click Save.")
    elif not rough_notes:
        st.warning("Please provide some rough notes.")
    else:
        with st.spinner(f"Agent is drafting using {selected_model}..."):
            try:
                # 1. Build the prompt with context
                sources = db.get_all_sources()
                context_texts = []
                for source in sources:
                    source_id, filename, content = source
                    if st.session_state.selected_sources.get(source_id, False):
                        context_texts.append(f"--- Source: {filename} ---\n{content}\n")
                
                final_prompt = ""
                if context_texts:
                    final_prompt += "BACKGROUND KNOWLEDGE/SOURCES:\n"
                    final_prompt += "\n".join(context_texts)
                    final_prompt += "\n\n"
                    
                final_prompt += f"ROUGH NOTES TO CONVERT:\n{rough_notes}"
                
                system_instruction = f"""
                You are an expert Thai Teacher Assistant. Your job is to take rough notes (and optional background sources) and extract the information into a highly professional, well-structured document.
                The task type is: {task_type}.
                You MUST use formal Thai official language (ภาษาราชการ). Ensure proper bureaucratic terminology, polite phrasing, and standard structural formatting suitable for Thai schools or government.
                
                CRITICAL INSTRUCTION: You MUST output ONLY valid JSON format. Do NOT wrap it in markdown blockquotes like ```json.
                All text values MUST be properly escaped according to JSON standards.
                - NEVER use raw line breaks inside strings. Use strictly '\\n' to denote paragraphs.
                - Escape all double quotes inside text as '\\"'.
                
                If the task is "Official Memos (บันทึกข้อความ)" OR "Letters to Parents (จดหมายแจ้งผู้ปกครอง)", your JSON must have AT LEAST these core keys:
                "government_agency" (string, use school name for letters), "document_number" (string), "date" (string), "subject" (string), "to" (string), "body" (string with \\n for paragraphs), "signature_name" (string), "signature_title" (string).
                
                IMPORTANT FLEXIBILITY: If the user explicitly asks for extra sections at the bottom (like "a checkbox to approve", "a form", "director signature block"), you MUST create a NEW key in your JSON for it (e.g., "approval_section": "[  ] อนุมัติ   [  ] ไม่อนุมัติ\\nเหตุผล................................") and provide the text.
                
                If it is another task, create appropriate logical string keys for the sections and provide the formal Thai text as string values.
                """
                
                raw_response = ""
                
                # 2. Call the appropriate API
                if selected_provider == "Google Gemini":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name=selected_model, 
                        system_instruction=system_instruction,
                        generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
                    )
                    response = model.generate_content(final_prompt)
                    raw_response = response.text
                    
                elif selected_provider == "OpenAI (ChatGPT)":
                    client = openai.OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=selected_model,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": final_prompt}
                        ]
                    )
                    raw_response = response.choices[0].message.content
                    
                elif selected_provider == "Anthropic (Claude)":
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model=selected_model,
                        system=system_instruction,
                        messages=[
                            {"role": "user", "content": final_prompt + "\n\nCRITICAL: OUTPUT ONLY JSON FORMAT, starting with { and ending with }."}
                        ],
                        max_tokens=4000
                    )
                    raw_response = response.content[0].text
                
                # 3. Parse JSON
                try:
                    # Strip possible markdown code blocks if the AI disobeyed
                    if raw_response.startswith("```json"):
                        raw_response = raw_response[7:]
                    if raw_response.startswith("```"):
                        raw_response = raw_response[3:]
                    if raw_response.endswith("```"):
                        raw_response = raw_response[:-3]
                        
                    data = json.loads(raw_response.strip())
                except Exception as e:
                    st.error(f"The AI failed to generate correct JSON data format. Please try again. Error: {e}\nRaw Output: {raw_response[:200]}...")
                    st.stop()
                
                # 4. Generate visual HTML preview
                html_preview = template_engine.get_html_preview(data, task_type)
                
                # 5. Save to database
                db.save_document(task_type, rough_notes, json.dumps(data, ensure_ascii=False))
                
                st.session_state['generated_data'] = data
                st.session_state['generated_html'] = html_preview
                st.session_state['current_task_type'] = task_type
                st.success("Document generated successfully!")
                
            except Exception as e:
                st.error(f"An error occurred with the API: {e}")
                if selected_provider == "Google Gemini":
                    try:
                        genai.configure(api_key=api_key)
                        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        st.info(f"Debug Info: The models available for your specific API key are: {available_models}")
                    except Exception:
                        pass

# --- DISPLAY PREVIEW ---
if 'generated_html' in st.session_state:
    st.subheader("Preview (A4 Paper Format)")
    
    # Display the HTML preview visually simulating a piece of paper
    st.html(st.session_state['generated_html'])
    
    st.write("### Ready to Print?")
    col1, col2 = st.columns(2)
    with col1:
        doc_io = template_engine.generate_docx(st.session_state['generated_data'], st.session_state['current_task_type'])
        st.download_button(
            label="📄 Download Word (.docx)",
            data=doc_io,
            file_name="official_document.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    with col2:
        st.download_button(
            label="🖨️ Download for Print/PDF (.html)",
            data=st.session_state['generated_html'],
            file_name="print_ready_document.html",
            mime="text/html",
            help="Download this, double click to open in your browser, and hit Ctrl+P to easily save as a perfect PDF!"
        )
