from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS 
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

CORS(app, resources={r"/register": {"origins": "*"}})

# MongoDB 연결 설정
app.config["MONGO_URI"] = "mongodb://localhost:27017/jungle_sunday"
mongo = PyMongo(app)

# JWT 비밀키 설정
JWT_SECRET = 'Sunday'

# 회원가입 API
@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    # 데이터 유효성 검사
    username = data.get("username")
    classR = data.get("classR")
    OS = data.get("OS")
    Email = data.get("email")
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
        "email": Email,
        "ID": ID,
        "password": hashed_password,
        "place": place
    }

    try:
        mongo.db.users.insert_one(user)
        return jsonify({"result": "success", "message": "회원가입 완료! 로그인 페이지로 이동합니다."})
    except Exception as e:
        return jsonify({"result": "error", "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"}), 500

# 로그인 부분 (JWT 할당)
@app.route('/login', methods=["POST"])
def login_user():
    data = request.get_json()
    
    Email = data.get("Email")
    password = data.get("password")

    if not Email or not password:
        return jsonify({"result": "error", "message": "이메일과 비밀번호를 입력하세요."}), 400

    # 사용자 조회
    user = mongo.db.users.find_one({"Email": Email})
    if not user:
        return jsonify({"result": "error", "message": "사용자가 존재하지 않습니다. 회원가입 해주세요."}), 400

    # 비밀번호 검증
    if not check_password_hash(user['password'], password):
        return jsonify({"result": "error", "message": "비밀번호가 틀렸습니다."}), 400

    # JWT 생성
    payload = {
        "user_id": str(user["_id"]),
        "exp": datetime.utcnow() + timedelta(hours=1)  # 토큰 만료 시간 설정
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return jsonify({"result": "success", "token": token})

# 보호된 API 예시 (JWT 인증)
@app.route("/protected", methods=["GET"])
def protected():
    token = request.headers.get("Authorization")
    
    if not token:
        return jsonify({"result": "error", "message": "토큰이 필요합니다."}), 403
    
    try:
        token = token.split(" ")[1]  # "Bearer <token>" 형식에서 토큰만 추출
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["user_id"]
        return jsonify({"result": "success", "message": f"인증된 사용자 ID: {user_id}"})
    except jwt.ExpiredSignatureError:
        return jsonify({"result": "error", "message": "토큰이 만료되었습니다."}), 403
    except jwt.InvalidTokenError:
        return jsonify({"result": "error", "message": "유효하지 않은 토큰입니다."}), 403



if __name__ == "__main__":
    app.run(debug=True, port=5001)
