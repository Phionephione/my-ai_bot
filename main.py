import os
import requests
import json
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Load API keys from .env file (for local testing)
load_dotenv()

# Initialize OpenAI
# Note: In GitHub Actions, we will set this as an environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_problem():
    """Scrapes hot posts from r/learnprogramming to find a coding problem."""
    print("Fetching problems from Reddit...")
    url = "https://www.reddit.com/r/learnprogramming/hot.json"
    # Reddit blocks requests without a custom User-Agent
    headers = {'User-agent': 'MyAIProblemSolver/1.0'}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch Reddit: {response.status_code}")
        return None, None

    data = response.json()
    for post in data['data']['children']:
        title = post['data']['title']
        body = post['data']['selftext']
        
        # Filter: Look for posts asking for help/challenges
        keywords = ["problem", "challenge", "how to", "help with"]
        if any(key in title.lower() for key in keywords) and len(body) > 50:
            print(f"Found potential problem: {title}")
            return title, body
            
    return None, None

def generate_solution(title, body):
    """Sends the problem to GPT-4o-mini to get a clean solution."""
    print("Asking AI for a solution...")
    prompt = f"""
    You are an expert coder. 
    Analyze the following coding problem and provide:
    1. A brief explanation of the solution.
    2. The complete code implementation in a markdown block.
    
    Problem Title: {title}
    Problem Details: {body}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def save_solution(title, content):
    """Saves the solution as a Markdown file."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Clean the title for use as a filename
    clean_title = "".join([c if c.isalnum() else "_" for c in title[:30]])
    folder = f"solutions/{date_str}"
    os.makedirs(folder, exist_ok=True)
    
    filename = f"{folder}/{clean_title}.md"
    
    # Don't overwrite if it already exists
    if os.path.exists(filename):
        print("Solution for today already exists.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Solution: {title}\n\n")
        f.write(f"Date: {date_str}\n\n")
        f.write(content)
        
    print(f"Successfully saved to {filename}")

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found!")
    else:
        title, body = get_problem()
        if title:
            solution = generate_solution(title, body)
            save_solution(title, solution)
        else:
            print("No suitable problem found today.")
