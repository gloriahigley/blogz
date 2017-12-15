
from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(120))
   body = db.Column(db.String(120))
    
   def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    return render_template('blog.html', 
        blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

     blog_title_error = ""
     blog_body_error = ""

     if request.method == 'POST':
        blog_title = request.form['title']
        if len(blog_title) < 1:
            blog_title_error = "Please add a title for your awesome blog"
        blog_body = request.form['body']
        if len(blog_body) < 1:
            blog_body_error = "Please add content for your awesome blog"
        if not blog_title_error and not blog_body_error:  
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/newblog?id='+str(new_blog.id))
        else:
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, blog_title_error=blog_title_error, blog_body_error=blog_body_error)

     return render_template('newpost.html')

@app.route('/newblog', methods = ['GET'])
def newblog():

    blog_id = request.args.get('id')
    blog_query = Blog.query.filter_by(id=blog_id).first()
    return render_template('newblog.html', blog=blog_query)

if __name__ == '__main__':
    app.run()