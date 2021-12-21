import os
from datetime import datetime
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
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
    recipes = mongo.db.recipes.find().sort("recipe_add_time", -1).limit(8)
    kitchen_tools = mongo.db.kitchen_tools.find().sort(
        "item_add_time", -1).limit(4)
    return render_template(
        "main_page.html", recipes=recipes, kitchen_tools=kitchen_tools)


@app.route('/search', methods=["GET", "POST"])
def search():
    '''Search function between recipes and kitchen_tools collection on mongodb'''
    query = request.form.get("requests")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    kitchen_tools = list(mongo.db.kitchen_tools.find({"$text": {"$search": query}}))
    return render_template(
        "search_results.html", recipes=recipes, kitchen_tools=kitchen_tools, query=query)


@app.route('/search_recipes', methods=["GET", "POST"])
def search_recipes():
    '''Search function only on recipes page'''
    query = request.form.get("requests")
    recipes = mongo.db.recipes.find({"$text": {"$search": query}})
    all_recipes = len(list(mongo.db.recipes.find()))
    return render_template(
        "recipes.html", recipes=recipes,
         all_recipes=all_recipes, query=query)


@app.route('/search_items', methods=["GET", "POST"])
def search_items():
    '''Search function only on kitchen tools page'''
    query = request.form.get("requests")
    kitchen_tools = mongo.db.kitchen_tools.find({"$text": {"$search": query}})
    return render_template(
        "tools.html", kitchen_tools=kitchen_tools, query=query)


@app.route('/filter_category', methods=["GET", "POST"])
def filter_category():
    '''Search function only on kitchen tools page'''
    categ = request.form.get("category_filter")
    recipes_list = list(mongo.db.recipes.find())
    recipes = mongo.db.recipes.find({'category_name': categ}).sort("recipe_name", 1)
    categories = mongo.db.categories.find().sort("category_name", 1)
    categories_list = list(mongo.db.categories.find())
    all_recipes = len(list(mongo.db.recipes.find()))

    # Create a list of recipe collection only from category_name
    recipe_dict = []
    for recipe in recipes_list:
        for key, value in recipe.items():
            if key == "category_name":
                recipe_dict.append(value)
        print(recipe_dict)

    # Create a list form category collection using only category_name
    category_it_list = []
    for dic in categories_list:
        for key, value in dic.items():
            if key == 'category_name':
                if value not in category_it_list:
                    category_it_list.append(value)
        print('mano sarasas', category_it_list)

    # Create a dict 
    # dict kyes will be category_it_list items
    # dict value will count how many same categroy recipes we have
    # in recipe collection.

    new_dict = {}
    for item in category_it_list:
        if item not in new_dict:
            new_dict[item] = 0
    for recipe in recipe_dict:
        if recipe not in new_dict:
            new_dict[recipe] = 0
        new_dict[recipe] += 1

    return render_template(
        "recipes.html", recipes=recipes,
        categories=categories, 
        new_dict=new_dict, all_recipes=all_recipes)


@app.route("/get_recipe")
def get_recipe():
    '''Page with a list of all added recipes.'''
    recipes = mongo.db.recipes.find().sort("category_name", 1)
    recipes_list = list(mongo.db.recipes.find())
    all_recipes = len(list(mongo.db.recipes.find()))
    categories = mongo.db.categories.find().sort("category_name", 1)
    categories_list = list(mongo.db.categories.find())
    
    # Create a list of recipe collection only from category_name
    recipe_dict = []
    for recipe in recipes_list:
        for key, value in recipe.items():
            if key == "category_name":
                recipe_dict.append(value)
        print(recipe_dict)

    # Create a list form category collection using only category_name
    category_it_list = []
    for dic in categories_list:
        for key, value in dic.items():
            if key == 'category_name':
                if value not in category_it_list:
                    category_it_list.append(value)
        print('mano sarasas', category_it_list)

    # Create a dict 
    # dict kyes will be category_it_list items
    # dict value will count how many same categroy recipes we have
    # in recipe collection
    new_dict = {}
    for item in category_it_list:
        if item not in new_dict:
            new_dict[item] = 0
    for recipe in recipe_dict:
        if recipe not in new_dict:
            new_dict[recipe] = 0
        new_dict[recipe] += 1

    return render_template(
        "recipes.html", recipes=recipes, all_recipes=all_recipes,
        categories=categories, new_dict=new_dict)


@app.route("/product_list")
def get_product_list():
    '''Page with a list of all added products.'''
    kitchen_tools = mongo.db.kitchen_tools.find().sort("product_name", 1)
    return render_template(
                    "tools.html", kitchen_tools=kitchen_tools)


@app.route("/item_details/<item_id>")
def item_details(item_id):
    '''Get an item by its' ID'''
    kitchen_tools = mongo.db.kitchen_tools.find_one({'_id': ObjectId(item_id)})
    return render_template(
                    "item_details.html", kitchen_tools=kitchen_tools)


