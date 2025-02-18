from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
# from forms import RegistrationForm,LoginForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user
# import os
import commands

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
#,BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
# from flaskblock import User

app=Flask(__name__)
app.config['SECRET_KEY']='91da80d1e75c6638528ddb0bfe6c0596'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    
    def __repr__(self):
        return "User({0},{1},{2})".format(self.username,self.email,self.password)

class RegistrationForm(FlaskForm):
    username=StringField('Username',
                            validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',
                        validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm_Password',
                                    validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('SignUp')  

    def validate_username(self,username):
        client=User.query.filter_by(username=username.data).first()
        if client :
            raise ValidationError('That username is taken.Please choose a different one.')                 

    def validate_email(self,email):
        client=User.query.filter_by(email=email.data).first()
        if client :
            raise ValidationError('That email is taken.Please choose a different account one.')

class LoginForm(FlaskForm):
    email=StringField('Email',
                        validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    #remember=BooleanField('Remember Me',True)
    submit=SubmitField('Login')                   

@app.route("/",methods=["POST","GET"])
@app.route("/register",methods=["POST","GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email=request.form.get('email')
        user = User(username = username, password = password, email=email)

        if form.validate_on_submit():
            hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user=User(username=form.username.data,email=form.email.data,password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("New Account created for {}.You are now able to log in ".format(form.username.data),'success')
            return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)


@app.route("/home",methods=["POST","GET"])
def home():
    return render_template('home.html')


@app.route("/output",methods=["POST","GET"])
def output():
    return render_template('output.html')


@app.route("/copy",methods = ["POST", "GET"])
def copy():
    code = request.form.get("code")
    arg =request.form.get("sys arg")
    file = open("file.py","w+")
    file.write(code)
    file.close()
    # os.system("python file.py > result.txt")
    s=commands.getoutput("python file.py "+str(arg))
    l=s.split('\n')
    # file1=open("result.txt","r")
    # display=file1.read()
    # file1.close()
    return render_template('output.html',title="output",display=l)


@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # if form.email.data=="admin@blog.com" and form.password.data=='password':
            #     flash('You have logged in!!','success')
            #     return redirect(url_for('home'))
        #else:
            user=User.query.filter_by(email=form.email.data).first()    
            if user and bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for('home'))
        else:
            flash('Unsuccessful Login.Please check your email and password','danger')
    return render_template('login.html',title='Login',form=form)

if __name__=="__main__":
    db.create_all()
    app.run(debug=True)
