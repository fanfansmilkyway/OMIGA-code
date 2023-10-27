# Built-in modules
import os
# Need to install(not built-in)
from flask import Flask, request, render_template, redirect, session, flash
import duckdb

# Environment Variables
DATABASE = os.environ['DATABASE_DIR'] # 'user data' folder's location
CONTENT = os.environ['CONTENT_DIR'] # 'content' folder's location

app = Flask(__name__, template_folder='{0}/templates'.format(CONTENT), static_folder='{0}/static'.format(CONTENT))
app.secret_key = 'q776NkmVYq3vjZwaJn9drw'

# Database
OMIGA_dictionary = duckdb.connect('{0}/dictionary.db'.format(DATABASE))
discussion_database = duckdb.connect("{0}/discussion.db".format(DATABASE))
con = duckdb.connect("{0}/userdata.db".format(DATABASE))

# Create database if it not exists
con.sql("CREATE TABLE IF NOT EXISTS users(Id int primary key, Name varchar, Password varchar, Number varchar)")
con.sql("CREATE SEQUENCE IF NOT EXISTS seq_id START 1")
OMIGA_dictionary.sql("CREATE TABLE IF NOT EXISTS dictionary(Id int primary key, Word varchar(255), Meaning varchar(255))")
OMIGA_dictionary.sql("CREATE SEQUENCE IF NOT EXISTS seq_id START 1")
discussion_database.sql("CREATE TABLE IF NOT EXISTS topic(Id int primary key, Title varchar, Content varchar, CreatedTime varchar, Username varchar)")
discussion_database.sql("CREATE TABLE IF NOT EXISTS comment(Id int primary key, TopicId int, Content varchar, CreatedTime varchar, Username varchar)")
discussion_database.sql("CREATE SEQUENCE IF NOT EXISTS topic_seq_id START 1")
discussion_database.sql("CREATE SEQUENCE IF NOT EXISTS comment_seq_id START 1")

# Main pgae
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = '/'
            return redirect('/sign_in')
    return render_template('index.html', username=session.get('username', 'Guest'))

@app.route('/words', methods=['GET', 'POST'])
def words():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/words"
            return redirect('/sign_in')
        # Choose searching mode
        if request.form['submit_button'] == '直接查找':
            return redirect('/words/search-word-with-OMIGA')
        if request.form['submit_button'] == '查找单词的解释':
            return redirect('/words/search-word-with-meaning')
        if request.form['submit_button'] == '查看所有单词':
            all_words = OMIGA_dictionary.sql("SELECT Word FROM dictionary").fetchall()
            all_words = [i[0] for i in all_words]
            text = '<h1>目前的所有单词有:</h1>'
            for k in all_words:
                text = text + k + ", "
            return text
        
    # Count the words in the dictionary
    rows = OMIGA_dictionary.sql("SELECT COUNT(*) FROM dictionary").fetchall()[0][0]
    return render_template('words.html', rows=rows, username=session.get('username', 'Guest'))
    
