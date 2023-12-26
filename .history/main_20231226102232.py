from flask import Flask, render_template, request, redirect, url_for, flash

from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','avif'}

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # SQLite database file

db = SQLAlchemy(app)

app.config['SECRET_KEY'] = '1234'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.app_context().push()


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Login manager user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
# @app.route('/')
# def index():
#     if current_user.is_authenticated:
#         return render_template('index.html', username=current_user.username)
#     return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print("1")
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print("2")
        # Check if the username or email already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        print("3")
        if existing_user or existing_email:
            flash('Username or email already exists!', 'error')
            return redirect(url_for('signup'))
        print("4")

        new_user = User(username=username, email=email, password=password)
        print("5")
        db.session.add(new_user)
        db.session.commit()

        # Log in the newly signed up user
        login_user(new_user)

        flash('Account created successfully! Welcome to the application.', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/user_page')
@login_required
def user_page():
    return render_template('user_page.html', username=current_user.username, email=current_user.email)

@app.route('/update_user', methods=['POST'])
@login_required
def update_user():
    if request.method == 'POST':
        new_username = request.form['new_username']
        new_email = request.form['new_email']
        new_password = request.form['new_password']

        # Update user details if new data is provided
        if new_username:
            current_user.username = new_username
        if new_email:
            current_user.email = new_email
        if new_password:
            current_user.password = new_password

        db.session.commit()
        flash('User details updated successfully!', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('index'))

#===========================================================================================================================


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    price = db.Column(db.Float)
    author = db.Column(db.String(100))
    image = db.Column(db.String(100))
    desc = db.Column(db.String(400))

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    posts = Post.query.all()
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.username,posts=posts)
    return render_template('index.html', posts=posts)



@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        author = request.form['author']
        desc = request.form['desc']
        try:
            if 'image' not in request.files:
                print("WTF..................")
                pass
            else:
                file = request.files['image']
                if file.filename == '':
                    print("I reached here atleast")
                    pass
                elif file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    print("print something here")
                    new_post = Post(title=title, price=price, author=author,desc=desc, image=filename)
                    db.session.add(new_post)
                    db.session.commit()
                    flash('File uploaded successfully')
                else:
                    new_post = Post(title=title, price=price, author=author, desc=desc)
                    db.session.add(new_post)
                    db.session.commit()
                    flash('File uploaded successfully')
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            flash(f'Error: {str(e)}', 'error')
            db.session.rollback()
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # post = Post.query.get_or_404(id)
    post=Post.query.get(id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.price = request.form['price']
        post.author = request.form['author']
        post.desc = request.form['desc']
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.image = filename
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', post=post)

@app.route('/product/<int:id>', methods=['GET', 'POST'])
def product(id):
    if current_user.is_authenticated:
        post=Post.query.get(id)
        if request.method == 'POST':
            post.title = request.form['title']
            post.price = request.form['price']
            post.author = request.form['author']
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    post.image = filename
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('product.html', post=post, username=current_user.username)
    else:
        post=Post.query.get(id)
        if request.method == 'POST':
            post.title = request.form['title']
            post.price = request.form['price']
            post.author = request.form['author']
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    post.image = filename
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('product.html', post=post)

@app.route('/delete/<int:id>')
def delete(id):
    # post = Post.query.get_or_404(id)
    post=Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    flash('Successfully deleted')
    return redirect(url_for('index'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if current_user.is_authenticated:
        return render_template('cart.html', username=current_user.username)
    return render_template('cart.html')


if __name__ == '__main__':
    db.create_all()  # Create the database tables
    db.create_all()
    app.run(debug=True)
