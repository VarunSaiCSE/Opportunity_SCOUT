Yep. Think of this as the **master specification/prompt** for the project. If we hand this to a capable coding agent, it should understand what we're trying to build, why, and how we're going to build it.

# SCOUT — Personal Autonomous Research & Opportunity Agent

## 1. The whole idea

We are going to build a **self-hosted AI research agent called SCOUT** that runs entirely on the user's MacBook.

SCOUT's job is to work like a **personal research analyst** that operates in the background.

It periodically searches publicly available online information for:

1. **Real-world problems** people are complaining about.
2. **Developer problems** appearing in GitHub, Hacker News, Stack Overflow, etc.
3. **Business problems** that could potentially be solved with software.
4. **Startup opportunities** and underserved markets.
5. **Open-source projects/issues** worth contributing to.
6. **Research opportunities** and interesting technical/ML problems.
7. **Potential freelance/side-project opportunities.**
8. Emerging trends that could turn into projects or businesses.

SCOUT should **not simply generate random AI startup ideas**.

It should find actual evidence first.

For example:

```text
Internet
   ↓
People repeatedly complain about X
   ↓
SCOUT collects the evidence
   ↓
SCOUT identifies the underlying problem
   ↓
SCOUT researches existing solutions
   ↓
SCOUT analyzes competition
   ↓
SCOUT estimates difficulty
   ↓
SCOUT estimates monetization potential
   ↓
SCOUT checks whether the user can realistically build it
   ↓
SCOUT gives the opportunity a score
   ↓
Store everything in database
   ↓
Send best opportunities to Telegram
```

The fundamental philosophy is:

> **Evidence → Problem → Research → Analysis → Opportunity → Recommendation**

not:

> **LLM → random startup idea**

---

# 2. What SCOUT should ultimately do

Every day, SCOUT should be able to produce something like:

```text
SCOUT DAILY BRIEF
────────────────────────────

Research completed: 03:17 AM

Sources scanned: 42
Items collected: 381
Duplicates removed: 127
Potential problems: 61
Verified problems: 23
High-value opportunities: 7


TOP OPPORTUNITY

AI quotation automation for contractors

Score: 9.1 / 10

Problem:
Contractors repeatedly create quotations manually...

Evidence:
• Reddit discussion
• GitHub project
• Industry forum
• Multiple independent complaints

Competition:
Medium

Difficulty:
Medium

Monetization:
High

Your skill fit:
Very high

Suggested MVP:
...

Why this is interesting:
...

Sources:
...
```

The report goes to **Telegram**.

Everything is also stored locally so it doesn't disappear after one day.

---

# 3. SCOUT should have memory

SCOUT will maintain a **local SQLite database**.

It remembers:

* problems it has discovered
* opportunities
* sources
* evidence
* research results
* previous analyses
* previous runs
* rejected ideas
* interesting ideas
* your feedback
* trends over time

This allows it to detect things like:

> "This problem appeared across 8 independent sources over the last 30 days."

That's much more useful than treating every research run independently.

---

# 4. SCOUT should understand YOU

We'll give SCOUT a user profile containing things such as:

```text
Skills:
Python
ML
AI
Web development
GitHub
Docker

Interests:
AI
ML
automation
startups
developer tools
research

Constraints:
Solo developer
Student
Low budget
Local computing

Goals:
Build portfolio projects
Find startup opportunities
Find research problems
Make money
Contribute to open source
```

The system then calculates:

### "Is this a good opportunity?"

and separately:

### "Is this a good opportunity **for you**?"

That distinction is important.

---

# 5. SCOUT's local AI architecture

We will use **Ollama** as the local LLM runtime.

We won't depend on OpenAI/Anthropic/Gemini APIs for the core intelligence.

The initial models will be:

### Qwen3 8B

Used for fast:

* classification
* filtering
* categorization
* lightweight summarization
* preprocessing

### Qwen3 14B

The primary model.

Used for:

* problem analysis
* opportunity analysis
* startup ideation
* summarization
* scoring
* report generation

### DeepSeek-R1 14B

