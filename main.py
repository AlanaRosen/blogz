from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 
import re

app = Flask(__name__)
app.config['DEBUG'] = True 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)
app.secret_key = 'fjgiowefj232esj5f'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')
    

    def __init__(self,username,password,email):
        self.username = username
        self.password = password
        self.email = email
        

def get_blogs():
    return db.session.query(Blog).order_by(Blog.id.desc()).all()

def get_blogs_by_user_id(user_id):
    return db.session.query(Blog).filter_by(owner_id=user_id).all()

def get_single_blog(id):
    return db.session.query(Blog).filter_by(id=id).first()

def get_user():
    return db.session.query(User).filter_by(email=session['user']).first()

def get_usernames():
    return db.session.query(User).all()


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():

    if 'user' in session:
        flash('You are already logged in')
        return redirect('/blog')

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
            
        user = db.session.query(User).filter_by(username=username).first()

        if user:
            if user.password == password:
                session['user'] = user.email
                logged_in = 'Logged in'
                return redirect('/')
            else:
                flash('That password is incorrect')
                return redirect('/login')
        else:
            flash('You need to register for an account')
            return redirect('/signup')
    

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')

@app.route('/', methods=['GET'])
def index():
    usernames = get_usernames()
    return render_template('index.html',
                            usernames_display='List of Blogger Usernames',
                            username_list=usernames)

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        password_verification = request.form['verify_password']
        username = request.form['username']

        existing_user = db.session.query(User).filter_by(username=username).first()

        if existing_user:
            flash('You aleady have an account')
            return redirect('/login')
  
        if not existing_user:
            if valid_email(email) == False:
                flash('Invalid email')
                return redirect('/signup')
        if valid_password(password) == False:
            flash('Invalid password - between 5 and 50 characters please')
            return redirect('/signup')
        if valid_verify(password,password_verification) == False:
            flash('This password did not match your previous entry')
            return redirect('/signup')
        if valid_email(email)==True and valid_password(password)==True and valid_verify(password,password_verification)==True:
            user = User(username,password,email)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.email
            flash('You registered an account.')
            return redirect('/newpost')
        else:
            return redirect('/signup')

def valid_email(email):
    if email != '':
        if not re.match(r'^[^@ ]+@[^@ ]+\.[^@ ]+$', email):
            return False
    if email == '':
        return False

    return True

def valid_password(password):
    if password == '':
        return False
    if len(password) > 50 or len(password) < 5:
        return False
    return True

def valid_verify(password, verify_password):
    if verify_password != password:
        return False
    return True

@app.route('/blog')
def blog():
    blogs = []
    user_id = request.args.get('user')
    username = db.session.query(User).filter_by(id=user_id).first()
    if user_id is None:
        blogs = get_blogs()
    else:
        blogs = get_blogs_by_user_id(int(user_id))
    return render_template(
        'blog.html',
        title='Blogs',
        blog_display = 'All Blogs',
        blog_list=blogs,
        username=username)

@app.route('/newpost', methods=['GET'])
def post_new():
    return render_template('newpost.html', write_title ='Write Your Blog') 

@app.route('/newpost', methods=['POST'])
def validate_entry():

    blog_title = request.form['blog_title']
    write_blog = request.form['write_blog']

    did_error = False

    title_error = ''
    blog_error = ''

    if blog_title == '':
        did_error = True
        title_error = 'Please enter a title for your blog entry.'
    if write_blog == '':
        did_error = True 
        blog_error = 'Please enter some text for your blog.'

    if did_error == True:
        return render_template('newpost.html',
                        write_title = 'Write Your Blog',
                        blogtitle = blog_title,
                        writeblog = write_blog,
                        blog_error = blog_error,
                        title_error = title_error)

    else:
        blog = Blog(blog_title, write_blog, get_user())
        db.session.add(blog)
        db.session.commit()

        return redirect('/single_blog?id=' + str(blog.id))

@app.route('/single_blog', methods=['GET'])
def singleblog():
    id = request.args['id']
    return render_template('single_blog.html',
                            title='A Blog',
                            blog=get_single_blog(id))
    
if __name__ == "__main__":
    app.run()
