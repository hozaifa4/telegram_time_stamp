import asyncio
from flask import Flask, render_template, request
from telegram_analyzer import get_message_details

app = Flask(__name__)

@app.route('/')
def index():
    """ Renders the main input page. """
    return render_template('index.html')

@app.route('/get_details', methods=['POST'])
async def process_form():
    """ Handles the form submission to get message details. """
    username = request.form.get('public_username')
    message_id = request.form.get('message_id')
    
    result = await get_message_details(username, message_id)
    
    if isinstance(result, dict):
        return render_template('result.html', details=result)
    else:
        return render_template('error.html', error_message=result)

if __name__ == '__main__':
    # Remember to install Flask with async support: pip install "Flask[async]"
    app.run(debug=True)