Used selectively for deeper reasoning:

* complex opportunity analysis
* competitor reasoning
* research analysis
* high-value opportunities

The models will run **locally on the MacBook** through Ollama.

We won't run all three simultaneously unnecessarily.

---

# 6. The application architecture

The final system will consist of:

```text
┌──────────────────────────────────────────────┐
│                    SCOUT                     │
│                                              │
│  ┌───────────────┐                           │
│  │     n8n       │  Scheduling / Automation  │
│  └───────┬───────┘                           │
│          │                                   │
│          ▼                                   │
│  ┌───────────────────────┐                   │
│  │    Python Agent Core  │                   │
│  │                       │                   │
│  │ Research              │                   │
│  │ Analysis              │                   │
│  │ Scoring               │                   │
│  │ Memory                │                   │
│  │ Deduplication         │                   │
│  └───────┬───────────────┘                   │
│          │                                   │
│     ┌────┴─────┐                             │
│     ▼          ▼                             │
│  Internet    Ollama                          │
│  Sources     Local LLMs                      │
│     │          │                             │
│     └────┬─────┘                             │
│          ▼                                   │
│      SQLite DB                               │
│          │                                   │
│          ▼                                   │
│      FastAPI                                 │
│          │                                   │
│          ▼                                   │
│      React UI                                │
│                                              │
└──────────────────────────────────────────────┘
          │
          ▼
       Telegram
```

---

# 7. Technologies

We will deliberately keep everything local/open-source where possible.

### Core

**Python**

The main programming language and agent engine.

### LLM

**Ollama**

Runs local models.

Models:

* Qwen3 8B
* Qwen3 14B
* DeepSeek-R1 14B

### Automation

**n8n Community Edition**

Responsible for:

* schedules
* triggers
* workflow execution
* nightly jobs
* Telegram integration
* failure/retry orchestration

### Database

**SQLite**

Local persistent storage.

No database server required.

### Backend

**FastAPI**

Provides the API for the dashboard and other components.

### Frontend

**React + Vite**

Local dashboard.

### UI

**Tailwind CSS**

For styling.

### Live communication

**WebSockets or Server-Sent Events**

So the dashboard can show:

```text
Scanning GitHub...
Found 73 issues
Analyzing problem #41...
Running Qwen3...
Saving result...
```

live.

### Web research

Use:

* `httpx`
* BeautifulSoup
* RSS/feedparser
* APIs where available
* Playwright when browser automation is actually necessary

### Telegram

**Telegram Bot API**

Used for:

* daily reports
* notifications
* commands
* remote control

### Deployment

**Docker + Docker Compose**

Used primarily for infrastructure such as n8n and supporting services.

### Version control

**Git + GitHub**

---

# 8. Phase-by-phase build prompts

Now the important part.

Each phase below can be treated as a **prompt to the coding agent**.

---

## PHASE 0 — Project Foundation

### Prompt

> Build the initial SCOUT project foundation.
>
> Create a clean monorepo structure for a local autonomous research agent running on macOS.
>
> The system will eventually contain:
>
> * Python agent backend
> * Ollama integration
> * SQLite database
> * n8n orchestration
> * FastAPI backend
> * React/Vite dashboard
> * Telegram bot
> * Docker configuration
>
> For this phase, only establish the project structure, environment configuration, dependency management, `.env.example`, logging system, configuration system, Docker Compose foundation, Git configuration, and README.
>
> Do not implement the actual research agent yet.
>
> Make the architecture modular so research sources, LLM providers, scoring algorithms, database repositories, notification systems, and UI components can be added independently later.

---

# PHASE 1 — Local LLM Engine

### Prompt

> Implement the SCOUT local LLM subsystem using Ollama.
>
> Create a clean abstraction layer so the rest of the application does not directly depend on Ollama-specific implementation details.
>
> Support:
>
> * Qwen3 8B
> * Qwen3 14B
> * DeepSeek-R1 14B
>
> Implement:
>
> * model selection
> * prompt management
> * structured JSON responses
> * retries
> * timeout handling
> * logging
> * token/context configuration
> * model health checks
>
> The system should allow different tasks to use different models.
>
> Qwen3 8B should handle lightweight classification/filtering.
>
> Qwen3 14B should be the primary analysis model.
>
> DeepSeek-R1 should be reserved for deeper reasoning tasks.
>
> Models should not be unnecessarily loaded or executed concurrently.

