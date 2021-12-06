import os
import urllib.request
from datetime import datetime
from flask import (
    Flask, flash, render_template, send_from_directory,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
if os.path.exists('env.py'):
    import env


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get("SECRET_KEY")


def allowed_file(filename):
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_latest")
def get_latest():
    '''Find recent added recipes and display then on home page.'''
    recipes = mongo.db.recipes.find()
    return render_template("main_page.html", recipes=recipes)


# @app.route("/file/<filename>")
# def file(filename):
#     return mongo.send_file(filename)


@app.route("/get_recipe")
def get_recipe():
    '''Page with a list of all added recipes.'''
    recipes = mongo.db.recipes.find().sort("category_name", 1)
    recipe_images = os.listdir('static/uploads')
    return render_template(
                    "recipes.html", recipes=recipes, recipe_images=recipe_images)


@app.route("/test_images/")
def test_images():
    # cia testuoju kaip vaizduojamas ikeltas image
    '''Page with a uploaded images.'''
    rec_images = os.listdir('static/uploads')
    # rec_images = ['uploads/' + filename for filename in rec_images]
    return render_template('test_images.html', rec_images=rec_images)


@app.route("/display_image/<filename>")
def display_image(filename):
    # cia testuoju kaip vaizduojamas ikeltas image
    '''Page with a uploaded images.'''
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route("/add_test_image", methods=["GET", "POST"])
def add_test_image():
    """cia funkcija kuri sukurs puslapi kuriame ikels test image"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for("add_test_image"))
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(url_for("add_test_image"))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # filename = str(uuid.uuid4())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # print('upload_image filename: ' + filename)
            flash('Image successfully uploaded')
            return render_template("add_test_image.html", filename=filename)
        else:
            flash('Allowed image types are: png, jpg, jpeg, gif')
            return redirect(url_for("add_test_image"))
    return render_template("add_test_image.html")


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
        recipes = mongo.db.recipes.find({"recipe_by": session['user']})
        recipe_images = os.listdir('static/uploads')
        return render_template(
            "profile.html", username=username, recipes=recipes, recipe_images=recipe_images)

    return redirect(url_for("login"))


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        print('pries check box')
        if request.form.get('check_to_upload_image') is None:
            print('NePazymeta')
            current_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
            current_recipe_image = current_recipe.get('recipe_image')
            current_recipe_path = os.path.join(app.config['UPLOAD_FOLDER'], current_recipe_image)
            print(current_recipe_image)
            print(current_recipe_path)
            recipe_image = request.files['recipe_image']
            if recipe_image and allowed_file(recipe_image.filename):
                # for image_list in mongo.db.recipes.find({},{ "_id": 0, "recipe_image": 1}):
                #     print('cia visas saras paveiksliuku: ' + str(image_list))
                if os.path.exists(current_recipe_path):
                    os.remove(os.path.join(
                        app.config['UPLOAD_FOLDER'], current_recipe_image))
                    print('Turejo istrinti: ' + current_recipe_image)
                else:
                    print("The file does not exist")
                filename = secure_filename(recipe_image.filename)
                splited_filename = filename.split(".")
                print('That\'s the filename parts: ' + str(splited_filename))
                suffix = datetime.now().strftime("%y%m%d_%H%M%S")
                new_filename = "_".join(
                            [splited_filename[0], suffix]) # e.g. 'mylogfile_120508_171442'
                filename = ".".join([new_filename, splited_filename[-1]])
                print("New filename is: " + filename)
                recipe_image.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename))
                flash('Image was successfully uploaded')
            else:
                flash('Allowed image types are: png, jpg, jpeg, gif')
                return redirect(url_for('edit_recipe', recipe_id=recipe_id))
            medium_date = datetime.now()
            update_recipe = {
                "category_name": request.form.get("category_name"),
                "recipe_name": request.form.get("recipe_name"),
                "recipe_description": request.form.get("recipe_description"),
                "ingredients": request.form.getlist("ingredients"),
                "methods": request.form.getlist("methods"),
                "cook_time": int(request.form.get("cook_time")),
                "prep_time": int(request.form.get("prep_time")),
                "recipe_by": session['user'],
                "recipe_image": filename,
                "recipe_add_time": medium_date.strftime('%m/%d/%Y %H:%M')
            }
            mongo.db.recipes.update_one(
                {"_id": ObjectId(recipe_id)}, {"$set": update_recipe})
            flash("Recipe Was Successfully Updated")
            return redirect(url_for("profile", username=session["user"]))
        else:
            print('Pazymeta')
        print('po check box')
        medium_date = datetime.now()
        update_recipe = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "ingredients": request.form.getlist("ingredients"),
            "methods": request.form.getlist("methods"),
            "cook_time": int(request.form.get("cook_time")),
            "prep_time": int(request.form.get("prep_time")),
            "recipe_by": session['user'],
            "recipe_add_time": medium_date.strftime('%m/%d/%Y %H:%M')
        }
    # if 'recipe_image' in request.files:
    #     mongo.save_file(recipe_image.filename, recipe_image)
    # recipe_image = request.files['recipe_image']
    #     mongo.save_file(recipe_image.filename, recipe_image)
    # elif request.method == "POST" and 'recipe_image' in request.files:
    #     medium_date = datetime.now()
    #     update_recipes = {
    #         "category_name": request.form.get("category_name"),
    #         "recipe_name": request.form.get("recipe_name"),
    #         "recipe_description": request.form.get("recipe_description"),
    #         "ingredients": request.form.getlist("ingredients"),
    #         "methods": request.form.getlist("methods"),
    #         "cook_time": int(request.form.get("cook_time")),
    #         "prep_time": int(request.form.get("prep_time")),
    #         "recipe_by": session['user'],
    #         "recipe_image": recipe_image.filename,
    #         "recipe_add_time": medium_date.strftime('%m/%d/%Y %H:%M')
    #     }
        mongo.db.recipes.update_one(
            {"_id": ObjectId(recipe_id)}, {"$set": update_recipe})
        flash("Recipe Was Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
            "edit_recipe.html", recipe=recipe, categories=categories)


@app.route("/delete/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.aggregate([
        {"$lookup":
            {
                "from": "fs.files",
                "localField": "recipe_image",
                "foreignField": "filename",
                "as": "remove_selection"
            }}
    ])
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    # filename = mongo.db.fs.files.find({"filename": "recipe_image"})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/logout")
def logout():
    '''Logout the user from his profile'''
    flash("You have been successfully logged out")
    session.pop("user")
    return redirect(url_for("get_latest"))


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        if 'recipe_image' not in request.files:
            flash('No file part')
            return redirect(url_for('add_recipe'))
        recipe_image = request.files['recipe_image']
        if recipe_image.filename == "":
            flash('No image selected for uploading')
            return redirect(url_for('add_recipe'))
        if recipe_image and allowed_file(recipe_image.filename):
            filename = secure_filename(recipe_image.filename)
            recipe_image.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            flash('Image was successfully uploaded')
        else:
            flash('Allowed image types are: png, jpg, jpeg, gif')
            return redirect(url_for('add_recipe'))
        medium_date = datetime.now()
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
            "recipe_add_time": medium_date.strftime('%m/%d/%Y %H:%M')
        }
        mongo.db.recipes.insert_one(recipes)
        flash("Recipe Was Successfully Added")
        return redirect(url_for("get_recipe"))
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
