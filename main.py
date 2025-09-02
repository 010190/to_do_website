import datetime
import flask_sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text, MetaData, Table, insert, delete
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_bootstrap import Bootstrap4
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import TimeField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, URL
import calendar
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.fields import DateField, DateTimeField

app= Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap4(app)

engine = create_engine("sqlite:///todo.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class ToDo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    date: Mapped[str] = mapped_column()
    time: Mapped[str] = mapped_column()

# class DoneToDo(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     text: Mapped[str] = mapped_column()
#     date: Mapped[str] = mapped_column()
#     time: Mapped[str] = mapped_column()


class TaskForm(FlaskForm):
    text = CKEditorField('TODO',  validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])


    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TaskForm()
    with app.app_context():
        result = db.session.execute(db.select(ToDo)).scalars().all()

    if form.validate_on_submit():
        text = form.text.data
        date = str(form.date.data)



        time =str(form.time.data)

        with app.app_context():
            new_todo = ToDo( text=text, date=date, time=time)
            db.session.add(new_todo)
            db.session.commit()
        print("todo added")
        return redirect(url_for('index'))

    return render_template('index.html', form = form, result=result)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    with app.app_context():
        to_delete = db.session.execute(db.select(ToDo).where(ToDo.id==id)).scalar()
        db.session.delete(to_delete)
        db.session.commit()
        print("deleted")

        return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)