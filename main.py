import os
import base64
import requests
import google.generativeai as genai

# GitHub Actions Secrets से कीज उठाना
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("MY_PERSONAL_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
FILE_PATH = "index.html"

# Google Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

def read_notes():
    notes_data = {}
    if not os.path.exists('notes'):
        os.makedirs('notes')
    for filename in os.listdir('notes'):
        if filename.endswith(".txt"):
            try:
                with open(os.path.join('notes', filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    notes_data[filename.replace('.txt', '').upper()] = content
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
    return notes_data

def build_website_html(notes_data):
    # Model configuration
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Create a clean, light-themed HTML webpage for 'Shorveer Notes'. Use these notes: {str(notes_data)}. Rules: English only, light background, cards layout, no links, include Ad placeholders, output raw HTML only."
    
    response = model.generate_content(prompt)
    
    # Cleaning the response to keep only HTML
    html = response.text.replace('```html', '').replace('```', '').strip()
    return html

def push_to_github(html_content):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. Check if file exists to get SHA
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha", "") if response.status_code == 200 else ""
    
    data = {
        "message": "Update via GitHub Action",
        "content": base64.b64encode(html_content.encode("utf-8")).decode("utf-8"),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    
    # 2. Push to GitHub
    push_response = requests.put(url, headers=headers, json=data)
    
    if push_response.status_code in [200, 201]:
        print("Success: Website updated!")
    else:
        print(f"Failed! Status Code: {push_response.status_code}")
        print(f"Response: {push_response.text}")

if __name__ == "__main__":
    print("Reading notes...")
    notes = read_notes()
    if notes:
        print("Generating HTML...")
        html = build_website_html(notes)
        push_to_github(html)
    else:
        print("No notes found.")
