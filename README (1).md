# Hamilton Ventures Startup Discovery Tool

This web application allows analysts to identify and evaluate promising early-stage (Seed to Series A) companies in the proptech space using Perplexity AI. Users can enter specific inputs, generate structured company profiles, and push selected data to Google Sheets for investment review.

---

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/hamilton-ventures-perplexity-tool.git
cd hamilton-ventures-perplexity-tool
```

---

## Environment Setup

### 2. Create a `.env` File

In the root directory of the project, create a `.env` file with the following keys:

```env
PPLX_API_KEY=your_perplexity_api_key
SPREADSHEET_ID=your_google_sheet_id
GOOGLE_CREDENTIALS_FILE=HV/credentials.json
```

- `PPLX_API_KEY`: Your API key from Perplexity AI
- `SPREADSHEET_ID`: The unique ID of your Google Sheet (found in the URL after `/d/`)
- `GOOGLE_CREDENTIALS_FILE`: Path to your service account credentials JSON file downloaded from Google Cloud Console

---

## Google Sheets Integration

### 3. Enable Sheets API and Share Access

1. Go to Google Cloud Console.
2. Create a new project or use an existing one.
3. Enable Google Sheets API and Google Drive API.
4. Create a Service Account under "IAM & Admin > Service Accounts".
5. Download the JSON key and place it in the `HV/` folder (or as specified in `.env`).
6. Share your Google Sheet with the client email from your service account (read/write access).

---

## Install Dependencies

Create a virtual environment and install required packages:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` should include:

```txt
Flask
requests
python-dotenv
gspread
oauth2client
```

---

## Run the App

Start the Flask server:

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser to use the application.

---

## Features

- Prompt user for startup discovery criteria (sector, geography, etc.)
- Query Perplexity AI API for structured company profiles
- View companies in browser
- Push selected companies to a connected Google Sheet
- Skip unwanted entries
- Retry queries up to 3 times if results are blank or error-prone

---

## Project Structure

```
.
├── HV/
│   └── credentials.json
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── styles.css
├── .env
├── requirements.txt
└── README.md
```

---

## Need Help?

Contact Pranay Nookala at vnookal@purdue.edu or through your GitHub issue tracker.
