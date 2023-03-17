from flask import Flask, request, render_template, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
        
app = Flask(__name__)

text = ''

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    if request.method == 'POST':
        text = request.form['text']
        return render_template('%s.html' %(text))
    return render_template('index.html')
    
@app.route('/lessons')
def contact():
    return render_template('lessons.html')

@app.route('/lessons', methods=['POST'])
def contact_post():
    if request.form['submit_button'] == '第一课：OMIGA语言的简介与导入':
        return render_template('第一课：OMIGA语言的简介与导入.html')
    if request.form['submit_button'] == '第二课：OMIGA语言的基本词语与语句':
        return render_template('第二课：OMIGA语言的基本词语与语句.html')

def allowed_file(filename):
        return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload Files</title>
    <h1>Upload Files</h1>
    <p>Please upload .txt file</p>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit>
    </form>
    '''

app.run(host='0.0.0.0',port='80')