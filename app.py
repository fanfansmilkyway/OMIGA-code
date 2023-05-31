# Built-in
import os
from git import Repo
# Need to install(not built-in)
from flask import Flask, request, render_template, flash, redirect, url_for, session
import jieba
from werkzeug.utils import secure_filename
import duckdb

# Environment Variables
USER_DATA = os.environ['USER_DATA_DIR']
CONTENT = os.environ['CONTENT_DIR']

# Init
app = Flask(__name__, template_folder='{0}/templates'.format(CONTENT), static_folder='{0}/static'.format(CONTENT))

app.secret_key = 'q776NkmVYq3vjZwaJn9drw'

# Database
con = duckdb.connect("{0}/userdata.db".format(USER_DATA))
# Create database if it not exists
try:
    con.sql("CREATE TABLE users(Id int primary key, Name varchar(255), Password varchar(255), Number varchar(255))")
    con.sql("CREATE SEQUENCE seq_id START 1")
except:
    pass

# Github
repo = Repo(CONTENT)
g = repo.git

# Index pgae
@app.route('/', methods=['GET','POST'])
def my_form_post(): 
    return render_template('index.html')
    
@app.route('/words', methods=['GET', 'POST'])
def words():
    if request.method == 'POST':
        # Choose searching mode
        if request.form['submit_button'] == '直接查找':
            return redirect('/search-word-with-OMIGA')
        if request.form['submit_button'] == '用中文查找':
            return redirect('/search-word-with-chinese')
    return render_template('words.html')
    
@app.route('/search-word-with-OMIGA', methods=['GET', 'POST'])
def search_word_with_OMIGA():
    if request.method == 'POST':
        # Check if word exists
        try:
            # If yes, show the meaning of the word
            session['word'] = request.form['word']
            return render_template('{0}.html'.format(session['word']))
        except:
            # If not, show error message
            return '未找到此单词'
    return render_template('search-word-with-OMIGA.html')

# These are not words
NOT_WORD = ['.DS_Store', '.gitignore', '第一课：OMIGA语言的简介与导入.html', '第二课：OMIGA语言的基本词语与语句.html',\
    '第三课：teriyoga! ditaiyosu! 你们好！初次见面！.html', '第四课：dv ing sihoma tsu loyode 班级中的规则.html',\
    '第五课：noku, misu, kongmi 没有，一些，很多.html','fix.html','index.html','lessons.html','sign_in.html',\
    'sign_up.html','uploads.html','users.html', 'search-word-with-chinese.html', 'search-word-with-OMIGA.html'\
    ,'words.html']

@app.route('/search-word-with-chinese', methods=['GET', 'POST'])
def search_word_with_chinese():
    if request.method == 'POST':
        session['word'] = request.form['word']
        possible_words = []

        for filename in os.listdir('{0}/templates'.format(CONTENT)):
            if filename not in NOT_WORD: # Check if the file is a word or not
                with open("{0}/templates/{1}".format(CONTENT, filename), "r") as f:
                    # Read it
                    text = f.read()
                    f.close()
                    # Cut the sentences with jieba
                    if '{0}'.format(session['word']) in list(jieba.cut_for_search(text)):
                        # Find possible words
                        possible_words.append(filename)
        # Output
        possible_words = [file_name[:-5] for file_name in possible_words]
        result = ', '.join(possible_words)
        # Check if possible words exist
        if result != '':
            # If yes, output
            return '''
            <h1>找到以下可能的单词</h1>
            <h3>{0}</h3>
            '''.format(result)  
        if result == '':
            # If not, show error message
            return '<h1>未找到单词'
    return render_template('search-word-with-chinese.html')

@app.route('/lessons', methods=['GET','POST'])
def contact_post():
    if request.method == 'POST':
        # Choose lessons
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

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Convert str to html files
        session['title'] = str(request.form['title'])
        session['content'] = request.form['content']
        text = repr(str(session['content']))
        text = text.replace('\\r\\n', '<br>')
        text = text.replace("'", '')
        # Write html files
        f = open('{0}/templates/{1}.html'.format(CONTENT, session['title']), 'a')
        f.write('{0}'.format('<h1>'+session['title']+'</h1>'))
        f.write('{0}'.format(text))
        f.close()
        # Push them to github
        g.add("--all")
        g.commit("-m auto update {0}".format(session['title']))
        g.push()
        return '<h1>成功添加单词</h1>'
    return render_template('uploads.html')

@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        # Check if the user exists
        if con.sql("SELECT EXISTS(SELECT * FROM users WHERE Name='{0}')".format(user_name)).fetchall()[0] == (False,):
            # If yes, create a new account
            con.sql("INSERT INTO users (Id, Name, Password, Number) VALUES (nextval('seq_id'), '{0}', '{1}', '0')".format(user_name, password))
            return '<h1>成功创建账户</h1>'
        if con.sql("SELECT EXISTS(SELECT * FROM users WHERE Name='{0}')".format(user_name)).fetchall()[0] == (True,):
            # If not, show error message
            return '<h1>此用户名已经被使用</h1>'
    return render_template('sign_up.html')

@app.route('/sign_in', methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = str(request.form['password'])
        # Check if the user exists
        if con.sql("SELECT EXISTS(SELECT * FROM users WHERE Name='{0}')".format(user_name)).fetchall()[0] == (True,):
            # If yes, read the password in database
            real_password = con.sql("SELECT Password FROM users WHERE Name='{0}'".\
                format(user_name)).df()
            real_password = str(real_password['Password'][0])
        if con.sql("SELECT EXISTS(SELECT * FROM users WHERE Name='{0}')".format(user_name)).fetchall()[0] == (False,):
            # If not, show error message
            return '<h1>此用户不存在</h1>'
        # Check if the password is correct
        if password == real_password:
            session['username'] = user_name
            return redirect('/users')
        else:
            return '<h1>密码错误</h1>'

    return render_template('sign_in.html')
            
@app.route('/users', methods=['GET','POST'])
def users():
    # Check if the user sign in
    try:
        session['username']
    except:
        # If not, redirect to /sign_in to sign in 
        return redirect('/sign_in')
    else:
        # If yes, show the user page
        number = con.sql("SELECT Number FROM users WHERE Name='{0}'".format(session['username'])).df()
        number = str(number['Number'][0])
    
    # Change user data
    if request.method == 'POST':
        new_number = request.form['number']
        con.sql("UPDATE users SET number={0} WHERE Name='{1}'".format(new_number, session['username']))
        return '<h1>成功更改</h1>'

    return render_template('users.html', user_name=session['username'], num=number)

# Don't open debug mode
app.run(host='0.0.0.0',port='80')