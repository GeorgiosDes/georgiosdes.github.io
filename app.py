import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = "./static/images"
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png"}

Session(app)

db = SQL("user=postgres password=[YOUR-PASSWORD] host=db.cozntgvceexyqiyectjs.supabase.co port=5432 database=postgres")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        user = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        if len(user) != 1 or not check_password_hash(user[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return redirect("/login")

        session["user_id"] = user[0]["id"]
        session["user_name"] = user[0]["username"]
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if (request.form.get("password") != request.form.get("confirmation")):
            flash("Passwords do not match")
            return redirect("/register")

        email = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        if len(email) == 1:
            flash("Email already in use")
            return redirect("/register")

        username = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(username) == 1:
            flash("Username is taken")
            return redirect("/register")

        username = request.form.get("username")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))

        id = db.execute("INSERT INTO users (username, email, hash) VALUES (?, ?, ?)", username, email, password)

        session["user_id"] = id
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["user_name"] = user[0]["username"]
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        recipe = request.form.get("name")
        ingredients = request.form.get("ingredients")
        instructions = request.form.get("instructions")
        creator = session["user_id"]
        photo = request.files.get("filename")

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        else:
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], "default.jpg")

        db.execute("INSERT INTO recipes (recipe_name, ingredients, photo, instructions, creator_id) VALUES (?, ?, ?, ?, ?)", recipe, ingredients, photo_path, instructions, creator)
        return redirect("/search")

    else:
        return render_template("create.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search = request.form.get("search")

        if search:
            word = search.split()
            if len(word) == 1:
                recipes = db.execute("SELECT * FROM recipes JOIN users ON recipes.creator_id = users.id WHERE recipe_name LIKE ? OR ingredients LIKE ?", f"%{search}%", f"%{search}%")
                return render_template("search.html", recipes=recipes)

            elif len(word) == 2:
                recipes = db.execute("SELECT * FROM recipes JOIN users ON recipes.creator_id = users.id WHERE (recipe_name LIKE ? AND recipe_name LIKE ?)", f"%{search[0]}%", f"%{search[1]}%")
                return render_template("search.html", recipes=recipes)

    else:
        sort_by = request.args.get("sort_by")

        if sort_by == "name_asc":
            recipes = db.execute("SELECT * FROM recipes JOIN users ON recipes.creator_id = users.id ORDER BY recipe_name ASC")
            return render_template("search.html", recipes=recipes)
        if sort_by == "name_desc":
            recipes = db.execute("SELECT * FROM recipes JOIN users ON recipes.creator_id = users.id ORDER BY recipe_name DESC")
            return render_template("search.html", recipes=recipes)
        if sort_by == "latest":
            recipes = db.execute("SELECT * FROM recipes JOIN users ON recipes.creator_id = users.id ORDER BY id DESC LIMIT 5")
            return render_template("search.html", recipes=recipes)
        else:
            recipes = db.execute("SELECT *, users.username FROM recipes JOIN users ON recipes.creator_id = users.id ORDER BY id DESC LIMIT 5;")
            return render_template("search.html", recipes=recipes)


@app.route("/settings", methods=["GET"])
@login_required
def settings():
    return render_template("settings.html")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":
        if (request.form.get("newPass") != request.form.get("confPass")):
            flash("Passwords don't match")
            return redirect("/settings")

        password = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["hash"]
        new_password = generate_password_hash(request.form.get("newPass"))

        if not check_password_hash(password, request.form.get("currentPass")):
            flash("Current password is incorrect")
            return redirect("/settings")

        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_password, session["user_id"])
        flash("Password changed")
        return redirect("/settings")

    else:
        return render_template("password.html")


@app.route("/username", methods=["GET", "POST"])
@login_required
def username():
    if request.method == "POST":
        username = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(username) == 1:
            flash("Username is taken")
            return redirect("/settings")

        new_username = request.form.get("username")
        db.execute("UPDATE users SET username = ? WHERE id = ?", new_username, session["user_id"])
        flash("Username changed")
        return redirect("/settings")

    else:
        return render_template("username.html")


@app.route("/email", methods=["GET", "POST"])
@login_required
def email():
    if request.method == "POST":
        if (request.form.get("newEmail") != request.form.get("confEmail")):
            flash("Emails don't match")
            return redirect("/settings")

        new_user = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("newEmail"))
        if len(new_user) == 1:
            flash("Email already in use")
            return redirect("/settings")

        new_email = request.form.get("newEmail")
        db.execute("UPDATE users SET email = ? WHERE id = ?", new_email, session["user_id"])
        flash("Email changed")
        return redirect("/settings")

    else:
        return render_template("email.html")


@app.route("/myrecipes", methods=["GET"])
@login_required
def myrecipes():
    recipes = db.execute("SELECT * FROM recipes WHERE creator_id = ?", session["user_id"])
    if (recipes):
        return render_template("myrecipes.html", recipes=recipes)
    else:
        flash("You dont have any recipes")
        return redirect("/create")


@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    if request.method == "POST":
        recipe = request.form.get("edit-name")
        ingredients = request.form.get("edit-ingredients")
        instructions = request.form.get("edit-instructions")
        photo = request.files.get("edit-filename")
        old_photo = db.execute("SELECT photo FROM recipes WHERE id = ?", recipe_id)

        if photo and allowed_file(photo.filename):
            old_photo_path = old_photo[0]["photo"]
            if old_photo_path != os.path.join(app.config["UPLOAD_FOLDER"], "default.jpg"):
                os.remove(old_photo_path)
            filename = secure_filename(str(recipe_id) + "_" + photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            db.execute("UPDATE recipes SET photo = ? WHERE id = ?", photo_path, recipe_id)

        else:
            photo_path = old_photo[0]

        db.execute("UPDATE recipes SET recipe_name = ?, ingredients = ?, instructions = ? WHERE id = ?", recipe, ingredients, instructions, recipe_id)
        flash("Changes saved")
        return redirect("/myrecipes")

    else:
        recipe = db.execute("SELECT * FROM recipes WHERE id = ? ORDER BY recipe_name ASC", recipe_id)
        return render_template("edit_recipe.html", recipe=recipe)
