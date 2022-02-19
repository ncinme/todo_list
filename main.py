from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, Date, desc, asc
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Todo(db.Model):
    id = Column(Integer, primary_key=True)
    item = Column(String(250), unique=True, nullable=False)
    due_date = Column(Date, nullable=False)
    created_date = Column(Date, nullable=False)
    # due_date = Column(String(250), nullable=False)
    # created_date = Column(String(250), nullable=False)
    status = Column(Boolean, nullable=False)


# db.create_all()

def add_item(data):
    todo = Todo(
        item=data['item'],
        due_date=data['due_date'],
        created_date=data['created_date'],
        status=data['status']
    )
    db.session.add(todo)
    db.session.commit()


def get_all_items():
    return Todo.query.all()


def get_item_by_id(item_id):
    return Todo.query.filter_by(id=item_id).first()  # This is one way


def get_item_by_filter(filter_option):
    return Todo.query.filter_by(status=filter_option).all()  # This is one way


def delete_item(item_id):
    todo = Todo.query.get(item_id)  # This is another way, as id is unique
    db.session.delete(todo)
    db.session.commit()


@app.route('/')
def home():
    all_items = get_all_items()
    return render_template('index.html', todos=all_items)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        due_date = request.form['date']  # This is in string format '2022-02-13'
        # due_date1 = datetime.strptime(due_date, "%Y-%m-%d").strftime("%d-%b-%Y")  # converting it into a datetime object then changing the format to '13-Feb-2022'
        # due_dt_obj = datetime.strptime(due_date1, "%d-%b-%Y")        # converting it into a datetime object, but it is stored in '2022-02-13' format in the database, hence dropping this idea
        due_dt_obj = datetime.strptime(due_date, "%Y-%m-%d")      # converting it into a datetime object, to store in the database for sorting

        data = {
            'item': request.form['item'],
            'due_date': due_dt_obj,
            'created_date': datetime.today(),
            'status': 0,
        }
        add_item(data)
    return redirect(url_for('home'))


@app.route('/status/<int:item_id>')
def status(item_id):
    item = get_item_by_id(item_id)
    if item.status == 0:
        item.status = 1
    else:
        item.status = 0
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    item_to_edit = get_item_by_id(item_id)
    all_items = get_all_items()
    if request.method == 'POST':
        new_due_date = request.form['date']  # This is in string format '2022-02-13'
        new_due_dt_obj = datetime.strptime(new_due_date, "%Y-%m-%d")  # converting it into a datetime object for db
        item_to_edit.item = request.form['item']
        item_to_edit.due_date = new_due_dt_obj
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', item=item_to_edit, todos=all_items)


@app.route('/delete/<int:item_id>')
def delete(item_id):
    delete_item(item_id)
    return redirect(url_for('home'))


current_status = ''
sort_option = ''


def fetch_record():
    items = []
    if current_status == 0 or current_status == 1:
        if sort_option == 'created_date':
            items = Todo.query.filter_by(status=current_status).order_by(asc(Todo.created_date)).all()
        elif sort_option == 'due_date':
            items = Todo.query.filter_by(status=current_status).order_by(asc(Todo.due_date)).all()
        else:
            items = Todo.query.filter_by(status=current_status).all()
    else:
        if sort_option == 'created_date':
            items = Todo.query.order_by(desc(Todo.created_date)).all()
        elif sort_option == 'due_date':
            items = Todo.query.order_by(desc(Todo.due_date)).all()
    return items


@app.route('/filter', methods=['GET', 'POST'])
def filter_by():
    global current_status
    if request.method == 'POST':
        filter_option = request.form['filter']
        if filter_option == 'completed':
            current_status = 1
        elif filter_option == 'active':
            current_status = 0
        else:
            current_status = 2          # random number for 'All'
        filtered_items = fetch_record()
        if filtered_items:
            return render_template('index.html', todos=filtered_items)
        else:
            return redirect(url_for('home'))


@app.route('/sort', methods=['GET', 'POST'])
def sort_by():
    global sort_option
    if request.method == 'POST':
        sort_option = request.form['sort']
        sorted_items = fetch_record()
        return render_template('index.html', todos=sorted_items)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