---

# PHASE 2 — Database & Memory

### Prompt

> Implement SCOUT's SQLite persistence layer.
>
> Design a normalized database schema for:
>
> * research runs
> * sources
> * raw discoveries
> * problems
> * evidence
> * opportunities
> * opportunity scores
> * research reports
> * user feedback
> * user profile
> * agent events
> * errors
>
> Create migrations and repository/service abstractions.
>
> Every research item must retain its source URL and discovery timestamp.
>
> The system must support historical queries so SCOUT can detect recurring problems and trends across multiple research runs.
>
> Do not couple database logic directly to the LLM or frontend.

---

# PHASE 3 — Research Sources

### Prompt

> Implement SCOUT's research ingestion system.
>
> Create a pluggable source architecture where every source implements a common interface.
>
> Initially support:
>
> * GitHub
> * Hacker News
> * Reddit where technically/API-accessibly appropriate
> * RSS feeds
> * public web pages
>
> Prefer official APIs and RSS feeds over scraping.
>
> Use HTTP clients for static pages.
>
> Use Playwright only for pages that genuinely require browser rendering.
>
> Every collected item must contain:
>
> * source
> * URL
> * title
> * content
> * timestamp if available
> * metadata
> * collection timestamp
>
> Implement rate limiting, retries, timeouts and graceful failure.
>
> A failure in one source must not terminate the entire research run.

---

# PHASE 4 — Problem Detection

### Prompt

> Build SCOUT's problem-detection pipeline.
>
> Convert raw internet discoveries into structured potential problems.
>
> For each discovery, determine:
>
> * what problem is being discussed
> * who experiences it
> * severity
> * frequency
> * category
> * industry
> * whether it appears to be a genuine problem
> * evidence supporting the problem
> * confidence
>
> Use Qwen3 8B for initial filtering and Qwen3 14B for detailed analysis.
>
> Do not allow the LLM to invent evidence.
>
> All claims about the existence of a problem must reference actual collected source material.

---

# PHASE 5 — Deduplication & Verification

### Prompt

> Implement SCOUT's deduplication and verification system.
>
> The same underlying problem may appear across multiple websites and discussions.
>
> Build a pipeline that clusters semantically similar discoveries into a single problem.
>
> Track:
>
> * number of independent sources
> * source diversity
> * recurrence over time
> * supporting evidence
> * contradictory evidence
>
> Produce a confidence score.
>
> SCOUT should prefer problems supported by multiple independent sources over isolated observations.
>
> Preserve all original sources so the user can inspect the evidence.

---

# PHASE 6 — Opportunity Intelligence

### Prompt

> Build SCOUT's opportunity-analysis engine.
>
> For each verified problem, determine whether it could become:
>
> * a software project
> * startup
> * SaaS product
> * freelance opportunity
> * open-source contribution
> * research project
> * ML project
> * automation
>
> Analyze:
>
> * problem severity
> * demand
> * evidence
> * competition
> * existing solutions
> * build difficulty
> * monetization potential
> * market timing
> * technical feasibility
> * user's skill fit
>
> Generate a structured opportunity report.
>
> Do not generate opportunities without first establishing the underlying problem.

---

# PHASE 7 — Opportunity Scoring

### Prompt

> Implement a deterministic opportunity scoring framework.
>
> Every opportunity should receive individual scores for:
>
> * problem severity
> * demand
> * evidence strength
> * competition
> * build difficulty
> * monetization potential
> * market timing
> * user's skill fit
>
> Calculate a final weighted opportunity score.
>
> Store both the individual dimensions and final score in SQLite.
>
> The scoring algorithm should be configurable rather than hard-coded so weights can be changed later.
>
> The system should rank opportunities and identify high-confidence recommendations.

