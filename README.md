# Google Review Scraper

React/Flask application with Selenium-powered Google review scraping, interactive DOM control panel, and intelligent title generation algorithm. Features async state management, RESTful API integration, and responsive UI built with shadcn components and Tailwind CSS.

## 🚀 Features

- **Automated Review Scraping**: Uses Selenium WebDriver to extract 5-star reviews from Google.
- **Interactive Scraping Control**: Injects a custom control panel into the browser for user-guided scraping.
- **Smart Title Generation**: Automatically generates relevant titles based on review content.
- **Modern React Frontend**: Built with functional components and hooks for state management.
- **Elegant UI**: Responsive design with Tailwind CSS and shadcn UI components.
- **RESTful API**: Flask backend with endpoints for scraping and uploading reviews.

## 🛠️ Tech Stack

- **Frontend**: React, Tailwind CSS, shadcn/ui, Lucide React icons
- **Backend**: Flask, Flask-CORS
- **Web Scraping**: Selenium WebDriver, ChromeDriver
- **State Management**: React Hooks (useState)
- **HTTP Requests**: Fetch API

## 🔧 Setup and Installation

### Prerequisites
- Node.js and npm
- Python 3.7+
- Chrome browser

### Backend Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/google-review-scraper.git
   cd google-review-scraper
   ```

2. Set up Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies
   ```bash
   pip install flask flask-cors selenium webdriver-manager
   ```

4. Start the Flask server
   ```bash
   python app.py
   ```

### Frontend Setup
1. Install Node dependencies
   ```bash
   npm install
   ```

2. Start the React development server
   ```bash
   npm start
   ```

3. Access the application at `http://localhost:3000`

## 📝 Usage

1. Launch the application and enter a Google Reviews URL (or use the default one for Park Plaza Plastic Surgery).
2. Click "Scrape Reviews" to start the scraping process.
3. In the Chrome window that opens, scroll through all reviews and expand any "More" buttons to reveal full review text.
4. Click the "Done" button in the control panel when finished.
5. Review the scraped content in the application interface.
6. Click "Upload All Reviews" to store the reviews (currently configured to use a local endpoint).

## 🔄 Workflow

```
User Interface → Flask API → Selenium WebDriver → Google Reviews Page
                                      ↓
Review Processing ← Title Generation ← Extracted Reviews
      ↓
Formatted Display → Optional Upload to WordPress
```

## 🔒 Security Notes

This application is designed for demonstration purposes. In a production environment:

- Implement proper authentication and API key management
- Add rate limiting to prevent abuse
- Consider using a headless browser configuration for scraping
- Add proper error handling and logging

## 📜 License

MIT

## 👤 Contact

For any inquiries, please open an issue on this repository.