@app.route("/recipe_details/<recipe_id>")
def recipe_details(recipe_id):
    '''Get a recipe by its' ID'''
    try:
        recipes = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
        if session['user']:
            # username = mongo.db.users.find_one({"username": session["user"]})["username"]
            current_user = mongo.db.users.find_one({"username": session['user']})
            is_admin = current_user.get("isAdmin")
        return render_template(
                    "recipe_details.html", recipes=recipes, is_admin=is_admin)
    except:
        return render_template(
                    "recipe_details.html", recipes=recipes)


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

        medium_date = datetime.now()
        new_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get('password')),
            "isAdmin": False,
            "acc_created": medium_date.strftime('%m/%d/%Y %H:%M')
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
    try:
        username = mongo.db.users.find_one(
                {"username": session["user"]})["username"]
        if session['user']:
            recipes = mongo.db.recipes.find(
                {"recipe_by": session['user']}).sort('recipe_add_time', -1)
            count_recip = len(list(mongo.db.recipes.find(
                {"recipe_by": session['user']})))
            count_items = len(list(mongo.db.kitchen_tools.find()))
            count_recipes = len(list(mongo.db.recipes.find()))
            kitchen_tools = mongo.db.kitchen_tools.find()
            current_user = mongo.db.users.find_one(
                {"username": session['user']})
            is_admin = current_user.get("isAdmin")
            creation_date = current_user.get("acc_created")
            return render_template(
                "profile.html", username=username, recipes=recipes,
                count_recip=count_recip, kitchen_tools=kitchen_tools,
                is_admin=is_admin, count_items=count_items, count_recipes=count_recipes, creation_date=creation_date)
    except:
        return redirect(url_for("login"))
    return redirect(url_for("login"))


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    '''Edit recipe by it ID'''
    if request.method == "POST":
        if request.form.get('check_to_upload_image') is None:
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
                "recipe_image": request.form.get("recipe_image"),
                "recipe_add_time": medium_date.strftime('%m/%d/%Y %H:%M')
            }
            mongo.db.recipes.update_one(
                {"_id": ObjectId(recipe_id)}, {"$set": update_recipe})
            flash("Recipe Was Successfully Updated")
            return redirect(url_for("profile", username=session["user"]))
        else:
            print('Checked')
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
            mongo.db.recipes.update_one(
            {"_id": ObjectId(recipe_id)}, {"$set": update_recipe})
            flash("Recipe Was Successfully Updated")
            return redirect(url_for("profile", username=session["user"]))
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
            "edit_recipe.html", recipe=recipe, categories=categories)


@app.route("/edit_item/<item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    '''Edit item by it ID'''
    if request.method == "POST":
        update_item = {
            "product_name": request.form.get("product_name"),
            "product_category": request.form.get("product_category"),
            "product_image": request.form.get("product_image"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price"))
        }
        mongo.db.kitchen_tools.update_one(
            {"_id": ObjectId(item_id)}, {"$set": update_item})
        flash("Item Was Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))
    item = mongo.db.kitchen_tools.find_one({"_id": ObjectId(item_id)})
    return render_template(
            "edit_item.html", item=item)


@app.route("/delete/<recipe_id>")
def delete_recipe(recipe_id):
    '''Delete recipe function'''
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/delete_item/<item_id>")
def delete_item(item_id):
    '''Delete an item function from the list'''
    mongo.db.kitchen_tools.remove({"_id": ObjectId(item_id)})
    flash("Item Was Successfully Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/logout")
def logout():
    '''Logout the user from his profile'''
    flash("You have been successfully logged out")
    session.pop("user")
    return redirect(url_for("get_latest"))


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    '''Function to add recipe to the recipes collection'''
    if request.method == "POST":
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
            "recipe_image": request.form.get("recipe_image"),
            "recipe_add_time": medium_date.strftime('%m/%d/%Y %H:%M')
        }
        mongo.db.recipes.insert_one(recipes)
        flash("Recipe Was Successfully Added")
        return redirect(url_for("get_recipe"))
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    '''Add new item to the kitchen_tools collection'''
    if request.method == "POST":
        medium_date = datetime.now()
        kitchen_tools = {
            "product_name": request.form.get("product_name"),
            "product_category": request.form.get("product_category"),
            "product_image": request.form.get("product_image"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price")),
            "item_add_time": medium_date.strftime('%m/%d/%Y %H:%M')
        }
        mongo.db.kitchen_tools.insert_one(kitchen_tools)
        flash("Item Was Successfully Added")
        return redirect(url_for("profile", username=session["user"]))
    kitchen_tools = mongo.db.kitchen_tools.find().sort("product_name", 1)
    return render_template("add_item.html", kitchen_tools=kitchen_tools)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
