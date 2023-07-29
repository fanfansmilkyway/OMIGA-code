# Built-in
import os
from datetime import date
from git import Repo
# Need to install(not built-in)
from flask import Flask, request, render_template, redirect, session
import duckdb

# Environment Variables
USER_DATA = os.environ['USER_DATA_DIR'] # 'user data' folder's location
CONTENT = os.environ['CONTENT_DIR'] # 'content' folder's location
GITHUB = os.environ['GITHUB'] # 0 or 1, means github fuction is off or on.

app = Flask(__name__, template_folder='{0}/templates'.format(CONTENT), static_folder='{0}/static'.format(CONTENT))
app.secret_key = 'q776NkmVYq3vjZwaJn9drw'

# Database
OMIGA_dictionary = duckdb.connect('{0}/dictionary.db'.format(CONTENT))
con = duckdb.connect("{0}/userdata.db".format(USER_DATA))
# Create database if it not exists
con.sql("CREATE TABLE IF NOT EXISTS users(Id int primary key, Name varchar(255), Password varchar(255), Number varchar(255))")
con.sql("CREATE SEQUENCE IF NOT EXISTS seq_id START 1")
OMIGA_dictionary.sql("CREATE TABLE IF NOT EXISTS dictionary(Id int primary key, Word varchar(255), Meaning varchar(255))")
OMIGA_dictionary.sql("CREATE SEQUENCE IF NOT EXISTS seq_id START 1")

# Github
if GITHUB == 1:
    repo = Repo(CONTENT)
    g = repo.git

# Main pgae
@app.route('/', methods=['GET','POST'])
def index(): 
    return render_template('index.html')
    
@app.route('/words', methods=['GET', 'POST'])
def words():
    if request.method == 'POST':
        # Choose searching mode
        if request.form['submit_button'] == '直接查找':
            return redirect('/words/search-word-with-OMIGA')
        if request.form['submit_button'] == '查找单词的解释':
            return redirect('/words/search-word-with-meaning')
    return render_template('words.html')
    
@app.route('/words/search-word-with-OMIGA', methods=['GET', 'POST'])
def search_word_with_OMIGA():
    if request.method == 'POST':
        word = request.form['word']
        # Check if word exists
        if OMIGA_dictionary.sql("SELECT EXISTS(SELECT * FROM dictionary WHERE Word='{0}')".format(word)).fetchall()[0] == (True,):
            # If yes, show the meaning of the word
            meaning = OMIGA_dictionary.sql("SELECT Meaning FROM dictionary WHERE Word='{0}'".format(word)).df()['Meaning'][0]
            text = '<h1>' + word + '</h1>' + repr(meaning)
            text = text.replace('\\r\\n', '<br>')
            text = text.replace("'", '')
            text = '''<head>
        <title>单词查询</title>
        <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
    </head>
            ''' + text
            return text
        else:
            # If not, show error message
            return "<h1>未找到此单词</h1>"
    return render_template('search-word-with-OMIGA.html')

@app.route('/words/search-word-with-meaning', methods=['GET', 'POST'])
def search_word_with_chinese():
    if request.method == 'POST':
        search_expresion = request.form['search']
        possible_words = []
        # Read ALL words from dataset
        meanings = list(OMIGA_dictionary.sql("SELECT Meaning FROM dictionary").fetchall())
        words = list(OMIGA_dictionary.sql("SELECT Word FROM dictionary").fetchall())
        # Search
        for word in words:
            meaning = meanings[words.index(word)][0]
            word = word[0]
            if search_expresion in meaning:
                possible_words.append(word)
        result = ', '.join(possible_words)
        # Check if possible words exists
        if result != '':
            # If yes, return the result
                return "<h1>找到以下可能的单词</h1> <br> <h3>{0}</h3>".format(result)
        if result == '':
            # If not, show error message
            return '<h1>未找到单词'
    return render_template('search-word-with-meaning.html')

@app.route('/lessons', methods=['GET','POST'])
def lessons():
    if request.method == 'POST':
        # Choose lesson
        if request.form['submit_button'] == '第一课：OMIGA语言的简介与导入':
            return render_template('lessons/第一课：OMIGA语言的简介与导入.html')
        if request.form['submit_button'] == '第二课：OMIGA语言的基本词语与语句':
            return render_template('lessons/第二课：OMIGA语言的基本词语与语句.html')
        if request.form['submit_button'] == '第三课：人称代词，基本的问候语，所有格':
            return render_template('lessons/第三课：人称代词，基本的问候语，所有格.html')
        if request.form['submit_button'] == '第四课：teriyoga! ditaiyosu! 你们好！初次见面！':
            return render_template('lessons/第四课：teriyoga! ditaiyosu! 你们好！初次见面！.html')
        if request.form['submit_button'] == '第五课：dv ing sihoma tsu loyode 班级中的规则':
            return render_template('lessons/第五课：dv ing sihoma tsu loyode 班级中的规则.html')
        if request.form['submit_button'] == '第六课：noku, misu, kongmi 没有，一些，很多':
            return render_template('lessons/第六课：noku, misu, kongmi 没有，一些，很多.html')
    return render_template('lessons.html')

# Function: Convert txt file to html
def txt_web_show(filepath):
    filepath = CONTENT + '/templates/passages/' + filepath
    with open(filepath, 'r') as f:
        text = f.read()
        f.close()
    text = repr(text)
    text = text.replace('\\n', '<br>')
    text = text.replace('\\t', '&emsp;&emsp;')
    text = text.replace("\\'", "'")
    text = '<p>' + text + '</p>'
    output = '''<head>
        <title>OMIGA文章阅读</title>
        <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">

    </head>
            ''' + text
    return output
    
