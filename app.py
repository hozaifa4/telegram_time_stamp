# app.py

import asyncio
from flask import Flask, render_template, request
from telegram_analyzer import analyze_links_in_bulk

app = Flask(__name__)

@app.route('/')
def index():
    """ Renders the main input page. """
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
async def process_links():
    """ Handles the form submission for multiple links. """
    links_text = request.form.get('telegram_links', '')
    links = [link.strip() for link in links_text.split('\n') if link.strip()]

    if not links:
        return render_template('error.html', error_message="Please provide at least one link.")

    successful, failed = await analyze_links_in_bulk(links)
    
    return render_template('result.html', successful_results=successful, failed_results=failed)

if __name__ == '__main__':
    # Make sure to install Flask with async support: pip install "Flask[async]"
    app.run(debug=True)
