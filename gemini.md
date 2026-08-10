# SCOUT: Architecture, Tools, and Workflow

Based on the `IDEA.md` specification, we are building a lightweight, highly optimized, and Mac-native autonomous research agent. It is designed to run entirely locally, respect strict time constraints, and avoid heavy enterprise orchestrators (like Docker or n8n).

Here is a breakdown of the tools we will use, the system architecture, and how it will work.

---

## 1. The Tools & Stack

We are keeping the stack incredibly lean. Everything runs on the bare metal of your M4 MacBook to maximize the 24GB of unified memory for the LLMs.

### Core Logic & Orchestration
*   **Python 3.12 + `uv`**: The core programming language. `uv` will be used for lightning-fast dependency management and virtual environments.
*   **macOS `pmset`**: Used to physically wake up your Mac from sleep just before the pipeline starts.
*   **macOS `launchd`**: The native Apple job scheduler (better than `cron` because if the Mac is asleep when a job is scheduled, `launchd` can catch up when it wakes).

### The "Brain" (Local AI)
*   **Ollama**: To serve the models locally.
*   **Main LLM (~14B model)**: E.g., Qwen 2.5 14B or Llama 3 8B. Used for the heavy lifting of reading text, analyzing problems, and scoring opportunities.
*   **Embedding Model**: A small model (like `nomic-embed-text`) to create vector embeddings of the text for deduplication and semantic search.
*   **Pydantic**: To force the LLM to output strict, schema-locked JSON. We will not parse freeform text.

### Data Ingestion (Scraping)
*   **`httpx` (async)**: For making fast, concurrent HTTP requests to APIs (Hacker News, Reddit, GitHub).
*   **`tenacity`**: For automatically retrying failed network requests.
*   **`feedparser`**: To easily ingest arbitrary RSS feeds.
*   **`trafilatura`**: To extract clean, readable text from raw HTML articles (stripping out ads, navbars, and junk).

### Storage & State
*   **SQLite**: The single source of truth. No in-memory state. If the script crashes, it can resume from SQLite.
    *   **WAL Mode**: Write-Ahead Logging enabled for concurrent reads/writes (so the UI can read while the agent writes).
    *   **FTS5**: Full-Text Search extension for incredibly fast searching in the "Archive" tab.
    *   **`sqlite-vec`**: An extension to store and query vector embeddings directly in SQLite (no need for a separate vector database like Milvus or Pinecone).

### Local Dashboard (UI)
*   **FastAPI**: The fast, async Python web server.
*   **Jinja2**: For rendering HTML templates on the server.
*   **HTMX**: To give the web UI dynamic, React-like interactivity without actually writing a heavy React Single Page Application (SPA).
*   **Tailwind CSS**: For beautiful, modern, utility-class styling.

### Delivery
*   **Telegram Bot API (over plain HTTP)**: To send the 6:00 AM digest directly to your phone.
*   **macOS Keychain**: To securely store the Telegram Bot token so it isn't sitting in plaintext in a `.env` file.

---

## 2. The Architecture

The most critical architectural decision is **Decoupling**. Delivery must never depend on the processing finishing successfully. Therefore, SCOUT is actually **two completely separate programs** that only communicate through the SQLite database.

### Job A: The Processing Pipeline (02:00 - 05:00)
This is the heavy job. 
1.  `pmset` wakes the Mac at 01:59.
2.  `launchd` fires the Python script at 02:00.
3.  The pipeline runs, downloads data, filters it, runs Ollama, and saves to SQLite.
4.  **Deadline Awareness:** The script constantly checks the clock. If it hits 05:00, it forcefully but gracefully truncates whatever it is doing, saves its current state to SQLite, and exits. The Mac can go back to sleep and cool down before you start your day.

### Job B: The Delivery Agent (06:00)
This is a tiny, instant script.
1.  `launchd` fires the delivery script at 06:00.
2.  It queries SQLite for: *"Give me the top-scored, unsent opportunities from the last 24 hours."*
3.  It formats them nicely and sends a Telegram message.
4.  If Job A crashed at 03:00, Job B still runs at 06:00 and sends whatever Job A managed to process (or a failure warning). 

---

## 3. How the Pipeline Works (The "Funnel")

Because running LLMs locally is slow and expensive (compute-wise), we use a "funnel" approach. We start with cheap operations and only send the survivors to the expensive LLM.

1.  **Ingestion (Cheap):** Download thousands of threads, issues, and articles.
2.  **Deduplication (Cheap):** Generate embeddings and compare them against SQLite to see if we've analyzed this exact topic recently. Drop the duplicates.
3.  **Heuristic Filtering (Cheap):** Use plain Python code (regex, keyword matching, length checks) to drop obvious junk (e.g., posts with 0 comments, posts containing spam keywords).
4.  **LLM Extraction (Expensive):** The surviving items (maybe 100-200) are fed to Ollama. The LLM's strict instructions are: *"Read this text. Is the author describing a genuine problem? Extract the problem. Do not invent anything."*
5.  **LLM Scoring (Expensive):** For the verified problems, Ollama scores them against your personal constraints (solo dev, no budget) and outputs a Pydantic-validated JSON score.
6.  **Storage:** The scored items sit in SQLite, waiting for the 6:00 AM Telegram delivery.

---

This architecture perfectly fits your constraints. It guarantees your Mac won't be running hot during the day, it's completely free, and it's robust against unexpected crashes.
