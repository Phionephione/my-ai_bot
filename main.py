import os
import requests
import json
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_problem():
    print("Fetching problems from Reddit...")
    url = "https://www.reddit.com/r/learnprogramming/hot.json"
    # Use a custom user agent so Reddit doesn't block us
    headers = {'User-agent': 'MyAIProblemSolver/1.0'}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch Reddit: {response.status_code}")
        return None, None

    data = response.json()
    for post in data['data']['children']:
        title = post['data']['title']
        body = post['data']['selftext']
        
        # Simple filter
        keywords = ["problem", "challenge", "how to", "help with"]
        if any(key in title.lower() for key in keywords) and len(body) > 50:
            print(f"Found potential problem: {title}")
            return title, body
            
    return None, None

def generate_solution(title, body):
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
    date_str = datetime.now().strftime("%Y-%m-%d")
    clean_title = "".join([c if c.isalnum() else "_" for c in title[:30]])
    folder = f"solutions/{date_str}"
    os.makedirs(folder, exist_ok=True)
    
    filename = f"{folder}/{clean_title}.md"
    
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