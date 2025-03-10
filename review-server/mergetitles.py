import json

# Read the reviews file
with open('reviews.json', 'r', encoding='utf-8') as f:
    reviews = json.load(f)

# Read the titles file
with open('titles.json', 'r', encoding='utf-8') as f:
    titles_data = json.load(f)

# Create a dictionary mapping reviewer names to titles
title_map = {item['reviewer']: item['title'] for item in titles_data['reviews']}

# Update each review with its corresponding title
for review in reviews:
    review['title'] = title_map.get(review['username'], review['title'])

# Write the merged data to a new file
with open('merged_reviews.json', 'w', encoding='utf-8') as f:
    json.dump(reviews, f, indent=2, ensure_ascii=False)

print("Merge complete! Check merged_reviews.json for the results.")