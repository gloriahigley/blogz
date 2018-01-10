
from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(120))
   body = db.Column(db.String(120))
   owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

   def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(120))
   password = db.Column(db.String(120))
   blogs = db.relationship('Blog', backref='owner')
    
   def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():

   if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       user = User.query.filter_by(username=username).first()
       if user == None:
           flash("Username is incorrect")
           return redirect('/login')
       if user.password != password:
           flash("Password is incorrect")
           return redirect('/login')
       else:
           session['username'] = username
           flash("Logged in")
           return redirect('/newpost')

   return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        user = User.query.filter_by(username=username).first()

        if username == "" or password == "" or verify == "" : 
            flash("One or more fields is invalid", 'error')
            return redirect('/register')

        if user != None:
            flash("The username entered already exists", 'error')
            return redirect('/register')

        if verify != password:
            flash("Passwords do not match", 'error')
            return redirect('/register')
        
        
        if len(username) < 3:
            flash("Username must be greater than three characters",'error')
            return redirect('/register')
        

        if len(password) < 3:
            flash("Password must be greater than three characters", 'error')
            return redirect('/register')

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get("id"):
        blog_id = request.args.get("id")
        blog_query = Blog.query.filter_by(id=blog_id).first()
        return render_template('singleBlogEntry.html', blog=blog_query)

    elif request.args.get("user"):
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        userblogs = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', userblogs= userblogs)
    
    blog_query = Blog.query.all()
    return render_template('blog.html', blog_query=blog_query)
    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

     blog_title_error = ""
     blog_body_error = ""
     blog_owner = User.query.filter_by(username=session['username']).first()

     if request.method == 'POST':
        blog_title = request.form['title']
        if len(blog_title) < 1:
            blog_title_error = "Please add a title for your awesome blog"
        blog_body = request.form['body']
        if len(blog_body) < 1:
            blog_body_error = "Please add content for your awesome blog"
        if not blog_title_error and not blog_body_error:  
            new_blog = Blog(blog_title, blog_body, blog_owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/newblog?id='+str(new_blog.id))
        else:
            return render_template('newpost.html', owner = blog_owner,blog_title=blog_title, blog_body=blog_body, blog_title_error=blog_title_error, blog_body_error=blog_body_error)

     return render_template('newpost.html')

@app.route('/newblog', methods = ['GET'])
def newblog():

    blog_id = request.args.get('id')
    blog_query = Blog.query.filter_by(id=blog_id).first()
    return render_template('newblog.html', blog=blog_query)

@app.route('/', methods=['POST', 'GET'])
def index():
    user_query = User.query.all()
    return render_template('index.html', user_query=user_query)

if __name__ == '__main__':
    app.run()