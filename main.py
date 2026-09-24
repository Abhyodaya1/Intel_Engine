import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import httpx
from groq import AsyncGroq
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown

from scraper import fetch_page, fetch_urls_concurrently
from router import score_and_select_links

load_dotenv()
console = Console()
groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

# Groq's high-speed frontier workhorse model
SYNTHESIS_MODEL = "openai/gpt-oss-120b"

async def run_audit(company_name: str, target_url: str):
    # Header Banner
    console.print(Panel(
        f"[bold white]Target Entity:[/bold white] [bold cyan]{company_name}[/bold cyan]\n"
        f"[bold white]Target Root URL:[/bold white] [underline blue]{target_url}[/underline blue]\n"
        f"[bold white]Route Classifier:[/bold white] [magenta]typesafe-ai/jev[/magenta] (via Vercel AI Gateway)\n"
        f"[bold white]Synthesis Engine:[/bold white] [green]Llama 3.3 70B[/green] (via Groq)",
        title="[bold yellow]System 1 + System 2 Due Diligence Engine[/bold yellow]",
        border_style="yellow"
    ))

    # 1. Fetch Landing Page
    with console.status("[bold green]Scraping landing root...", spinner="dots"):
        async with httpx.AsyncClient() as client:
            _, root_text, discovered_links = await fetch_page(client, target_url)

    console.print(f"[dim]Discovered {len(discovered_links)} internal route paths.[/dim]")

    # 2. Evaluate via Jev
    with console.status("[bold magenta]Evaluating route candidate probabilities via Jev...", spinner="bouncingBar"):
        top_targets = await score_and_select_links(discovered_links)

    # Render Decision Matrix
    decision_table = Table(title="Jev Routing & Calibration Matrix", show_header=True, header_style="bold magenta")
    decision_table.add_column("Category", style="cyan", width=15)
    decision_table.add_column("Confidence Score (Noul)", style="green", width=24)
    decision_table.add_column("Route Target", style="white")

    for url, cat, prob in top_targets:
        decision_table.add_row(cat.upper(), f"{prob * 100:.1f}%", url)
    console.print(decision_table)

    # 3. Concurrently Scrape Filtered Subpages
    selected_urls = [t[0] for t in top_targets]
    with console.status(f"[bold yellow]Concurrently fetching {len(selected_urls)} priority subpages...", spinner="dots"):
        subpage_data = await fetch_urls_concurrently(selected_urls)

    # 4. Context Aggregation
    corpus = f"### Main Page ({target_url})\n{root_text}\n\n"
    for url, content in subpage_data.items():
        corpus += f"### Subpage ({url})\n{content}\n\n"

    console.rule("[bold green]Streaming Strategic Synthesis Dossier")

    system_prompt = (
        "You are a Principal Solutions Architect and Due Diligence Analyst. "
        "Synthesize the provided company data into a rigorous technical dossier in Markdown. "
        "You must cover:\n"
        "1. Inferred System Architecture & Tech Stack Indicators\n"
        "2. Core Value Proposition & Pricing Strategy\n"
        "3. Defensibility & Competitive Moat\n"
        "4. Key Engineering Talent & Hiring Signals\n"
        "Be concrete, avoid marketing fluff, and focus on technical indicators."
    )
    user_prompt = f"Target Company: {company_name}\n\nScraped Context:\n{corpus}"

    # 5. Groq Streaming
    stream = await groq_client.chat.completions.create(
        model=SYNTHESIS_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True,
        temperature=0.2
    )

    full_report = ""
    # Live updates the terminal panel smoothly at 10 frames/sec as tokens arrive
    with Live(console=console, refresh_per_second=10) as live:
        async for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            full_report += token
            live.update(Panel(Markdown(full_report), title=f"Teardown: {company_name}", border_style="cyan"))

    # 6. Save Artifact
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    report_filename = output_dir / f"{company_name.lower().replace(' ', '_')}_teardown.md"
    report_filename.write_text(full_report, encoding="utf-8")

    console.print(f"\n[bold green]Report saved to:[/] [underline]{report_filename}[/underline]\n")

if __name__ == "__main__":
    # Test Run Target
    TARGET_COMPANY = "Supabase"
    TARGET_URL = "https://supabase.com"
    asyncio.run(run_audit(TARGET_COMPANY, TARGET_URL))