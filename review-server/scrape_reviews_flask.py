from flask import Flask, jsonify, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import threading
import os

app = Flask(__name__)
CORS(app)

# Global variables for scraping state
scraping_done = threading.Event()
current_driver = None

def inject_control_panel(driver):
    try:
        # Create the panel programmatically instead of using innerHTML
        script = """
            // Create container
            const panel = document.createElement('div');
            panel.id = 'control-panel';
            panel.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 999999; font-family: system-ui, -apple-system, sans-serif;';

            // Create instructions
            const instructions = document.createElement('div');
            instructions.style.cssText = 'margin-bottom: 15px; font-size: 14px; color: #333; max-width: 250px;';
            instructions.innerHTML = '1. Please scroll to bottom of reviews page<br>2. Click any "More" buttons to expand reviews<br>3. Click "Done" when finished';
            
            // Create button
            const button = document.createElement('button');
            button.id = 'done-button';
            button.textContent = 'Done';
            button.style.cssText = 'background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 14px;';
            
            // Create status div
            const status = document.createElement('div');
            status.id = 'status';
            status.style.cssText = 'margin-top: 10px; font-size: 12px; color: #666;';
            
            // Add click handler
            button.addEventListener('click', async function() {
                try {
                    button.disabled = true;
                    button.textContent = 'Processing...';
                    status.textContent = 'Notifying server...';
                    
                    const response = await fetch('http://localhost:5000/api/scraping-done', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (!response.ok) {
                        throw new Error('Server response was not ok');
                    }
                    
                    status.textContent = 'Successfully notified server. Please wait...';
                } catch (error) {
                    console.error('Error:', error);
                    status.textContent = 'Error: ' + error.message;
                    button.disabled = false;
                    button.textContent = 'Done';
                }
            });
            
            // Assemble panel
            panel.appendChild(instructions);
            panel.appendChild(button);
            panel.appendChild(status);
            
            // Add to page
            document.body.appendChild(panel);
            console.log('Control panel injected');
        """
        
        # Execute the injection script
        driver.execute_script(script)
        print("Control panel injected successfully")
        
    except Exception as e:
        print(f"Error injecting control panel: {str(e)}")

def scroll_reviews(driver, max_scrolls=30):
    scroll_count = 0
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    
    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
        
        last_height = new_height
        scroll_count += 1
        print(f"Completed scroll {scroll_count}/{max_scrolls}")

def extract_months_ago(time_text):
    if not time_text:
        return 0
    
    time_map = {
        'year': 12,
        'years': 12,
        'month': 1,
        'months': 1,
        'day': 0,
        'days': 0
    }
    
    try:
        number = int(''.join(filter(str.isdigit, time_text)))
        for unit, multiplier in time_map.items():
            if unit in time_text:
                return number * multiplier
    except:
        pass
    return 0

def scrape_google_reviews():
    global current_driver
    url = "https://www.google.com/search?q=parkplazaplasticsurgery&oq=parkplazaplasticsurgery&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MgYIARBFGDwyDwgCEC4YDRivARjHARiABDIGCAMQRRg8MgYIBBBFGDwyBggFEEUYPDIGCAYQRRg8MgYIBxBFGDzSAQc4OTdqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8#lrd=0x89c258ee2c5d7b69:0xf4592dc5fac0f2b,1,,,,"
    
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                            options=chrome_options)
    current_driver = driver
    scraping_done.clear()  # Reset the event
    
    reviews = []
    try:
        driver.get(url)
        print("Waiting for initial page load...")
        time.sleep(5)
        
        print("Injecting control panel...")
        inject_control_panel(driver)
        
        # print("Starting to scroll through reviews...")
        # scroll_reviews(driver)
        
        print("Waiting for user to click Done...")
        scraping_done.wait()  # Wait for the Done button to be clicked
        print("Done button clicked, processing reviews...")
        
        review_elements = driver.find_elements(By.CSS_SELECTOR, "div.WMbnJf.gws-localreviews__google-review")
        print(f"\nFound {len(review_elements)} total reviews")
        
        for i, review in enumerate(review_elements, 1):
            try:
                username = review.find_element(By.CSS_SELECTOR, "div.TSUbDb").text.strip()
                rating_elem = review.find_element(By.CSS_SELECTOR, "span.z3HNkc")
                rating = float(rating_elem.get_attribute("aria-label").split()[1])
                time_text = review.find_element(By.CSS_SELECTOR, "span.dehysf").text.strip()
                months_ago = extract_months_ago(time_text)
                review_text = review.find_element(By.CSS_SELECTOR, ".Jtu6Td").text.strip()
                
                if rating == 5.0:
                    reviews.append({
                        'username': username,
                        'review': review_text,
                        'rating': rating,
                        'months_ago': months_ago,
                        'time_text': time_text,
                        'title': ''
                    })
                    print(f"Processed review {i}/{len(review_elements)} - {username}")
                    
            except Exception as e:
                print(f"Error processing review {i}: {str(e)}")
                continue
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise e
    
    finally:
        driver.quit()
        current_driver = None
    
    with open('reviews.json', 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)
    
    return reviews

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        reviews = scrape_google_reviews()
        return jsonify({"success": True, "reviews": reviews})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/scraping-done', methods=['POST'])
def mark_scraping_done():
    print("Received scraping-done signal")
    scraping_done.set()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)