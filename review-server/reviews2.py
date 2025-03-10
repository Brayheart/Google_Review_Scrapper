import json
from datetime import datetime
from bs4 import BeautifulSoup
import re
import requests

def calculate_months_ago(date_str):
    """Calculate months between the review date and Jan 30, 2025"""
    try:
        review_date = datetime.strptime(date_str, "%B %Y")
        current_date = datetime(2025, 1, 30)
        months = (current_date.year - review_date.year) * 12 + (current_date.month - review_date.month)
        return months
    except Exception as e:
        print(f"Date parsing error for {date_str}: {e}")
        return 0

def count_stars(paragraph):
    """Count full stars (fa-star not followed by -o)"""
    full_stars = len(re.findall(r'fa-star(?!-o)', paragraph))
    return float(full_stars) if full_stars > 0 else 0.0

def parse_reviews(content):
    soup = BeautifulSoup(content, 'html.parser')
    reviews = []
    
    for review_item in soup.select('.Patient-Review li'):
        paragraphs = review_item.find_all('p')
        if not paragraphs:
            continue
            
        # First paragraph contains stars, name, and date
        first_para = paragraphs[0]
        
        # Get star rating
        rating = count_stars(str(first_para))
        
        # Split the text by <br> tags to get name and date
        parts = [text for text in first_para.stripped_strings]
        
        # Remove empty strings and star ratings
        parts = [part for part in parts if part and not part.startswith('★')]
        
        if len(parts) >= 2:
            username = parts[0]
            date = parts[1]
            
            # Get review text from the second paragraph
            review_text = paragraphs[1].get_text().strip() if len(paragraphs) > 1 else ""
            
            months_ago = calculate_months_ago(date)
            years_ago = months_ago // 12
            
            reviews.append({
                "username": username,
                "review": review_text,
                "rating": rating,
                "months_ago": months_ago,
                "time_text": f"{years_ago} years ago",
                "title": ""
            })
    
    return reviews

# Fetch content from the website
url = "https://www.plasticsandderm.com/patient-reviews.htm"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    reviews = parse_reviews(response.text)
    
    # Write to JSON file
    with open('reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

    print(f"Successfully processed {len(reviews)} reviews")

except requests.RequestException as e:
    print(f"Error fetching the webpage: {e}")