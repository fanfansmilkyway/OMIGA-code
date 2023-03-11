from flask import Flask, request, render_template

app = Flask(__name__)

text = ''

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    return render_template('%s.html' %(text))

@app.route('/lessons')
def contact():
    return render_template('lessons.html')

@app.route('/lessons', methods=['POST'])
def contact_post():
    if request.form['submit_button'] == 'Do Something':
        return render_template('第一课：OMIGA语言的简介与导入.html')
    elif request.form['submit_button'] == 'Do Something Else':
        pass # do something else
    else:
        pass # unknow

app.run(host='0.0.0.0',port='80')