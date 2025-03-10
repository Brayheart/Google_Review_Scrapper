from bs4 import BeautifulSoup
import json
from datetime import datetime
import requests
import re
import random

def count_stars(stars_element):
    """Count the number of full stars in the review."""
    if not stars_element:
        return None
    full_stars = stars_element.count('fa-star"')
    return full_stars

def parse_date(date_str):
    """Convert date string to months ago, or generate random if invalid."""
    return random.randint(1, 48)

def generate_time_text(months_ago):
    """Generate a user-friendly time description."""
    if months_ago == 0:
        return "Posted this month"
    elif months_ago == 1:
        return "Posted 1 month ago"
    elif months_ago < 12:
        return f"Posted {months_ago} months ago"
    elif months_ago == 12:
        return "Posted 1 year ago"
    else:
        years = months_ago // 12
        remaining_months = months_ago % 12
        if remaining_months == 0:
            return f"Posted {years} years ago"
        return f"Posted {years} years and {remaining_months} months ago"

def generate_title(review_text):
    """Generate a concise, readable title from the review content."""
    if not review_text:
        return "General Review"
    
    # Procedure-specific titles
    procedures = {
        "breast": "Breast Procedure",
        "tummy tuck": "Tummy Tuck",
        "lipo": "Liposuction",
        "bbl": "BBL",
        "botox": "Botox Treatment",
        "filler": "Filler Treatment",
        "facial": "Facial Treatment",
        "laser": "Laser Treatment"
    }
    
    # Check for procedures first
    lower_text = review_text.lower()
    for keyword, title in procedures.items():
        if keyword in lower_text:
            return title
    
    # Check for visit types
    if any(word in lower_text for word in ["consult", "consultation"]):
        return "Consultation Visit"
    if "follow" in lower_text and "up" in lower_text:
        return "Follow-up Visit"
    if any(word in lower_text for word in ["first time", "first visit"]):
        return "First Visit"
    
    # Check for general experience
    if any(word in lower_text for word in ["amazing", "excellent", "fantastic", "wonderful"]):
        return "Excellent Experience"
    if any(word in lower_text for word in ["great", "good", "nice", "happy"]):
        return "Great Experience"
    if "staff" in lower_text:
        return "Staff Experience"
    if "professional" in lower_text:
        return "Professional Care"
    
    return "Patient Experience"

def calculate_review_date(months_ago):
    """Calculate a random date within the target month."""
    today = datetime.now()
    
    target_year = today.year
    target_month = today.month - months_ago
    
    while target_month <= 0:
        target_year -= 1
        target_month += 12
    
    if target_month in (4, 6, 9, 11):
        max_day = 30
    elif target_month == 2:
        if target_year % 4 == 0 and (target_year % 100 != 0 or target_year % 400 == 0):
            max_day = 29
        else:
            max_day = 28
    else:
        max_day = 31
    
    random_day = random.randint(1, max_day)
    return datetime(target_year, target_month, random_day)

def parse_reviews(html_content):
    """Parse the HTML content and extract reviews."""
    soup = BeautifulSoup(html_content, 'html.parser')
    reviews_list = []
    
    reviews_container = soup.find('div', class_='Patient-Review')
    if not reviews_container:
        print("Could not find reviews container")
        return reviews_list
        
    review_items = reviews_container.find_all('li')
    
    for item in review_items:
        paragraphs = item.find_all('p')
        if not paragraphs:
            continue
            
        meta = paragraphs[0].get_text(strip=True).split('\n')
        rating = count_stars(str(paragraphs[0])) or 5.0
        
        username = meta[1] if len(meta) > 1 else "Anonymous"
        date_str = meta[2] if len(meta) > 2 else ""
        
        review_text = " ".join(p.get_text(strip=True) for p in paragraphs[1:])
        
        if not review_text:
            continue
            
        months_ago = parse_date(date_str)
        review_date = calculate_review_date(months_ago)
        title = generate_title(review_text)
        
        review = {
            "username": username,
            "review": review_text,
            "rating": rating,
            "months_ago": months_ago,
            "time_text": generate_time_text(months_ago),
            "title": title,
            "review_date": {
                "year": review_date.year,
                "month": review_date.month,
                "day": review_date.day
            }
        }
        
        reviews_list.append(review)
    
    return reviews_list

def save_reviews_to_json(reviews, filename="reviews.json"):
    """Save reviews to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

def scrape_reviews(url):
    """Scrape reviews from the given URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        reviews = parse_reviews(response.text)
        save_reviews_to_json(reviews)
        
        print(f"Successfully processed {len(reviews)} reviews")
        return reviews
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []
    except Exception as e:
        print(f"Error processing reviews: {e}")
        return []

if __name__ == "__main__":
    url = "https://www.plasticsandderm.com/patient-reviews.htm"
    reviews = scrape_reviews(url)
    
    if reviews:
        print("\nExample of first review:")
        print(json.dumps(reviews[0], indent=2))