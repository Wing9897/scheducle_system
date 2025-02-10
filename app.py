from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, abort
from functools import wraps
from flask_bcrypt import Bcrypt

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
from pymongo import MongoClient
import uuid
from bson import ObjectId  # 確保導入 ObjectId
import ics
from io import BytesIO

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 請修改為安全的隨機字串

bcrypt = Bcrypt(app)

# === MongoDB 連線設定 ===
client = MongoClient("mongodb://localhost:27017/")
db = client["my_calendar_app_db"]
users_collection = db["users"]  # 用於存儲使用者帳號密碼

# ========== 路由 (Web) ==========

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    email = request.form.get("email")
    password = request.form.get("password")

    # 檢查是否已存在相同 email
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return "此 Email 已被註冊，請使用其他 Email 或登入。"

    # 建立使用者
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    users_collection.insert_one({
        "email": email,
        "password_hash": pw_hash
    })

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("email")
    password = request.form.get("password")

    user = users_collection.find_one({"email": email})
    if not user:
        return "無此使用者，請先註冊。"

    if bcrypt.check_password_hash(user["password_hash"], password):
        # 登入成功
        session["user_id"] = email
        return redirect(url_for("dashboard"))
    else:
        return "密碼錯誤，請重新嘗試。"


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/create_event", methods=["GET", "POST"])
def create_event_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("create_event.html")

    user_id = session["user_id"]
    user_calendar_collection = db[user_id]  # 每個使用者有獨立的 collection

    # 從表單獲取事件資料
    event = {
        "uid": str(uuid.uuid4()) + "@example.com",  # 唯一識別符
        "summary": request.form.get("summary"),
        "description": request.form.get("description"),
        "location": request.form.get("location"),
        "dtstart": request.form.get("dtstart"),
        "dtend": request.form.get("dtend"),
        "timezone": request.form.get("timezone"),
        "visibility": request.form.get("visibility"),
        "userId": user_id
    }

    # 儲存事件到 MongoDB
    user_calendar_collection.insert_one(event)

    return redirect(url_for("dashboard"))

# ========== JSON API 路由 ==========

@app.route("/api/events", methods=["GET"])
def api_get_events():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    user_calendar_collection = db[user_id]

    # 取得所有事件，確保 `_id` 轉為 `str`
    events_cursor = user_calendar_collection.find({})
    events = []

    for event in events_cursor:
        events.append({
            "_id": str(event["_id"]),  # 轉換 `_id` 讓前端可讀取
            "uid": event.get("uid", str(uuid.uuid4()) + "@example.com"),
            "title": event.get("summary", "No Title"),
            "start": event.get("dtstart", ""),
            "end": event.get("dtend", ""),
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "timezone": event.get("timezone", "UTC"),
            "visibility": event.get("visibility", "public")
        })

    return jsonify(events), 200






@app.route("/api/events", methods=["POST"])
def api_create_event():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.json
    if not data or "event" not in data:
        return jsonify({"error": "No event data provided"}), 400

    event_data = data["event"]

    # 獲取當前用戶 ID
    user_id = session["user_id"]
    user_calendar_collection = db[user_id]  # 取得該用戶的事件 collection

    # 產生唯一事件 ID
    event_data["uid"] = str(uuid.uuid4()) + "@example.com"
    event_data["userId"] = user_id  # 記錄用戶

    # 存入 MongoDB
    result = user_calendar_collection.insert_one(event_data)

    # **將 MongoDB _id 轉換成字串，讓前端可見**
    event_data["_id"] = str(result.inserted_id)

    return jsonify({"message": "Event created", "event": event_data}), 201



@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/api/events/<event_id>", methods=["DELETE"])
def api_delete_event(event_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    user_calendar_collection = db[user_id]

    try:
        # Convert string ID to ObjectId
        result = user_calendar_collection.delete_one({"_id": ObjectId(event_id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Event not found"}), 404
            
        return jsonify({"message": "Event deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/download_ics")
def download_ics():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user_calendar_collection = db[user_id]

    # 獲取所有 public 事件
    events = user_calendar_collection.find({"visibility": "public"})

    # 創建 ICS 日曆
    calendar = ics.Calendar()

    for event in events:
        calendar_event = ics.Event(
            uid=event["uid"],
            name=event["summary"],
            description=event["description"],
            location=event["location"],
            begin=event["dtstart"],
            end=event["dtend"],
            created=event.get("created_at", None),
            last_modified=event.get("updated_at", None)
        )
        calendar.events.add(calendar_event)

    # 將日曆轉為字符串
    ics_content = str(calendar)

    # 創建文件對象
    mem = BytesIO()
    mem.write(ics_content.encode('utf-8'))
    mem.seek(0)

    return send_file(
        mem,
        mimetype="text/calendar",
        as_attachment=True,
        download_name="events.ics",
        mode='rb'
    )


if __name__ == "__main__":
    app.run(debug=True)