---

# PHASE 8 — Personalization

### Prompt

> Implement SCOUT's user-profile and feedback system.
>
> Create a configurable user profile containing:
>
> * skills
> * technologies
> * interests
> * research interests
> * preferred project types
> * budget constraints
> * time constraints
> * career goals
>
> Add feedback actions:
>
> * interesting
> * ignore
> * already exists
> * investigate
> * build
>
> Store all feedback.
>
> Modify opportunity ranking using the user's profile and historical feedback.
>
> Do not modify the core evidence score based solely on user preference. Keep objective opportunity quality separate from personalized fit.

---

# PHASE 9 — n8n Automation

### Prompt

> Integrate SCOUT with self-hosted n8n Community Edition.
>
> n8n should act as the orchestration and scheduling layer, while Python remains responsible for the actual research and intelligence logic.
>
> Implement workflows for:
>
> * daily research
> * random research windows
> * manual execution
> * nightly execution
> * morning report generation
> * failure notifications
>
> Support scheduling such as:
>
> * fixed time
> * random time within a configured window
> * manual trigger
>
> The system must support overnight execution while the user is asleep.
>
> Implement job locking so multiple heavy SCOUT research jobs cannot run simultaneously.

---

# PHASE 10 — Telegram Bot

### Prompt

> Implement the SCOUT Telegram bot.
>
> Telegram is the primary notification and remote-control interface.
>
> Implement:
>
> `/start`
> `/help`
> `/status`
> `/run`
> `/stop`
> `/report`
> `/history`
>
> Send the morning opportunity report through Telegram.
>
> Reports should contain only the highest-value opportunities rather than dumping all collected information.
>
> Each opportunity should include:
>
> * title
> * problem
> * opportunity score
> * evidence summary
> * potential
> * build difficulty
> * user fit
> * recommended next action
>
> Add interactive feedback where practical.

---

# PHASE 11 — FastAPI Backend

### Prompt

> Implement the SCOUT FastAPI backend.
>
> Create REST APIs for:
>
> * system status
> * research runs
> * agent events
> * opportunities
> * research reports
> * sources
> * user feedback
> * scheduling
> * manual agent execution
> * statistics
>
> Add WebSocket or Server-Sent Events support for live agent activity.
>
> The API should communicate with the existing Python agent services and SQLite database without duplicating business logic.

---

# PHASE 12 — React Dashboard

### Prompt

> Build SCOUT's localhost React dashboard using Vite and Tailwind CSS.
>
> The dashboard should provide:
>
> ### Overview
>
> * system status
> * current run
> * source counts
> * discoveries
> * verified problems
> * opportunities
> * recent activity
>
> ### Live Activity
>
> Show real-time agent events through WebSockets/SSE.
>
> ### Opportunities
>
> Provide filtering and sorting by:
>
> * score
> * category
> * difficulty
> * monetization
> * user fit
> * date
>
> ### Opportunity Detail
>
> Show:
>
> * problem
> * evidence
> * sources
> * competitors
> * analysis
> * scores
> * suggested MVP
> * user fit
>
> ### Research
>
> Show research discoveries and reports.
>
> ### History
>
> Show previous research runs.
>
> ### Settings
>
> Allow configuration of:
>
> * schedules
> * research categories
> * source configuration
> * model selection
> * user profile
>
> Keep the UI clean and functional rather than visually excessive.

---

# PHASE 13 — Live Agent Monitoring

### Prompt

> Implement real-time agent observability.
>
> Every significant SCOUT event should be emitted as an event:
>
> * run started
> * source started
> * source completed
> * items collected
> * filtering started
> * analysis started
> * opportunity discovered
> * database write
> * Telegram report sent
> * error
> * run completed
>
> Stream these events to the React dashboard using WebSockets or SSE.
>
> The user should be able to watch a research run live from localhost.

---

# PHASE 14 — Advanced Autonomous Research

### Prompt

