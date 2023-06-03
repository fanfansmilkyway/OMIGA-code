# Fix mode
from flask import Flask, render_template, redirect, url_for, request
import os

CONTENT = os.environ['CONTENT_DIR']

app = Flask(__name__, template_folder='{0}/templates'.format(CONTENT), static_folder='{0}/static'.format(CONTENT))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not request.path.endswith('/'):
        return redirect(url_for('catch_all', path=''))
    return render_template('fix.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80')