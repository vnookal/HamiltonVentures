from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests
import json
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from time import sleep
from uuid import uuid4
import webbrowser

app = Flask(__name__)
app.secret_key = "startup-selector-" + str(uuid4())

load_dotenv()

API_KEY = os.getenv("PPLX_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
NUM_COMPANIES = 5
RETRY_ATTEMPTS = 1

FIELDS = [
    "Company Name", "Website", "HQ Location", "Year Founded", "Proptech Sub-Sector",
    "Problem/Solution", "Target Audience", "Competitors", "Business Model", "Technology Stack",
    "Current Funding Stage", "Annual Revenue", "YoY Growth Rate", "Revenue Over Last 4 Years",
    "Total Funding to Date", "Last Round Valuation", "Last Funding Date",
    "Current Investors + Amount Invested", "Leadership Team", "Email Address", "LinkedIn", "Notes"
]

def build_prompt(industry, stage, region):
    return f"""
    List {NUM_COMPANIES} DIFFERENT real {stage}-stage startups in the {industry} industry based in {region}.
    For each company, return the following structured JSON fields:
    {', '.join(['- ' + field for field in FIELDS])}

    Format the output as a JSON array with exactly {NUM_COMPANIES} entries. Do not include any commentary or markdown. 
    If a field is unknown, leave it as an empty string.
    """

def query_perplexity(industry, stage, region, temperature=0.2):
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are a startup research assistant that outputs clean structured JSON."},
            {"role": "user", "content": build_prompt(industry, stage, region)}
        ],
        "temperature": temperature
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)

    try:
        raw = response.json()["choices"][0]["message"]["content"].strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        return json.loads(raw)
    except:
        return []

def merge_company_data(existing, new):
    return {field: new.get(field) or existing.get(field, "") for field in FIELDS}

def get_gsheet():
    creds = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1

def append_single_company(sheet, company):
    headers = sheet.row_values(1)
    row = [''] * len(headers)
    for i, header in enumerate(headers):
        if header in company:
            row[i] = company[header]
    sheet.append_row(row)

def fetch_complete_company_data(industry, stage, region, temperature):
    merged = [{} for _ in range(NUM_COMPANIES)]
    logs = []

    for attempt in range(RETRY_ATTEMPTS):
        logs.append(f"🔁 Attempt {attempt + 1} of {RETRY_ATTEMPTS}")
        batch = query_perplexity(industry, stage, region, temperature)

        for i, new_data in enumerate(batch[:NUM_COMPANIES]):
            merged[i] = merge_company_data(merged[i], new_data)

        if all(all(company.get(field) for field in FIELDS) for company in merged):
            logs.append("✅ All fields filled — stopping early.")
            break
        sleep(1)

    session["logs"] = logs
    return merged

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        industry = request.form["industry"]
        stage = request.form["stage"]
        region = request.form["region"]
        temp = request.form["temperature"]
        try:
            temperature = float(temp) if temp else 0.2
        except ValueError:
            temperature = 0.2

        companies = fetch_complete_company_data(industry, stage, region, temperature)
        session["companies"] = companies
        session["skipped"] = []
        session["approved"] = []
        return redirect(url_for("review"))

    return render_template("form.html")

@app.route("/review", methods=["GET"])
def review():
    companies = session.get("companies", [])
    skipped = set(session.get("skipped", []))
    approved = set(session.get("approved", []))
    logs = session.get("logs", [])

    visible_companies = [
        (i, company) for i, company in enumerate(companies)
        if i not in skipped and i not in approved
    ]

    return render_template("review.html", companies=visible_companies, fields=FIELDS, logs=logs)

@app.route("/approve/<int:index>", methods=["POST"])
def approve(index):
    companies = session.get("companies", [])
    if 0 <= index < len(companies):
        sheet = get_gsheet()
        append_single_company(sheet, companies[index])

        approved = set(session.get("approved", []))
        approved.add(index)
        session["approved"] = list(approved)

    return redirect(url_for("review"))

@app.route("/skip/<int:index>", methods=["POST"])
def skip(index):
    skipped = set(session.get("skipped", []))
    skipped.add(index)
    session["skipped"] = list(skipped)
    return redirect(url_for("review"))

@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)