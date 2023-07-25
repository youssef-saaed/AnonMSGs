from funcs import *

app = Flask(__name__)
app.url_map.strict_slashes = False

conn = sqlite3.connect("database.db", check_same_thread=False)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["POST", "GET"])
@login_required
def index():
    if request.method == "GET":
        data = sqliteQuery(conn, "SELECT name, username FROM users WHERE user_id = :ui", {"ui" : session["user_id"]}).fetchall()[0]
        name = data[0]
        username = data[1]
        messages = sqliteQuery(conn, f"SELECT message, resources, name, id FROM _{session['user_id']} LEFT OUTER JOIN users ON sender = user_id ORDER BY id DESC").fetchall()
        return render_template("index.html", name=name, messages=messages, username=username, host=request.base_url)
    else:
        id = request.form.get("msgID")
        resources = sqliteQuery(conn, f"SELECT resources FROM _{session['user_id']} WHERE id = :id", {"id" : id}).fetchall()[0][0]
        sqliteQuery(conn, f"DELETE FROM _{session['user_id']} WHERE id = :id", {"id" : id})
        conn.commit()
        if resources:
            os.remove(resources)
        return apology(200, "OK")

@app.route("/Register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        user = request.form.get("user").lower()
        pass1 = request.form.get("pass1")
        pass2 = request.form.get("pass2")
        if not name or not user or not pass1 or not pass2:
            return render_template("register.html", error="All fields are required")
        if user[0].isnumeric() or not(4 <= len(user) <= 16) or " " in user or "-" in user:
            return render_template("register.html", error="Username should start with letter and not have whitespaces or dashes and its length must be between 4 to 16 characters")
        if pass1 != pass2 or not(8 <= len(pass1) <= 16):
            return render_template("register.html", error="Two passwords must be identical and their length must be between 8 to 16 characters")
        if sqliteQuery(conn, "SELECT * FROM users WHERE username = :user", {"user" : user}).fetchall():
            return render_template("register.html", error="Username exists")
        sqliteQuery(conn, "INSERT INTO users (name, username, password) VALUES (:n, :u, :p)", {"n" : name, "u" : user, "p" : generate_password_hash(pass1)})
        conn.commit()
        session["user_id"] = sqliteQuery(conn, "SELECT user_id FROM users WHERE username = :u", {"u" : user}).fetchall()[0][0]
        sqliteQuery(conn, f"CREATE TABLE _{session['user_id']} (Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, resources TEXT, sender INTEGER DEFAULT NULL, FOREIGN KEY (sender) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE SET DEFAULT)")
        conn.commit()
        return redirect("/")
    else:
        if session.get("user_id"):
            return redirect("/")
        return render_template("register.html")

@app.route("/Login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user").lower()
        pwd = request.form.get("pass")
        if not user or not pwd:
            return render_template("login.html", error="All fields are required")
        data = sqliteQuery(conn, "SELECT * FROM users WHERE username = :u", {"u" : user}).fetchall()
        if data:
            if not check_password_hash(data[0][3], pwd):
                return render_template("login.html", error="Invalid username or password")
            session["user_id"] = data[0][0]
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid username or password")

    else:
        if session.get("user_id"):
            return redirect("/")
        return render_template("login.html")

@app.route("/Logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/user/<username>/", methods=["GET", "POST"])
def sendMessage(username):
    username = str(username).lower()
    data = sqliteQuery(conn, "SELECT user_id, name FROM users WHERE username = :u", {"u" : username}).fetchall()
    if data:
        data = data[0]
    else:
        return apology(404, "Not found")
    user_id = data[0]
    if request.method == "POST":
        voiceMsgPath = ""
        sender = request.form.get("sender")
        msg = request.form.get("msg")
        if not msg:
            return render_template("sendMessage.html", username=data[1], error="You must add text msg")
        if request.files.get("voice"):
            path = f"static/voices/{user_id}"
            if not os.path.exists(path):
                os.mkdir(path)
            voiceMsgPath = f"{path}/{''.join(generate_password_hash(datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + str(randint(1, 1000) + randint(1, 1000))).split('$')[1:])}.wav"
            request.files.get("voice").save(voiceMsgPath)
        if request.form.get("signature") == "main":
            if voiceMsgPath and sender:
                sqliteQuery(conn, f"INSERT INTO _{user_id} (message, resources, sender) VALUES (:m, :r, :s)", {"m" : msg, "r" : voiceMsgPath, "s" : int(sender)})
                conn.commit()
            elif voiceMsgPath:
                sqliteQuery(conn, f"INSERT INTO _{user_id} (message, resources) VALUES (:m, :r)", {"m" : msg, "r" : voiceMsgPath})
                conn.commit()
            else:
                sqliteQuery(conn, f"INSERT INTO _{user_id} (message) VALUES (:m)", {"m" : msg})
                conn.commit()
        return redirect("/success")
    else:
        return render_template("sendMessage.html", username=data[1])

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/friends", methods=["POST", "GET"])
@login_required
def friends():
    if request.method == "POST":
        username = request.form.get("user")
        data = sqliteQuery(conn, "SELECT user_id FROM users WHERE username = :u", {"u" : username}).fetchall()
        if request.form.get("type") == "add":
            if data:
                reciever_id = data[0][0]
                datacheck = sqliteQuery(conn, f"SELECT * FROM friends WHERE p1 = {session['user_id']} AND p2 = {reciever_id}").fetchall()
                if datacheck:
                    return apology(453, "Username already in your friend list or in your sent request list")
                else:
                    if str(session["user_id"]) == str(reciever_id):
                        return apology(454, "You can't add yourself")
                    sqliteQuery(conn, f"INSERT INTO friends (p1, p2) VALUES ({session['user_id']}, {reciever_id})")
                    conn.commit()
                    datacheck = sqliteQuery(conn, f"SELECT * FROM friends WHERE (p1 = {session['user_id']} AND p2 = {reciever_id}) OR (p1 = {reciever_id} AND p2 = {session['user_id']})").fetchall()
                    if len(datacheck) == 2:
                        if not sqliteQuery(conn, f'SELECT * FROM chats WHERE (p1 = {session["user_id"]} AND p2 = {reciever_id}) OR (p2 = {session["user_id"]} AND p1 = {reciever_id})').fetchall():
                            sqliteQuery(conn, f"INSERT OR IGNORE INTO chats (p1, p2) VALUES ({session['user_id']}, {reciever_id})")
                            conn.commit()
                            chat_id = sqliteQuery(conn, f"SELECT chat_id FROM chats WHERE p1 = {session['user_id']} AND p2 = {reciever_id}").fetchall()[0][0]
                            sqliteQuery(conn, f"CREATE TABLE IF NOT EXISTS chat_{chat_id} (Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, sender INTEGER, content TEXT, FOREIGN KEY (sender) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE SET NULL)")
                            conn.commit()
                        return apology(227, "OK")
                    return apology(227, "OK")
            else:
                return apology(452, "Username not found")
        elif request.form.get("type") == "remove":
            if len(sqliteQuery(conn, f'SELECT * FROM friends WHERE (p1 = {session["user_id"]} AND p2 = {data[0][0]}) OR (p2 = {session["user_id"]} AND p1 = {data[0][0]})').fetchall()) == 2:
                sqliteQuery(conn, f'DELETE FROM friends WHERE (p1 = {session["user_id"]} AND p2 = {data[0][0]}) OR (p2 = {session["user_id"]} AND p1 = {data[0][0]})')
                conn.commit()
                return apology(227, "OK")
            else:
                return apology(400, "Something went wrong!")
        elif request.form.get("type") == "cancel":
            if len(sqliteQuery(conn, f'SELECT * FROM friends WHERE (p1 = {session["user_id"]} AND p2 = {data[0][0]}) OR (p2 = {session["user_id"]} AND p1 = {data[0][0]})').fetchall()) == 1 and sqliteQuery(conn, f'SELECT * FROM friends WHERE p1 = {session["user_id"]} AND p2 = {data[0][0]}').fetchall():
                sqliteQuery(conn, f'DELETE FROM friends WHERE p1 = {session["user_id"]} AND p2 = {data[0][0]}')
                conn.commit()
                return apology(227, "OK")
            else:
                return apology(400, "Something went wrong!")
        elif request.form.get("type") == "accept":
            if len(sqliteQuery(conn, f'SELECT * FROM friends WHERE (p1 = {session["user_id"]} AND p2 = {data[0][0]}) OR (p2 = {session["user_id"]} AND p1 = {data[0][0]})').fetchall()) == 1 and sqliteQuery(conn, f'SELECT * FROM friends WHERE p2 = {session["user_id"]} AND p1 = {data[0][0]}').fetchall():
                sqliteQuery(conn, f"INSERT INTO friends (p1, p2) VALUES ({session['user_id']}, {data[0][0]})")
                conn.commit()
                if not sqliteQuery(conn, f'SELECT * FROM chats WHERE (p1 = {session["user_id"]} AND p2 = {data[0][0]}) OR (p2 = {session["user_id"]} AND p1 = {data[0][0]})').fetchall():
                    sqliteQuery(conn, f"INSERT OR IGNORE INTO chats (p1, p2) VALUES ({session['user_id']}, {data[0][0]})")
                    conn.commit()
                    chat_id = sqliteQuery(conn, f"SELECT chat_id FROM chats WHERE p1 = {session['user_id']} AND p2 = {data[0][0]}").fetchall()[0][0]
                    sqliteQuery(conn, f"CREATE TABLE IF NOT EXISTS chat_{chat_id} (Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, sender INTEGER, content TEXT, FOREIGN KEY (sender) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE SET NULL)")
                    conn.commit()
                return apology(227, "OK")
            else:
                return apology(400, "Something went wrong!")
        elif request.form.get("type") == "decline":
            if len(sqliteQuery(conn, f'SELECT * FROM friends WHERE (p1 = {session["user_id"]} AND p2 = {data[0][0]}) OR (p2 = {session["user_id"]} AND p1 = {data[0][0]})').fetchall()) == 1 and sqliteQuery(conn, f'SELECT * FROM friends WHERE p2 = {session["user_id"]} AND p1 = {data[0][0]}').fetchall():
                sqliteQuery(conn, f'DELETE FROM friends WHERE p2 = {session["user_id"]} AND p1 = {data[0][0]}')
                conn.commit()
                return apology(227, "OK")
            else:
                return apology(400, "Something went wrong!")
        return apology(400, "Something went wrong!")


    else:
        friendsReq = list()
        reqSent = list()
        friendsL = list()
        sent = sqliteQuery(conn, f"SELECT username FROM friends JOIN users ON users.user_id = p2 WHERE p1 = {session['user_id']}").fetchall()
        recieved = sqliteQuery(conn, f"SELECT username FROM friends JOIN users ON users.user_id = p1 WHERE p2 = {session['user_id']}").fetchall()
        for u1 in sent:
            friend = False
            for u2 in recieved:
                if u1[0] == u2[0]:
                    friendsL.append(u1[0])
                    friend = True
                    break
            if not friend:
                reqSent.append(u1[0])
        for u1 in recieved:
            friend = False
            for u2 in sent:
                if u1[0] == u2[0]:
                    friend = True
                    break
            if not friend:
                friendsReq.append(u1[0])
        return render_template("friends.html", friendsReq=friendsReq, reqSent=reqSent, friends=friendsL)

@app.route("/chats", methods=["GET", "POST"])
@login_required
def chats():
    if request.method == "POST":
        chat_id = request.form.get("chat_id")
        if sqliteQuery(conn, f"SELECT * FROM chats WHERE chat_id = :ci AND (p1 = {session['user_id']} OR p2 = {session['user_id']})", {"ci" : chat_id}).fetchall():
            return apology(227, "OK")
        else:
            return apology(400, "Something went wrong!")
    else:
        chats = sqliteQuery(conn, f"SELECT name, chat_id FROM chats JOIN users ON p2 = users.user_id WHERE p1 = {session['user_id']}").fetchall() + sqliteQuery(conn, f"SELECT name, chat_id FROM chats JOIN users ON p1 = users.user_id WHERE p2 = {session['user_id']}").fetchall()
        return render_template("chats.html", chats=chats)

@app.route("/chats/<chat_id>", methods=["POST", "GET"])
@login_required
def chat(chat_id):
    if request.method == "POST":
        msg = request.form.get("msg")
        if msg:
            sqliteQuery(conn, f"INSERT INTO chat_{chat_id} (sender, content) VALUES ({session['user_id']}, :c )", {"c" : msg})
            conn.commit()
            return apology(227, "OK")
        else:
            return apology(400, "Something went wrong!")
    else:
        if not sqliteQuery(conn, f"SELECT * FROM chats WHERE chat_id = :ci AND (p1 = {session['user_id']} OR p2 = {session['user_id']})", {"ci" : chat_id}).fetchall():
            return apology(401, "Not authorized")
        else:
            data = sqliteQuery(conn, f"SELECT name FROM chats JOIN users ON p2 = users.user_id WHERE chat_id = {chat_id} AND p1 = {session['user_id']}").fetchall() + sqliteQuery(conn, f"SELECT name, p1 FROM chats JOIN users ON p1 = users.user_id WHERE chat_id = {chat_id} AND p2 = {session['user_id']}").fetchall()
            chat = sqliteQuery(conn, f"SELECT sender, content FROM chat_{chat_id}").fetchall()
            return render_template("chat.html",  name=data[0][0], chat=chat)

@app.errorhandler(HTTPException)
def myExcept(e):
    return apology(e.code, e.name)