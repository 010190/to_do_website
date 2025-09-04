import datetime
from typing import List

import flask_sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text, MetaData, Table, insert, delete, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from flask_bootstrap import Bootstrap4
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import TimeField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, URL
import calendar
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.fields import DateField, DateTimeField
from flask_login import LoginManager, UserMixin, login_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap4(app)

engine = create_engine("sqlite:///todo.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"

login_manager = LoginManager()
login_manager.init_app(app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Users(db.Model, UserMixin):
    __tablename__ = "users_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    done_todo: Mapped[int] = mapped_column(default=0)
    undone_todo: Mapped[int] = mapped_column(default=0)
    todos: Mapped[List["ToDo"]] = relationship(back_populates="user")


class ToDo(db.Model):
    __tablename__ = 'todo_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    date: Mapped[str] = mapped_column()
    time: Mapped[str] = mapped_column()
    is_done: Mapped[bool] = mapped_column(default=False)
    user_id = mapped_column(ForeignKey("users_table.id"))
    user: Mapped["Users"] = relationship(back_populates="todos")


class TaskForm(FlaskForm):
    text = CKEditorField('TODO', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])

    submit = SubmitField('Submit')


class Login(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Submit')


class Register(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm_Password', validators=[DataRequired()])

    submit = SubmitField('Submit')

with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TaskForm()
    name = session.get('name')
    with Session(engine) as sess:
        result = sess.execute(select(Users).where(Users.nickname == name)).scalars().all()

    if form.validate_on_submit():
        text = form.text.data
        date = str(form.date.data)

        time = str(form.time.data)

        with app.app_context():
            new_todo = ToDo(text=text, date=date, time=time)
            db.session.add(new_todo)
            db.session.commit()
        print("todo added")
        return redirect(url_for('index'))

    return render_template('index.html', form=form, result=result)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    with app.app_context():
        to_delete = db.session.execute(db.select(ToDo).where(ToDo.id == id)).scalar()
        db.session.delete(to_delete)
        db.session.commit()
        print("deleted")

        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    login = Login()
    if login.validate_on_submit():
        result = db.session.execute(db.select(Users).where(Users.nickname == login.name.data))
        user = result.scalar()
        print("logowanie")

        if check_password_hash(user.password, login.password.data):
            login_user(user)
            session['user_name'] = user.nickname
            print("zalogowano")
            return redirect(url_for('index'))
        db.session.commit()

    return render_template('login.html', login=login)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register = Register()
    if register.validate_on_submit() and register.password.data == register.confirm_password.data:
        user = Users(nickname=register.name.data,
                     password=generate_password_hash(password=register.password.data, method="pbkdf2:sha256",
                                                     salt_length=8))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        session['user_name'] = user.nickname
        print(session['user_name'])
        print("registred")
        return redirect(url_for('index'))
    return render_template('register.html', register=register)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = TaskForm()
    with app.app_context():
        result = db.session.execute(db.select(ToDo)).scalars().all()

    if form.validate_on_submit():
        text = form.text.data
        date = str(form.date.data)

        time = str(form.time.data)

        with app.app_context():
            new_todo = ToDo(text=text, date=date, time=time)
            db.session.add(new_todo)
            db.session.commit()
        print("todo added")
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    name = session['user_name']
    form = TaskForm()
    with Session(engine) as sess:
        result = sess.execute(select(Users).where(Users.nickname == name)).scalars().all()
    return render_template('profile.html', result=result, form=form)


if __name__ == '__main__':

    app.run(debug=True)
