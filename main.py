from flask import Flask, render_template, request
from scraper import search_data

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None

    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        college = request.form['college']

        result = search_data(name, city, college)

    return render_template('index.html', result=result)


import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))