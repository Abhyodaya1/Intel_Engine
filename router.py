import os
from dotenv import load_dotenv
import httpx

load_dotenv()
VERCEL_GATEWAY_URL = "https://ai-gateway.vercel.sh/v1/evaluate"
VERCEL_KEY = os.getenv("VERCEL_AI_GATEWAY_KEY")

async def score_and_select_links(links: list[str]) -> list[tuple[str, str, float]]:
    """
    Sends discovered routes to typesafe-ai/jev via Vercel AI Gateway.
    Filters out junk and ranks paths by calibrated confidence.
    """
    if not VERCEL_KEY:
        raise ValueError("Missing VERCEL_AI_GATEWAY_KEY in your environment.")

    headers = {
        "Authorization": f"Bearer {VERCEL_KEY}",
        "Content-Type": "application/json"
    }

    # Evaluate up to 10 unique internal routes to avoid excessive API calls
    candidates = list(set(links))[:10]
    qualified_targets = []

    async with httpx.AsyncClient() as client:
        for link in candidates:
            payload = {
                "model": "typesafe-ai/jev",
                "state": f"Discovered website route path: {link}",
                "questions": {
                    "page_category": {
                        "type": "choice",
                        "instructions": "Classify the functional purpose of this internal URL route.",
                        "choices": {
                            "tech_docs": "Developer documentation, API reference, architecture guides",
                            "pricing": "Subscription tiers, usage-based fees, calculators, enterprise pricing",
                            "careers": "Engineering job listings, culture, hiring positions",
                            "about": "Company origin, leadership, mission, investor overview",
                            "irrelevant": "Terms of service, privacy, login, legal cookies, status updates"
                        }
                    },
                    "is_high_value": {
                        "type": "boolean",
                        "instructions": "Is this page critical for high-level technical or commercial analysis?"
                    }
                }
            }

            try:
                res = await client.post(VERCEL_GATEWAY_URL, json=payload, headers=headers, timeout=5.0)
                if res.status_code != 200:
                    continue

                body = res.json()
                results = body.get("results", {})

                # Extract typed results
                category = results.get("page_category", {}).get("value", "irrelevant")
                is_valuable = results.get("is_high_value", {}).get("value", False)
                # Jev provides calibrated confidence estimates alongside decisions
                confidence = results.get("is_high_value", {}).get("probability", 0.0)

                # Gatekeeper logic: Only accept high-value, non-irrelevant links with >= 65% certainty
                if category != "irrelevant" and is_valuable and confidence >= 0.65:
                    qualified_targets.append((link, category, round(confidence, 2)))
            except Exception:
                continue

    # Sort descending by Jev confidence score, return top 3 routes
    qualified_targets.sort(key=lambda x: x[2], reverse=True)
    return qualified_targets[:3]