@app.route('/passages', methods=['GET', 'POST'])
def passages():
    if request.method == 'POST':
        # Choose passage
        if request.form['submit_button'] == 'hotini hegude 校园政府':
            return redirect('/passages/hotini-hegude')
        if request.form['submit_button'] == 'remu o OMIGA OMIGA之歌':
            return txt_web_show('songs/remu-o-OMIGA.txt')
        if request.form['submit_button'] == 'HUNTERxHUNTER Departure OP 全职猎人 Departure 主题曲':
            return txt_web_show('songs/HUNTERxHUNTER--Departure.txt')
    return render_template('passages.html')

@app.route('/passages/hotini-hegude', methods=['GET', 'POST'])
def hotini_hegude():
    if request.method == 'POST':
        # Choose chapter
        if request.form['submit_button'] == '1.memode':
            return txt_web_show('hotini-hegude/yi-memode.txt')
        if request.form['submit_button'] == '2.honakode':
            return txt_web_show('hotini-hegude/nv-honakode.txt')
        if request.form['submit_button'] == '3.goku':
            return txt_web_show('hotini-hegude/sv-goku.txt')
    return render_template('hotini-hegude.html')

@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
    if request.method == 'POST':
        # Useful Function: Check if word already existed
        if request.form['submit_button'] == '检查':
            if OMIGA_dictionary.sql("SELECT EXISTS(SELECT * FROM dictionary WHERE Word='{0}')".format(request.form['check'])).fetchall()[0] == (True, ):
                # If yes, show error message
                return '<h1>此单词已经存在，你将无法添加，你只能去<a href="/edit">omiga.org/edit</a>修改单词</h1>'
            else:
                # If not:
                return '<h1>这是一个安全的单词，你可以添加</h1>'
        if request.form['submit_button'] == '完成':
            title = str(request.form['title'])
            if OMIGA_dictionary.sql("SELECT EXISTS(SELECT * FROM dictionary WHERE Word='{0}')".format(title)).fetchall()[0] == (True, ):
                return '<h1>此单词已经存在，你将无法添加，你只能去<a href="/edit">omiga.org/edit</a>修改单词</h1>'
            content = str(request.form['content'])
            # Check if the content is empty
            if title == '' or content == '':
                return '<h1>不能添加空的单词！！</h1>'
            OMIGA_dictionary.sql("INSERT INTO dictionary (Id, Word, Meaning) VALUES (nextval('seq_id'), '{0}', '{1}')".format(title, content))
            # Push dataset to github
            if GITHUB == 1:
                g.add("--all")
                g.commit("-m auto update {0} from omiga.org".format(request.form['title']))
                g.push()
            return '<h1>成功添加单词</h1>'
    return render_template('uploads.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        word = str(request.form['word'])
        # Check if the word exists
        if OMIGA_dictionary.sql("SELECT EXISTS(SELECT * FROM dictionary WHERE Word='{0}')".format(word)).fetchall()[0] == (True,):
            # If yes, redirect to /edit/editing
            session['word'] = word
            return redirect('/edit/editing')
        else:
            # If not, show error message
            return '<h1>此单词还未存在于字典中，若想添加此单词请前往<a href="/uploads">omiga.org/uploads</a></h1>'
    return render_template('edit.html')

@app.route('/edit/editing', methods=['GET', 'POST'])
def editing():
    # Read from dataset
    content = OMIGA_dictionary.sql("SELECT Meaning FROM dictionary WHERE Word='{0}'".format(session['word'])).df()['Meaning'][0]
    if request.method == 'POST':
        if request.form['submit_button'] == '完成':
            edited_content = request.form['content']
            # Check if the content is empty
            if edited_content == '':
                return '<h1>不能添加空的单词！！</h1>'
            OMIGA_dictionary.sql("UPDATE dictionary SET Meaning='{0}' WHERE Word='{1}'".format(edited_content, session['word']))
            # Push dataset to github
            if GITHUB == 1:
                g.add("--all")
                g.commit("-m auto update {0} from omiga.org".format(session['word']))
                g.push()
            return '<h1>成功修改单词</h1>'
        if request.form['submit_button'] == '删除此单词':
            OMIGA_dictionary.sql("DELETE FROM dictionary WHERE Word='{0}'".format(session['word']))
            if GITHUB == 1:
                g.add("--all")
                g.commit("-m auto update {0} from omiga.org".format(session['word']))
                g.push()
            return "<h1>成功删除此单词</h1>"
    return render_template('editing.html', word=session['word'], content=content)

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
        password = request.form['password']
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
    if 'username' in session:
        # If yes, show the user page
        number = con.sql("SELECT Number FROM users WHERE Name='{0}'".format(session['username'])).df()
        number = str(number['Number'][0])
    else:
        # If not, redirect to /sign_in to sign in 
        return redirect('/sign_in')
    
    # Change user data
    if request.method == 'POST':
        new_number = request.form['number']
        con.sql("UPDATE users SET number={0} WHERE Name='{1}'".format(new_number, session['username']))
        return '<h1>成功更改</h1>'

    return render_template('users.html', user_name=session['username'], num=number)

# Run!!!!!
if __name__ == '__main__':
    print('''                             
   ___  __  __ ___ ____    _            
  / _ \|  \/  |_ _/ ___|  / \     
 | | | | |\/| || | |  _  / _ \      Version: BETA2.1a
 | |_| | |  | || | |_| |/ ___ \     Contributor: Fanfansmilyway, Fkpwolf
  \___/|_|  |_|___\____/_/   \_\    Date: 2023/7/28

    ''')
    # Don't open debug mode because of duckdb database.
    app.run(host='0.0.0.0',port='80', debug=False)