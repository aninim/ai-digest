import os
import json
import datetime
import shutil
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OUTPUT_PATH = "docs/digest/data.json"
HISTORY_PATH = "docs/digest/history"

client = genai.Client(api_key=GEMINI_API_KEY)

# Load sources
with open("digest/sources.json") as f:
    sources = json.load(f)

today = datetime.date.today().isoformat()

PROMPT = f"""
You are an AI research analyst. Today is {today}.

Search and synthesize the most important AI developments from the last 24 hours.
Focus on these sources and topics: {json.dumps(sources, indent=2)}

Return ONLY valid JSON. No markdown, no explanation, no backticks. Exactly this structure:

{{
  "date": "{today}",
  "top_story": "one sentence max — the single most important thing today",
  "tools": [
    {{"name": "", "summary": "", "url": "", "relevance": ""}}
  ],
  "hacks": [
    {{"title": "", "description": "", "source": ""}}
  ],
  "use_cases": [
    {{"title": "", "description": "", "applicable_to": ""}}
  ],
  "big_moves": [
    {{"who": "", "what": "", "why_it_matters": ""}}
  ],
  "deprecated": [
    {{"what": "", "note": ""}}
  ]
}}

Rules:
- Max 5 items per category. 3 is fine if there's nothing worth including.
- Be terse. One sentence per field unless critical context needed.
- Relevance field: tag as one of [coding, CV, education, prompting, agents, general]
- applicable_to field: tag as one of [Clodi, Codi, dads42, kids-apps, general]
- If nothing notable happened in a category, return empty array []
- Prioritize signal over volume. No fluff.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=PROMPT,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)

# Parse and validate
raw = response.text.strip()
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    raw = raw.strip()
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"❌ Gemini returned invalid JSON: {e}")
    print(f"Raw response:\n{raw}")
    raise

# Write daily output
os.makedirs(HISTORY_PATH, exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    json.dump(data, f, indent=2)

# Archive snapshot
snapshot_path = f"{HISTORY_PATH}/{today}.json"
shutil.copy(OUTPUT_PATH, snapshot_path)

print(f"✅ Digest written for {today}")
