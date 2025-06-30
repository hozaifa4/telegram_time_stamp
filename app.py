# app.py

import asyncio
from flask import Flask, render_template, request
from telegram_analyzer import get_details_from_link

app = Flask(__name__)

@app.route('/')
def index():
    """ Renders the main input page. """
    return render_template('index.html')

@app.route('/get_details', methods=['POST'])
async def process_form():
    """ Handles the form submission to get message details from a link. """
    link = request.form.get('telegram_link')
    
    result = await get_details_from_link(link)
    
    if isinstance(result, dict):
        return render_template('result.html', details=result)
    else:
        return render_template('error.html', error_message=result)

if __name__ == '__main__':
    # Make sure to install Flask with async support: pip install "Flask[async]"
    app.run(debug=True)
