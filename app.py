from flask import Flask, request, render_template, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
        
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def my_form_post():
    if request.method == 'POST':
        text = request.form['text']
        return render_template('%s.html' %(text))
    return render_template('index.html')
    
@app.route('/lessons', methods=['GET','POST'])
def contact_post():
    if request.method == 'POST':
        if request.form['submit_button'] == '第一课：OMIGA语言的简介与导入':
            return render_template('第一课：OMIGA语言的简介与导入.html')
        if request.form['submit_button'] == '第二课：OMIGA语言的基本词语与语句':
            return render_template('第二课：OMIGA语言的基本词语与语句.html')
        if request.form['submit_button'] == '第三课：teriyoga! ditaiyosu! 你们好！初次见面！':
            return render_template('第三课：teriyoga! ditaiyosu! 你们好！初次见面！.html')
        if request.form['submit_button'] == '第四课：dv ing sihoma tsu loyode 班级中的规则':
            return render_template('第四课：dv ing sihoma tsu loyode 班级中的规则.html')
        if request.form['submit_button'] == '第五课：noku, misu, kongmi 没有，一些，很多':
            return render_template('第五课：noku, misu, kongmi 没有，一些，很多.html')
    return render_template('lessons.html')
    
def allowed_file(filename):
        return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# set environment variable to your folder's path
UPLOAD_FOLDER = os.environ['UPLOAD_DIR']
ALLOWED_EXTENSIONS = {'txt','png','jpg','jpeg','gif','mp3','mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1000 * 1000

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
    return render_template('uploads.html')

app.run(host='0.0.0.0',port='80')