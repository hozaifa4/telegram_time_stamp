# app.py

import asyncio
from flask import Flask, render_template, request
# telegram_analyzer.py থেকে নতুন ফাংশনটি ইম্পোর্ট করা হচ্ছে
from telegram_analyzer import get_details_from_link

app = Flask(__name__)

@app.route('/')
def index():
    """ মূল ইনপুট পেজটি দেখানোর জন্য। """
    return render_template('index.html')

@app.route('/get_details', methods=['POST'])
async def process_form():
    """ ফর্ম থেকে লিঙ্ক নিয়ে ফলাফল দেখানোর জন্য। """
    # ফর্ম থেকে এখন 'telegram_link' নেওয়া হচ্ছে
    link = request.form.get('telegram_link')
    
    # লিঙ্ক থেকে তথ্য আনার জন্য নতুন ফাংশনটি কল করা হচ্ছে
    result = await get_details_from_link(link)
    
    # ফলাফল ডিকশনারি হলে result.html, নাহলে error.html দেখানো হচ্ছে
    if isinstance(result, dict):
        return render_template('result.html', details=result)
    else:
        return render_template('error.html', error_message=result)

if __name__ == '__main__':
    # Flask-কে async সমর্থন সহ ইনস্টল করতে হবে: pip install "Flask[async]"
    app.run(debug=True)