import os
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
    '''Check if uploaded image extension is in Allowed_xtensions list'''
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    recipe_images = os.listdir('static/uploads')
    all_recipes = len(list(mongo.db.recipes.find()))
    return render_template(
        "recipes.html", recipes=recipes, all_recipes=all_recipes,
         recipe_images=recipe_images, query=query)


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
    recipe_images = os.listdir('static/uploads')

    recipe_dict = []
    for recipe in recipes_list:
        for key, value in recipe.items():
            if key == "category_name":
                recipe_dict.append(value)
        print(recipe_dict)

    category_it_list = []
    for dic in categories_list:
        for key, value in dic.items():
            if key == 'category_name':
                if value not in category_it_list:
                    category_it_list.append(value)
        print('mano sarasas', category_it_list)

    new_dict = {}
    for item in category_it_list:
        if item not in new_dict:
            new_dict[item] = 0
    print('Neeeeeeeeeeeeeeeeeeeew_dict', new_dict)
    for recipe in recipe_dict:
        if recipe not in new_dict:
            new_dict[recipe] = 0
        new_dict[recipe] += 1
    print('Neeeeeeeeeeeeeeeeeeeew', new_dict)

    return render_template(
        "recipes.html", recipes=recipes,
        categories=categories, recipe_images=recipe_images,
        new_dict=new_dict, all_recipes=all_recipes)


@app.route("/get_recipe")
def get_recipe():
    '''Page with a list of all added recipes.'''
    recipes = mongo.db.recipes.find().sort("category_name", 1)
    recipes_list = list(mongo.db.recipes.find())
    all_recipes = len(list(mongo.db.recipes.find()))
    categories = mongo.db.categories.find().sort("category_name", 1)
    categories_list = list(mongo.db.categories.find())
    # dishes_count = len(list(mongo.db.recipes.find({'category_name': 'Dishes'})))
    # soup_count = len(list(mongo.db.recipes.find({'category_name': 'Soup'})))
    # easy_count = len(list(mongo.db.recipes.find({'category_name': 'Easy'})))
    # vegan_count = len(list(mongo.db.recipes.find({'category_name': 'Vegan'})))
    # vegetarian_count = len(list(mongo.db.recipes.find({'category_name': 'Vegetarian'})))
    # print('skaiciuoju sarasa -------------> ', dishes_count, soup_count, easy_count, vegan_count, vegetarian_count)
    # categ = request.form.get("category_filter")
    recipe_dict = []
    for recipe in recipes_list:
        for key, value in recipe.items():
            if key == "category_name":
                recipe_dict.append(value)
        print(recipe_dict)

    category_it_list = []
    for dic in categories_list:
        for key, value in dic.items():
            if key == 'category_name':
                if value not in category_it_list:
                    category_it_list.append(value)
        print('mano sarasas', category_it_list)
    
    new_dict = {}
    for item in category_it_list:
        if item not in new_dict:
            new_dict[item] = 0
    print('Neeeeeeeeeeeeeeeeeeeew_dict', new_dict)
    for recipe in recipe_dict:
        if recipe not in new_dict:
            new_dict[recipe] = 0
        new_dict[recipe] += 1
    print('Neeeeeeeeeeeeeeeeeeeew', new_dict)



#  for letter in word:
# ...     if letter not in counter:
# ...         counter[letter] = 0
# ...     counter[letter] += 1


    # count_recip = len(list(mongo.db.recipes.find({'category_name': categ})))


    # sarasas = {}
    # for dic in categories_list:
    #     print('loooooooooooooooopinam tarp kategoriju')
    #     for key, value in dic.items():
    #         if key == 'category_name':
    #             if value not in sarasas:
    #                 sarasas[value] = int(0)
    #                 print('mano sarasas', sarasas)

    # new_sarasas = {}
    # for key_cat, value_cat in sarasas.items():
    #     print(key_cat, value_cat)
    #     for recipe in recipes_list:
    #         print('ieksom receptu')
    #         print()
    #         for key, value in recipe.items():
    #             if key == 'category_name':
    #                 if value == key_cat:
    #                     print('Lyginu ------------->', value, 'SU', key_cat)
    #                     print('value_cat - reiksme -------------------->', key_cat)
    #                     value_cat = value_cat + 1
    #                     new_sarasas[key_cat] = value_cat
    # print('Naujai kurtas sarasas -------------------------------------> ', new_sarasas)



                        # for keyc, valuec in sarasas.items():
                        #     if  == keyc:
                        #         sarasas[keyc] += 1
                            # print(sarasas)
