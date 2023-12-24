import mysql.connector
from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from form import Add, Add_Data,Update_Data
import requests
from flask_login import UserMixin, login_required, login_user, LoginManager, current_user, logout_user
import json
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


# Create a User model
class User(UserMixin):
    def __init__(self, user_id, email, name, data):
        self.id = user_id
        self.email = email
        self.name = name
        self.data = data

# User loader function


@login_manager.user_loader
def load_user(user_id):
    sql = f"SELECT * FROM user WHERE id={user_id}"
    mycursor.execute(sql)
    user_data = mycursor.fetchone()
    if user_data:
        user_id, email, name, data = user_data[0], user_data[1], user_data[3], user_data[4]
        return User(user_id, email, name, data)


# mysql connections
# "CREATE TABLE user (id INT AUTO_INCREMENT PRIMARY KEY,email VARCHAR(255) NOT NULL UNIQUE,password VARCHAR(255) NOT NULL,name VARCHAR(255) NOT NULL,data VARCHAR(10000))"
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="bhanupattemz",
    database="movieadder"
)
mycursor = db.cursor()


@app.route("/", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        sql = f"SELECT * FROM user WHERE email='{email}'"
        mycursor.execute(sql)
        user_data = mycursor.fetchone()
        if user_data and check_password_hash(user_data[2], password=password):
            user_id, name, data = user_data[0], user_data[3], user_data[4]
            user = User(user_id, email, name, data)
            login_user(user)
            return redirect(url_for("home"))
        elif not check_password_hash(user_data[2], password=password):
            return render_template("index.html", logged_in=current_user.is_authenticated, password=False, signin=True, signup=False)
    return render_template("index.html", logged_in=current_user.is_authenticated, password=True, signin=True, signup=False)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = generate_password_hash(
            password=request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8)
        name = request.form.get("name")
        sql = "INSERT INTO user (email, password, name) VALUES (%s,%s,%s)"
        new_user = (email, password, name)
        mycursor.execute(sql, new_user)
        db.commit()
        return redirect(url_for("signin"))
    return render_template("signup.html", logged_in=current_user.is_authenticated, signin=False, signup=True)


@app.route("/home")
@login_required
def home():
    movies = current_user.data
    if movies != None :
       movies = convert_list(movies)
       return render_template("home.html", movies=movies, logged_in=current_user.is_authenticated)
    else:
        return render_template("home.html", movies=[], logged_in=current_user.is_authenticated)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    add_movie = Add()
    if request.method == 'POST':
        return redirect(f"/select/{add_movie.title.data}")
    return render_template('add.html', form=add_movie, logged_in=current_user.is_authenticated)


@app.route('/select/<movie_name>', methods=['GET', 'POST'])
@login_required
def select(movie_name):
    data = requests.get(
        f'https://api.themoviedb.org/3/search/movie?query={movie_name}&api_key=f0bbbed02be68009b6d528416956968e').json()
    return render_template('select.html', data=data["results"], logged_in=current_user.is_authenticated)


@app.route('/add_data/<movie_name>/<date>/<description>/<img>', methods=["GET", "POST"])
@login_required
def add_movie(movie_name, date, description, img):
    form = Add_Data()
    if request.method == "POST":   
        upload_date= datetime.datetime.now().strftime("%d-%m-%Y")
        if current_user.data != None :
            movies_data = convert_list(current_user.data)
            new_movie = [{
            "id": len(movies_data),
            "time":upload_date,
            "title": movie_name,
            "year": date,
            "description": description,
            "rating": form.Rating.data,
            "review": form.review.data,
            "img_url": f"https://image.tmdb.org/t/p/w500/{img}"
        }]
            new_data = convert_list(current_user.data)+new_movie
        else:  
            new_movie = [{
            "id": 0,
            "time": upload_date,
            "title": movie_name,
            "year": date,
            "description": description,
            "rating": form.Rating.data,
            "review": form.review.data,
            "img_url": f"https://image.tmdb.org/t/p/w500/{img}"
             }]
            new_data = new_movie
        try:
            sql=f"UPDATE user SET data=\"{new_data}\" WHERE id={current_user.id}"
            mycursor.execute(sql)
            db.commit()
            return redirect(url_for('home'))
        except:
            return redirect(url_for("home"))
    return render_template("add_movie.html",form=form,logged_in=current_user.is_authenticated)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('signin'))
@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route("/delete_movie/<int:index_>")
@login_required
def delete_movie(index_):
    movies_data=convert_list(current_user.data)
    del movies_data[index_]
    sql=f"UPDATE user SET data=\"{movies_data}\" WHERE id={current_user.id}"
    mycursor.execute(sql)
    db.commit()
    return redirect(url_for("home"))


@app.route("/update_movie/<int:id_>", methods=["GET", "POST"])
@login_required
def update_movie(id_):
    update_data = Update_Data()
    movies_data = convert_list(current_user.data)

    if request.method == "POST":
        movies_data[id_]["rating"] = update_data.Rating.data
        movies_data[id_]["review"] = update_data.review.data

        # Update the database with the modified movie data
        try:
            sql = f"UPDATE user SET data=%s WHERE id=%s"
            new_data = json.dumps(movies_data)  # Convert updated movie data to JSON
            mycursor.execute(sql, (new_data, current_user.id))
            db.commit()
            return redirect(url_for("home"))
        except Exception as e:
            print(f"Error updating movie: {e}")
            return redirect(url_for("home"))

    return render_template('update.html', form=update_data, logged_in=current_user.is_authenticated)
   



def convert_list(data_string):
    valid_json_string = data_string.replace("'", "\"")
    inner_json_string = valid_json_string.strip('[]')
    data_list = json.loads(f"[{inner_json_string}]")
    return data_list


if __name__ == "__main__":
    app.run(debug=True, port=5001)
