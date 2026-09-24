# intel-engine ⚡

A lightweight due-diligence engine built to experiment with **Jev** (`typesafe-ai/jev`) and LLMs for intelligent context pruning and automated company teardowns.

Instead of dumping an entire website into an LLM and blowing through token context limits, `intel-engine` uses a **System 1 (Jev) + System 2 (LLM)** routing pattern:
1. **Scrape & Discover:** Scrapes a target domain's root page and normalizes DOM text while discovering all internal route paths.
2. **Probabilistic Link Filtering (Jev):** Evaluates discovered routes via `typesafe-ai/jev` (Vercel AI Gateway) to score and classify links into categories (docs, pricing, tech, careers) with calibrated confidence probabilities. Junk links (terms, login, legal) are dropped.
3. **Targeted Fetching:** Concurrently scrapes only high-value subpages ($\ge$ 65% confidence threshold).
4. **Strategic Synthesis:** Streams a technical due-diligence teardown using high-speed LLM inference (Groq) and saves the output to `reports/`.

---

## 🏗️ How It Works

```
                        ┌─────────────────────────┐
                        │   Root Target URL       │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │    Scrape & Extract     │
                        │    Discovered Links     │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │     typesafe-ai/jev     │ (Vercel AI Gateway)
                        │  (Probabilistic Router) │
                        └────────────┬────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     │ Gatekeeper: confidence >= 0.65│
                     │ Drop legal / terms / login    │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │  Concurrent Subpage     │
                        │        Scrape           │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   LLM Synthesis Engine  │ (Groq)
                        │    Technical Teardown   │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │ reports/<company>.md    │
                        └─────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Prerequisites & Installation

Clone the repository and install dependencies (using [`uv`](https://github.com/astral-sh/uv) or `pip`):

```bash
git clone https://github.com/your-username/intel-engine.git
cd intel-engine
uv sync
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
VERCEL_AI_GATEWAY_KEY=your_vercel_ai_gateway_key
```

### 3. Run an Audit

Run `main.py` to trigger a teardown:

```bash
uv run main.py
```

The CLI streams live teardown output to your terminal and generates a report in `reports/` (e.g., `reports/supabase_teardown.md`).

---

## 📂 Project Structure

- `main.py` - Main CLI pipeline, rich terminal output rendering, live token streaming, and report generation.
- `router.py` - Interfaces with `typesafe-ai/jev` via Vercel AI Gateway for probabilistic route classification and confidence scoring.
- `scraper.py` - DOM cleaner (strips SVG, scripts, footers) and concurrent async page fetcher.
- `reports/` - Output directory containing generated Markdown teardown reports.

---

## 💡 Why Jev?

Sending raw site crawls directly to an LLM is noisy and expensive. Jev provides calibrated confidence estimates per route choice, allowing us to deterministically filter out irrelevant pages and feed only high-density, context-relevant content into the synthesis LLM—significantly lowering token consumption and latency.
