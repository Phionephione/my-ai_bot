import praw
import openai
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup Clients
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent="ProblemSolverBot/1.0"
)
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_problem():
    # Scraping r/learnprogramming for "challenge" or "problem"
    subreddit = reddit.subreddit("learnprogramming")
    for submission in subreddit.hot(limit=5):
        if "problem" in submission.title.lower() or "challenge" in submission.title.lower():
            return submission.title, submission.selftext
    return None, None

def generate_solution(title, body):
    prompt = f"Solve this coding problem: '{title}'. Details: {body}. Provide Python code and a markdown explanation."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Main Logic
title, body = get_problem()
if title:
    solution_text = generate_solution(title, body)
    
    # Save to file
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    folder = f"solutions/{date_str}"
    os.makedirs(folder, exist_ok=True)
    
    with open(f"{folder}/solution.py", "w") as f:
        # Simplistic extraction - assume LLM puts code in blocks
        f.write(solution_text) 
    
    print(f"Solved: {title}")