# dictionary1 = {"a": 1, "b": 2}
# dictionary2 = {"a": 3, "b": 2}
# common_pairs = dict()
# for key in dictionary1:
#     if (key in dictionary2 and dictionary1[key] == dictionary2[key]):
#         common_pairs[key] = dictionary1[key]
# print(common_pairs)


    # category_counter_dic = {}
    # for dic in categories_list:
    #     print('looooooooooooooopinam')
    #     for key, value in dic.items():
    #         if key == 'category_name':
    #             if key not in category_counter_dic:
    #                 category_counter_dic[key] = value
    #             print(key, '->', value)
    #             for rec_dic in recipes_list:
    #                 print('loooooooooooooooopinam tarp receptu')
    #                 for keyr, valuer in rec_dic.items():
    #                     if keyr == 'category_name':
    #                         print('Recepto indeksas- ', keyr, 'Reiksme- ', valuer)
    #                         if value == valuer:
    #                             number = number + 1
    #         print('skaicius kiek atitiko : ', number)
    # print('cia kategoriju sarasas ', category_counter_dic)
                #         print('receopto indeksas', keyr, '->', 'recepto value', valuer)

    # cat = []
    # for category in categories_list:
    #     cat.append(category)
    # categ = categories_list.get('category_name')
    recipe_images = os.listdir('static/uploads')
    # recip_count = 0
    # print('cia yra kategorijus listas nekurtas')
    # print()
    # print(categories_list)
    # print('cia  yra receptu listas')
    # print()
    # print(recipes_list)
    # print("kiek yra yrasu recipe liste")
    # print(len(recipes_list))
    # for category_name in categories_list:
    #     for recipe in recipes:
    #         if categories_list.category_name == recipe.category_name:
    #             recip_count = recip_count + 1
    #             print(recip_count)
    return render_template(
        "recipes.html", recipes=recipes,
        recipe_images=recipe_images, all_recipes=all_recipes,
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
    recipes = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template(
                    "recipe_details.html", recipes=recipes)


@app.route("/manage_products")
def manage_products():
    '''Page with a list of all products to manage(add/edit/delete).'''
    kitchen_tools = mongo.db.kitchen_tools.find().sort("product_name", 1)
    return render_template(
                    "manage_products.html", kitchen_tools=kitchen_tools)


@app.route("/display_image/<filename>")
def display_image(filename):
    # cia testuoju kaip vaizduojamas ikeltas image
    '''Page with a uploaded images.'''
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return redirect(url_for(
        'static', filename='uploads/' + filename), code=301)


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
            "password": generate_password_hash(request.form.get('password')),
            "isAdmin": False
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
            print(count_recip)
            kitchen_tools = mongo.db.kitchen_tools.find()
            recipe_images = os.listdir('static/uploads')
            current_user = mongo.db.users.find_one(
                {"username": session['user']})
            is_admin = current_user.get("isAdmin")
            if is_admin:
                print(f'Prisijunge Adminas {username}')
            else:
                print("Prisijunge neAdminas")
            return render_template(
                "profile.html", username=username, recipes=recipes,
                recipe_images=recipe_images, count_recip=count_recip,
                kitchen_tools=kitchen_tools, is_admin=is_admin)
    except:
        return redirect(url_for("login"))
    return redirect(url_for("login"))


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    '''Edit recipe by it ID'''
    if request.method == "POST":
        print('pries check box')
        if request.form.get('check_to_upload_image') is None:
            print('NePazymeta')
            current_recipe = mongo.db.recipes.find_one(
                {"_id": ObjectId(recipe_id)})
            current_recipe_image = current_recipe.get('recipe_image')
            current_recipe_path = os.path.join(
                app.config['UPLOAD_FOLDER'], current_recipe_image)
            print(current_recipe_image)
            print(current_recipe_path)
            recipe_image = request.files['recipe_image']
            if recipe_image and allowed_file(recipe_image.filename):
                if os.path.exists(current_recipe_path):
                    os.remove(os.path.join(
                        app.config['UPLOAD_FOLDER'], current_recipe_image))
                    print('Turejo istrinti: ' + current_recipe_image)
                else:
                    print("The file does not exist")
                # create unique image filename
                filename = secure_filename(recipe_image.filename)
                splited_filename = filename.split(".")
                print('That\'s the filename parts: ' + str(splited_filename))
                suffix = datetime.now().strftime("%y%m%d_%H%M%S")
                new_filename = "_".join(
                            [splited_filename[0], suffix])
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
        return redirect(url_for("manage_products"))
    item = mongo.db.kitchen_tools.find_one({"_id": ObjectId(item_id)})
    return render_template(
            "edit_item.html", item=item)


@app.route("/delete/<recipe_id>")
def delete_recipe(recipe_id):
    '''Delete recipe function'''
    current_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    current_recipe_image = current_recipe.get('recipe_image')
    current_recipe_path = os.path.join(
        app.config['UPLOAD_FOLDER'], current_recipe_image)
    print(current_recipe_image)
    print(current_recipe_path)
    os.remove(os.path.join(
        app.config['UPLOAD_FOLDER'], current_recipe_image))
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/delete_item/<item_id>")
def delete_item(item_id):
    '''Delete an item function from the list'''
    mongo.db.kitchen_tools.remove({"_id": ObjectId(item_id)})
    flash("Item Was Successfully Deleted")
    return redirect(url_for("manage_products"))


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
        if 'recipe_image' not in request.files:
            flash('No file part')
            return redirect(url_for('add_recipe'))
        recipe_image = request.files['recipe_image']
        if recipe_image.filename == "":
            flash('No image selected for uploading')
            return redirect(url_for('add_recipe'))
        if recipe_image and allowed_file(recipe_image.filename):
            filename = secure_filename(recipe_image.filename)
            splited_filename = filename.split(".")
            print('That\'s the filename parts: ' + str(splited_filename))
            suffix = datetime.now().strftime("%y%m%d_%H%M%S")
            new_filename = "_".join(
                [splited_filename[0], suffix])
            filename = ".".join([new_filename, splited_filename[-1]])
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
            "recipe_image": filename,
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
        return redirect(url_for("manage_products"))
    kitchen_tools = mongo.db.kitchen_tools.find().sort("product_name", 1)
    return render_template("add_item.html", kitchen_tools=kitchen_tools)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
