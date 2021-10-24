import os
import datetime
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists('env.py'):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_latest")
def get_latest():
    '''Find recent added recipes and display then on home page.'''
    recipes = mongo.db.recipes.find()
    return render_template("main_page.html", recipes=recipes)


@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)


@app.route("/get_recipe")
def get_recipe():
    '''Page with a list of all added recipes.'''
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    '''Creating register method for user to create account.'''
    if request.method == "POST":
        # check if the user already exist
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        password_one = request.form.get("password")
        password_two = request.form.get("repeat-password")

        if existing_user:
            flash("Username already exist")
            return redirect(url_for("register"))
        elif password_one != password_two:
            flash("Your password didn't match")
            return redirect(url_for("register"))

        new_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get('password'))
        }
        mongo.db.users.insert_one(new_user)

        # put new user into session
        session["user"] = request.form.get("username").lower()
        flash("Congratz!!! You joined our community")
        return redirect(url_for("profile", username=session['user']))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    '''Login methon to login into user profile page.'''
    if request.method == "POST":
        # check for account if it exist in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            # check if password is correct
            if check_password_hash(
                    existing_user['password'], request.form.get("password")):
                session['user'] = request.form.get('username').lower()
                flash("Welcome, {}".format(request.form.get('username')))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # if user inputs wrong password
                flash("Incorrect Cook Name and/or Password")
                return redirect(url_for('login'))

        else:
            # if user inputs wrong username
            flash("Incorrect Cook Name and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    ''' User profile page method'''
    username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]

    if session['user']:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    '''Logout the user from his profile'''
    flash("You have been successfully logged out")
    session.pop("user")
    return redirect(url_for("get_latest"))


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST" and 'recipe_image' in request.files:
        recipe_image = request.files['recipe_image']
        mongo.save_file(recipe_image.filename, recipe_image)
        recipes = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "ingredients": request.form.getlist("ingredients"),
            "methods": request.form.getlist("methods"),
            "cook_time": int(request.form.get("cook_time")),
            "prep_time": int(request.form.get("prep_time")),
            "recipe_by": session['user'],
            "recipe_image": recipe_image.filename,
            "recipe_add_time": datetime.datetime.now()
        }
        mongo.db.recipes.insert_one(recipes)
        flash("Recipe Was Successfully Added")
        return redirect(url_for("get_recipe"))
    categories = mongo.db.categories.find().sort("category_name", 1)
    # if 'recipe_image' in request.files:
    #     recipe_image = request.files['recipe_image']
    #     mongo.save_file(recipe_image.filename, recipe_image)
    return render_template("add_recipe.html", categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
