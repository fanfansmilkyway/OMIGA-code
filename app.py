from flask import Flask, request, render_template, flash, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import duckdb
from git import Repo

#Environment Variables
USER_DATA = os.environ['USER_DATA_DIR']
CONTENT = os.environ['CONTENT_DIR']

app = Flask(__name__, template_folder='{0}/templates'.format(CONTENT), static_folder='{0}/static'.format(CONTENT))

app.secret_key = 'q776NkmVYq3vjZwaJn9drw'

# Github
os.system("git config --global user.name 'fanfansmilkyway'")
os.system("git config --global user.email 'fanfansmilkyway@qq.com'")
repo = Repo(CONTENT)
g = repo.git

# Database
con = duckdb.connect("{0}/userdata.db".format(USER_DATA))

try:
    con.sql("CREATE TABLE users(Id int primary key, Name varchar(255), Password varchar(255), Number varchar(255))")
    con.sql("CREATE SEQUENCE seq_id START 1")
except:
    pass

CANT_VISIT = ['fix','index','lessons','sign_in','sign_up','uploads','users']
@app.route('/', methods=['GET','POST'])
def my_form_post():
    if request.method == 'POST':
        session['text'] = request.form['text']
        if session['text'] in CANT_VISIT:
            return '''
                <h1>不要访问以下页面：</h1>
                <h2>fix, index, lessons, sign_in, sign_up, uploads, users</h2>
                    '''
        try:
            return render_template('%s.html' %(session['text']))
        except:
            return "<h1>未找到此单词，请换一个</h1>" 

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

ALLOWED_EXTENSIONS = {'html'}
app.config['UPLOAD_FOLDER'] = CONTENT
app.config['MAX_CONTENT_LENGTH'] = 20 * 1000 * 1000   # 20MB

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        session['title'] = str(request.form['title'])
        session['content'] = request.form['content']
        text = repr(str(session['content']))
        text = text.replace('\\r\\n', '<br>')
        text = text.replace("'", '')
        f = open('{0}/templates/{1}.html'.format(CONTENT, session['title']), 'a')
        f.write('{0}'.format('<h1>'+session['title']+'</h1>'))
        f.write('{0}'.format(text))
        f.close()
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
            con.sql("INSERT INTO users (Id, Name, Password, Number) VALUES (nextval('seq_id'), '{0}', '{1}', '0')".format(user_name, password))
            return '<h1>成功创建账户</h1>'
        if con.sql("SELECT EXISTS(SELECT * FROM users WHERE Name='{0}')".format(user_name)).fetchall()[0] == (True,):
            return '<h1>此用户名已经被使用</h1>'
    return render_template('sign_up.html')

@app.route('/sign_in', methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = str(request.form['password'])
        # Check if the user exists
        if con.sql("SELECT EXISTS(SELECT * FROM users WHERE Name='{0}')".format(user_name)).fetchall()[0] == (True,):
            real_password = con.sql("SELECT Password FROM users WHERE Name='{0}'".\
                format(user_name)).df()
            real_password = str(real_password['Password'][0])
        if con.sql("SELECT EXISTS(SELECT * FROM users WHERE Name='{0}')".format(user_name)).fetchall()[0] == (False,):
            return '<h1>此用户不存在</h1>'    # Break
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
    
    # Change the number
    if request.method == 'POST':
        new_number = request.form['number']
        con.sql("UPDATE users SET number={0} WHERE Name='{1}'".format(new_number, session['username']))
        return '<h1>成功更改</h1>'

    return render_template('users.html', user_name=session['username'], num=number)

# Don't open debug mode
app.run(host='0.0.0.0',port='80')