> Extend SCOUT from a single-pass analysis system into a multi-step research agent.
>
> When SCOUT identifies a high-value problem, automatically perform additional research:
>
> 1. Verify the problem.
> 2. Search for additional evidence.
> 3. Search for competitors.
> 4. Search GitHub for existing implementations.
> 5. Search academic literature where relevant.
> 6. Investigate market signals.
> 7. Analyze possible MVPs.
> 8. Estimate technical complexity.
> 9. Analyze monetization.
> 10. Recalculate the opportunity score.
>
> Use DeepSeek-R1 only for high-value or complex research tasks.
>
> Keep the process bounded so the agent cannot enter an infinite research loop.

---

# PHASE 15 — Trend Detection

### Prompt

> Implement temporal trend analysis.
>
> Use historical SQLite data to identify:
>
> * rapidly increasing problems
> * recurring problems
> * emerging technologies
> * growing developer complaints
> * increasing demand signals
> * opportunities appearing across multiple sources
>
> SCOUT should distinguish between a one-time observation and a persistent/emerging trend.
>
> Include trend information in opportunity scoring.

---

# PHASE 16 — Self-Improvement

### Prompt

> Implement SCOUT's long-term personalization system.
>
> Analyze the user's historical feedback to identify:
>
> * preferred opportunity categories
> * preferred difficulty
> * technologies of interest
> * frequently rejected ideas
> * frequently selected opportunities
>
> Improve personalized ranking over time.
>
> Do not allow personalization to override objective evidence quality.
>
> Maintain separate:
>
> * Objective Opportunity Score
> * Personalized Fit Score
>
> so the user can understand why SCOUT recommends something.

---

# 17. Final operating model

Once everything is finished, the workflow becomes:

```text
                 NIGHT
                   │
                   ▼
              n8n Scheduler
                   │
                   ▼
             Start SCOUT Run
                   │
                   ▼
           Collect Internet Data
                   │
                   ▼
            Qwen3 8B Filtering
                   │
                   ▼
             Deduplication
                   │
                   ▼
            Problem Detection
                   │
                   ▼
            Qwen3 14B Analysis
                   │
                   ▼
           Evidence Verification
                   │
                   ▼
           Opportunity Scoring
                   │
              High potential?
               /          \
             NO            YES
             │              │
           Store       Deep Research
                            │
                            ▼
                     DeepSeek-R1
                            │
                            ▼
                     Final Ranking
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
               SQLite             Telegram
                  │
                  ▼
            Local Dashboard
```

Then you wake up.

You don't have to search Reddit.

You don't have to browse GitHub.

You don't have to ask ChatGPT:

> "Give me startup ideas."

You open Telegram and see:

> **"I found these 3 things overnight. These are the ones worth your attention."**

And localhost gives you the full investigation if one catches your eye.

---

# 18. The final technology stack

```text
SCOUT
│
├── Language
│   └── Python
│
├── AI
│   └── Ollama
│       ├── Qwen3 8B
│       ├── Qwen3 14B
│       └── DeepSeek-R1 14B
│
├── Research
│   ├── GitHub
│   ├── Hacker News
│   ├── Reddit
│   ├── RSS
│   ├── Public Web
│   └── Playwright
│
├── Storage
│   └── SQLite
│
├── Automation
│   └── n8n Community Edition
│
├── Backend
│   └── FastAPI
│
├── Frontend
│   ├── React
│   ├── Vite
│   └── Tailwind
│
├── Realtime
│   └── WebSockets / SSE
│
├── Notifications
│   └── Telegram Bot API
│
├── Infrastructure
│   └── Docker Compose
│
└── Version Control
    └── Git + GitHub
```

### The key architectural principle

**SCOUT is not an "AI that generates ideas."**

It is a **local evidence-driven research pipeline** with an LLM inside it.

The LLM provides intelligence, but:

* sources provide evidence,
* Python controls the logic,
* SQLite provides memory,
* deterministic scoring provides consistency,
* n8n provides scheduling,
* FastAPI provides the API,
* React provides visibility,
* Telegram provides your interface.

That separation is what will keep the project maintainable when it grows from a simple overnight experiment into a genuinely capable autonomous research system.
