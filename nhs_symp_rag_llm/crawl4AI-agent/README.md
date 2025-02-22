NHS Symptom Detective
=====================

An interactive Streamlit application that leverages official NHS information to analyze user symptoms, retrieve relevant health guidelines, and provide general medical guidance. **Important Note:** This tool provides general guidance only and should **not** replace professional medical advice.

Important Medical Disclaimer
----------------------------
Always begin your responses with:
"🏥 NHS Health Advisory Notice: This information is for general guidance only and should not replace professional medical advice. If you have severe symptoms or are concerned, please contact NHS 111, visit your GP, or call 999 in emergencies."

Prerequisites
-------------
- **Python 3.11+**  
  Other versions of Python may work, but this has been tested with 3.11.

- **Supabase**  
  You need a [Supabase](https://supabase.com/) account and an appropriate database with the `site_pages` table and the `match_site_pages` function set up. (See `site_pages.sql` for reference.)

- **OpenAI API Key**  
  Obtain an OpenAI API key from [https://platform.openai.com](https://platform.openai.com).

- **Environment Variables**  
  The app relies on environment variables to connect to OpenAI and Supabase. Create a `.env` file or set them in your environment:
  OPENAI_API_KEY=your_openai_api_key
  SUPABASE_URL=your_supabase_url
  SUPABASE_SERVICE_KEY=your_supabase_service_key
  LLM_MODEL=gpt-4o-mini

Features
--------
1. **Symptom Analysis**
   - Users can input their symptoms in natural language, and the system retrieves matching information from a Supabase database containing NHS-sourced documents.

2. **Context-Preserved Conversation**
   - The app maintains the entire conversation history, allowing for context-aware Q&A.

3. **Streaming Responses**
   - Answers are streamed in real-time, providing an interactive user experience.

4. **NHS-Sourced Recommendations**
   - The AI agent is prompted to prioritize NHS guidelines and official resources.

Installation
------------
1. **Clone the Repository**
   git clone https://github.com/coleam00/ottomator-agents.git
   cd ottomator-agents/crawl4AI-agent

2. **Create and Activate a Virtual Environment (Recommended)**
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate

3. **Install Dependencies**
   pip install -r requirements.txt

4. **Configure Environment Variables**
   - Rename `.env.example` to `.env`, or create a new `.env` file.
   - Add your OpenAI key, Supabase URL, and Supabase service key to `.env`.
   - (Optional) Set `LLM_MODEL` to your preferred model (e.g., `gpt-3.5-turbo`, `gpt-4`, etc.).

5. **Set Up the Supabase Database** (if not done already)
   - Go to your [Supabase project](https://app.supabase.com/).
   - In the **SQL Editor**, paste and run the SQL commands from `site_pages.sql`.
   - This will:
     1. Create the `site_pages` table
     2. Enable the `pgvector` extension for vector embeddings
     3. Set up the custom function `match_site_pages` for semantic matching
     4. Enable RLS policies and public read access

Usage
-----
1. **Start the Streamlit App**
   streamlit run streamlit_ui.py

2. **Open the Web Interface**
   - The interface will typically open automatically in your browser. If it doesn't, go to http://localhost:8501.
   - You will see a chat-like interface titled "NHS Symptom Detective."

3. **Enter Your Symptoms**
   - In the chat input box, describe your symptoms.
   - The system will respond with NHS-guided information and links to relevant resources in the Supabase database.

How It Works
------------
1. **User Input**
   - The user provides a symptom description, which is captured and passed to the AI agent.

2. **RAG (Retrieval-Augmented Generation)**
   - The system uses an OpenAI embedding model (configured as `text-embedding-3-small` in the code) to embed the user query.
   - A Supabase RPC function (`match_site_pages`) searches for the closest vectors in the `site_pages` table and returns the most relevant NHS pages.
   - The agent combines that retrieved content with a specialized system prompt to generate a comprehensive answer.

3. **Streaming**
   - The OpenAI model streams tokens (partial responses) back to the browser, giving a dynamic user experience.

4. **Conversation Context**
   - All previous messages (both user questions and AI responses) are maintained in `st.session_state.messages`.
   - The agent can provide contextually coherent replies based on the entire conversation.

Project Structure
-----------------
- **`streamlit_ui.py`**  
  Main Streamlit app; handles user input, streaming AI responses, and conversation context.

- **`nhs_symptom_checker.py`**  
  Contains the core RAG agent logic, the system prompt, and the AI tools to analyze symptoms and retrieve condition info.

- **`site_pages.sql`**  
  Supabase database schema and function definitions.

- **`requirements.txt`**  
  Python dependencies.

Contributing
------------
1. **Fork** the repository.
2. **Create a new branch** for your feature or bug fix.
3. **Commit** your changes with clear commit messages.
4. **Push** to your fork.
5. **Open a Pull Request** in the original repository.

License
-------
This project is licensed under the [MIT License](LICENSE).
Please note that while the tool references NHS content, it is **not** an official NHS product.

Disclaimer
----------
This tool is intended for educational and informational purposes only. It does not provide medical diagnosis or treatment. Always consult a qualified health professional for accurate medical advice and treatment recommendations.
