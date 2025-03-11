from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS 
from werkzeug.security import generate_password_hash

app = Flask(__name__)

CORS(app, resources={r"/register": {"origins": "*"}})

# MongoDB 연결 설정
app.config["MONGO_URI"] = "mongodb://localhost:27017/jungle_sunday"
mongo = PyMongo(app)

# 회원가입 API
@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    # 데이터 유효성 검사
    username = data.get("username")
    classR = data.get("classR")
    OS = data.get("OS")
    ID = data.get("ID")
    password = data.get("password")
    place = data.get("place")

    if not username or not classR or not ID or not password:
        return jsonify({"result": "error", "message": "아이디와 비밀번호를 입력하세요."}), 400

    # 기존 아이디 중복 확인
    existing_user = mongo.db.users.find_one({"ID": ID})
    if existing_user:
        return jsonify({"result": "error", "message": "이미 가입된 아이디 입니다."}), 400

    # 비밀번호 해싱 (보안을 위해)
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    # 사용자 정보 저장
    user = {
        "username": username,
        "classR": classR,
        "OS": OS,
        "ID": ID,
        "password": hashed_password,
        "place": place
    }

    try:
        mongo.db.users.insert_one(user)
        return jsonify({"result": "success", "message": "회원가입이 완료되었습니다."})
    except Exception as e:
        return jsonify({"result": "error", "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
