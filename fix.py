# Fix mode
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def fix():
    return render_template('fix.html')

app.run(host='0.0.0.0', port='80')