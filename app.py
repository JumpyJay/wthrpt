import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from icrawler.builtin import GoogleImageCrawler

from tools import sorry, login_required, lookup, lookin

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///wth.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
# key idea: if clicked on image, use GPS to see how's the weather at user's location
def index():
    rows = db.execute("SELECT * FROM cities WHERE userid=?", session.get("user_id"))
    if rows:
        return render_template("index.html", rows=rows)
    else:
        return render_template("index.html")



@app.route("/wth", methods=["GET", "POST"])
@login_required
def weather():
    if request.method == "POST":
        city = request.form.get("city")
        print(city)
        rzt = lookup(city)
        if not rzt:
            return render_template("check.html", text="enter a valid city")
        if os.path.isfile('static/show/000001.jpg') and os.path.isfile('static/show/000002.jpg') and os.path.isfile('static/show/000003.jpg'):
            os.remove("static/show/000001.jpg")
            os.remove("static/show/000002.jpg")
            os.remove("static/show/000003.jpg")
            print('picture existed and removed')
        google_Crawler = GoogleImageCrawler(storage = {'root_dir': 'static/show'})
        google_Crawler.crawl(keyword = f'{city} city', max_num = 3)
        return render_template("show.html", rzt=rzt, city=city)

    return render_template("check.html")


@app.route("/adc", methods=["GET","POST"])
@login_required
def get_city():
    if request.method == "POST":
        city = request.form.get("acity")
        print(city)
        rzt = lookin(city)
        if not rzt:
            return render_template("add.html", text="enter a valid city")
        if os.path.isfile('static/showt/000001.jpg'):
            os.remove("static/showt/000001.jpg")
        google_Crawler = GoogleImageCrawler(storage = {'root_dir': 'static/showt'})
        google_Crawler.crawl(keyword = f'{city} city', max_num = 1)
        return render_template("showt.html", rzt=rzt, city=city)
    else:
        return render_template("add.html")


@app.route("/add", methods=["POST"])
@login_required
def add_city():
    city = request.form.get("citn")
    rzt = lookin(city)
    weather = rzt["mainw"]
    temp = rzt["temp"]
    country = rzt["cntr"]
    foo = session.get("user_id")
    google_Crawler = GoogleImageCrawler(storage = {'root_dir': f'static/save/{city}'})
    google_Crawler.crawl(keyword = f'{city} city', max_num = 1)

    db.execute("INSERT INTO cities (name, weather, temp, country, userid) VALUES (?, ?, ?, ?, ?)",
               city, weather, temp, country, foo)
    return redirect("/")


@app.route("/edit")
@login_required
def edit_city():
    rows = db.execute("SELECT * FROM cities WHERE userid=?", session.get("user_id"))
    count = db.execute("SELECT COUNT(*) AS n FROM cities WHERE userid=?", session.get("user_id"))
    num = count[0]['n']
    nae = []
    for i in range(num):
        nae.append(rows[i]['name'])
    for i in range(num):
        print(nae[i])

    if rows:
        return render_template("edit.html", rows=rows, nae=nae, i=0)
    else:
        return render_template("edit.html")

@app.route("/faq")
@login_required
def faq():
    return render_template("faq.html")


@app.route("/rm", methods=["POST"])
@login_required
def rm_city():
    city = request.form.get("citm")
    print(city)
    db.execute("DELETE FROM cities WHERE userid=? AND name=?", session.get("user_id"), city)
    return redirect("/edit")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure new username is entered !
        zn = request.form.get("username")
        row = db.execute("SELECT * FROM users WHERE username = ?", zn)
        pz = request.form.get("password")
        if row:
            return render_template("register.html", text="username already existed")

        elif not zn:
            return render_template("register.html", text="please provide username")

        elif not pz:
            return render_template("register.html", text="please provide password")

        elif not request.form.get("confirmation"):
            return render_template("register.html", text="please retype password")

        elif not request.form.get("confirmation") == pz:
            return render_template("register.html", text="password does not match")

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", zn, generate_password_hash(pz))
        return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("login.html", text="please provide username")

        elif not request.form.get("password"):
            return render_template("login.html", text="please provide password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", text="invalid username and/or password")

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    print(f"Flask app name is: {app.name}")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)