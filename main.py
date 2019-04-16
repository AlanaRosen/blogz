from flask import Flask, request, redirect, render_template 
from flask_sqlalchemy import SQLAlchemy 
import cgi
import os 

app = Flask(__name__)
app.config['DEBUG'] = True 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    body = db.Column(db.String(5000))

    def __init__(self,title,body):
        self.title = title
        self.body = body

blogs = []

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog')
def blog_page():
    return render_template('blog.html', title='Your Blog', blog_display = 'Your Blog', blogs=blogs)

@app.route('/newpost')
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
        blog = Blog(blog_title, write_blog)
        blogs.append(blog)
        return redirect('/blog')

@app.route('/single_blog', methods=['GET'])
def singleblog():

    id = request.args.get('id')

    return render_template('single_blog.html', blog_title = id.title, blog_body = id.body, id = id)
    
if __name__ == '__main__':
    app.run()




# 'add a new post' and blog listings on the same page
# separate those portions into separate routes, handler classes, and templates
# when a user submits a new post, redirect them to the main blog page
# nav links on both pages