@app.route('/words/search-word-with-OMIGA', methods=['GET', 'POST'])
def search_word_with_OMIGA():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/words/search-word-with-OMIGA"
            return redirect('/sign_in')
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
    </head>
            ''' + text
            return text
        else:
            # If not, show error message
            return "<h1>未找到此单词</h1>"
    return render_template('search-word-with-OMIGA.html', username=session.get('username', 'Guest'))

@app.route('/words/search-word-with-meaning', methods=['GET', 'POST'])
def search_word_with_chinese():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/words/search-word-with-meaning"
            return redirect('/sign_in')
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
    return render_template('search-word-with-meaning.html', username=session.get('username', 'Guest'))

@app.route('/lessons', methods=['GET','POST'])
def lessons():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/lessons"
            return redirect('/sign_in')
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
    return render_template('lessons.html', username=session.get('username', 'Guest'))

# Function: Convert txt file to html
def txt_web_show(filepath):
    filepath = CONTENT + '/templates/passages/' + filepath
    with open(filepath, 'r') as f:
        content = f.read()
        f.close()
    return render_template('passages-view.html', content = content, username=session.get('username', 'Guest'))

@app.route('/passages', methods=['GET', 'POST'])
def passages():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/passages"
            return redirect('/sign_in')
        # Choose passage
        if request.form['submit_button'] == 'hotini hegude 校园政府':
            return redirect('/passages/hotini-hegude')
        if request.form['submit_button'] == 'remu o OMIGA OMIGA之歌':
            return txt_web_show('songs/remu-o-OMIGA.txt')
        if request.form['submit_button'] == 'HUNTERxHUNTER Departure OP 全职猎人 Departure 主题曲':
            return txt_web_show('songs/HUNTERxHUNTER--Departure.txt')
        if request.form['submit_button'] == 'boku to hangte来之不易':
            return txt_web_show('stories/boku-to-hangte来之不易.txt')
        if request.form['submit_button'] == 'nv eyi两个家':
            return txt_web_show('stories/nv-eyi两个家.txt')
        if request.form['submit_button'] == 'sayoma buno a maki天堂鸟与女孩':
            return txt_web_show('stories/sayoma-buno-a-maki天堂鸟与女孩.txt')
    return render_template('passages.html', username=session.get('username', 'Guest'))

@app.route('/passages/hotini-hegude', methods=['GET', 'POST'])
def hotini_hegude():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/passages/hotini-hegude"
            return redirect('/sign_in')
        # Choose chapter
        if request.form['submit_button'] == '1.memode':
            return txt_web_show('hotini-hegude/yi-memode.txt')
        if request.form['submit_button'] == '2.honakode':
            return txt_web_show('hotini-hegude/nv-honakode.txt')
        if request.form['submit_button'] == '3.goku':
            return txt_web_show('hotini-hegude/sv-goku.txt')
    return render_template('hotini-hegude.html', username=session.get('username', 'Guest'))

@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/uploads"
            return redirect('/sign_in')
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
            return '<h1>成功添加单词</h1>'
    return render_template('uploads.html', username=session.get('username', 'Guest'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/edit"
            return redirect('/sign_in')
        if request.form['submit_button'] == '编辑':
            word = str(request.form['word'])
            # Check if the word exists
            if OMIGA_dictionary.sql("SELECT EXISTS(SELECT * FROM dictionary WHERE Word='{0}')".format(word)).fetchall()[0] == (True,):
                # If yes, redirect to /edit/editing
                session['word'] = word
                return redirect('/edit/editing')
            else:
                # If not, show error message
                return '<h1>此单词还未存在于字典中，若想添加此单词请前往<a href="/uploads">omiga.org/uploads</a></h1>'
    return render_template('edit.html', username=session.get('username', 'Guest'))

@app.route('/edit/editing', methods=['GET', 'POST'])
def editing():
    # Read from dataset
    content = OMIGA_dictionary.sql("SELECT Meaning FROM dictionary WHERE Word='{0}'".format(session['word'])).df()['Meaning'][0]
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/edit/editing"
            return redirect('/sign_in')
        if request.form['submit_button'] == '完成':
            edited_content = request.form['content']
            # Check if the content is empty
            if edited_content == '':
                return '<h1>不能添加空的单词！！</h1>'
            OMIGA_dictionary.sql("UPDATE dictionary SET Meaning='{0}' WHERE Word='{1}'".format(edited_content, session['word']))
            # Push dataset to github
            return '<h1>成功修改单词</h1>'
        if request.form['submit_button'] == '删除此单词':
            OMIGA_dictionary.sql("DELETE FROM dictionary WHERE Word='{0}'".format(session['word']))
            return "<h1>成功删除此单词</h1>"
    return render_template('editing.html', word=session['word'], content=content, username=session.get('username', 'Guest'))

@app.route('/discussion', methods=['GET', 'POST'])
def discussion():
    my_list = discussion_database.sql("SELECT * EXCLUDE Content FROM topic").fetchall()
    my_list.reverse()
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/discussion"
            return redirect('/sign_in')
        if request.form['submit_button'] == "创作一篇文章":
            return redirect('/discussion/create')
    return render_template('discussion.html', my_list=my_list, username=session.get('username', 'Guest'))

@app.route('/discussion/create', methods=['GET', 'POST'])
def discussion_create():
    if 'username' not in session:
        session['last_page'] = "/discussion/create"
        return redirect('/sign_in')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        discussion_database.sql("INSERT INTO topic (Id, Title, Content, CreatedTime, Username) VALUES (nextval('topic_seq_id'), '{0}', '{1}', CURRENT_TIMESTAMP::STRING, '{2}')".format(title, content, session['username']))
        return redirect('/discussion')
    return render_template('discussion-create.html', username=session.get('username', 'Guest'))

@app.route('/discussion/view/<passage_id>', methods=['GET', 'POST'])
def view_passage(passage_id):
    if request.method == 'POST':
        if request.form['submit_button'] == '登录':
            session['last_page'] = "/discussion/view/{0}".format(passage_id)
            return redirect('/sign_in')
        if 'username' not in session:
            return redirect('/sign_in')
        comment = request.form['comment']
        discussion_database.sql("INSERT INTO comment (Id, TopicId, Content, CreatedTime, Username) VALUES (nextval('comment_seq_id'), '{0}', '{1}', CURRENT_TIMESTAMP::STRING, '{2}')".format(passage_id, comment, session['username']))
    title = discussion_database.sql("SELECT Title FROM topic WHERE Id={0}".format(passage_id)).fetchone()[0]
    content = discussion_database.sql("SELECT Content FROM topic WHERE Id={0}".format(passage_id)).fetchone()[0]
    time = discussion_database.sql("SELECT CreatedTime FROM topic WHERE Id={0}".format(passage_id)).fetchone()[0]
    user = discussion_database.sql("SELECT Username FROM topic WHERE Id={0}".format(passage_id)).fetchone()[0]
    id = discussion_database.sql("SELECT Id FROM topic WHERE Id={0}".format(passage_id)).fetchone()[0]
    comments = discussion_database.sql("SELECT * EXCLUDE (Id,TopicId) FROM comment WHERE TopicId={0}".format(passage_id)).fetchall()
    return render_template('discussion-view.html', title=title, content=content, user=user, time=time, id=id, comments=comments, username=session.get('username', 'Guest'))   

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
    return render_template('sign_up.html', username=session.get('username', 'Guest'))

@app.route('/sign_in', methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Complete':
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
                if 'last_page' in session:
                    last_page = session['last_page']
                    session.pop('last_page', None)
                    return redirect(last_page)
                return '<h1>登录成功</h1>'
            else:
                return '<h1>密码错误</h1>'
        if request.form['submit_button'] == '退出账号':
            session.pop('username', None)
            return '<h1>成功退出账户</h1>'

    return render_template('sign_in.html', username=session.get('username', 'Guest'))
            
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

    return render_template('users.html', user_name=session['username'], num=number, username=session.get('username', 'Guest'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404NotFound.html'), 404

# Run!!!!!
if __name__ == '__main__':
    print('''                             
   ___  __  __ ___ ____    _            
  / _ \|  \/  |_ _/ ___|  / \     
 | | | | |\/| || | |  _  / _ \      Version: BETA3.2
 | |_| | |  | || | |_| |/ ___ \     Contributor: Fanfansmilyway, Fkpwolf
  \___/|_|  |_|___\____/_/   \_\    Date: 2023/10/27

    ''')
    # Don't open debug mode because of duckdb database.
    app.run(host='0.0.0.0',port='80', debug=False)