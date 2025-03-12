from bson import ObjectId
import json

from flask import Flask, render_template, request, jsonify, redirect, url_for, g, make_response
from flask.json.provider import JSONProvider
from flask_cors import CORS 
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta


from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.jungle_sunday

app = Flask(__name__)

# JWT 비밀키 설정
JWT_SECRET = 'Sunday'

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
    
app.json = CustomJSONProvider(app)


@app.before_request
def load_current_user():
    g.current_user = None
    if request.endpoint in ['login', 'login_user', 'register', 'register_user']:
        return
    else: 
        # '/login' 라우트에서는 토큰 검증을 하지 않음
        # 다른 라우트에서는 토큰을 검증하고, 'g.current_user'를 설정
        token = request.cookies.get('access_token')
        if token:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload["user_id"]
            g.current_user = user_id
        else:
            return redirect(url_for('login'))

#전체 템플릿에서 사용할 전역변수 설정
@app.context_processor
def inject_user():
   return dict(username = g.current_user)

#GENERAL ROUTE
@app.route('/')
def index():
    if g.current_user != None:
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))


#MAIN HTML
@app.route('/main')
def main():
    try:
      if not g.current_user:
         return redirect(url_for('index'))

      return render_template('main.html',
                            title="Jungle Sunday",
                            heading="Jungle Sunday",
                            sub_head="일요일을 맛있게 보내자!",
                            post="글쓰기",
                            delete="삭제",
                            ) 
    except:
      return redirect(url_for('index'))

@app.route('/main/post', methods=['GET', 'POST'])
def handle_post():
    if request.method == 'GET':
      result = list(db.post.find().sort({'_id': -1}))
      return jsonify({'result': 'success', 'posts': result})
    
    elif request.method == 'POST':
      poster_id_receive = request.form['poster_id_give']
      image_receive = request.form['image_give']
      post_title_receive = request.form['post_title_give']
      post_content_receive = request.form['post_content_give']
      link_receive = request.form['link_give']
      post_time_receive = request.form['post_time_give']

      real_user_name_json = db.users.find_one({"ID": g.current_user}, {"username": 1, "_id": 0})
      real_user_name = real_user_name_json['username']
      print(real_user_name)

      post = {
        'real_user_name': real_user_name,
        'poster_id': poster_id_receive,
        'image': image_receive,
        'post_title': post_title_receive,
        'post_content': post_content_receive,
        'link': link_receive,
        'post_time': post_time_receive,
        'like': 0,
        'dislike': 0,
      }

      db.post.insert_one(post)
      return jsonify({'result': 'success'})

@app.route('/main/post/delete', methods=['POST'])
def delete_post():
  temp_id_receive = request.form['post_id_give']
  poster_id_receive = request.form['poster_id_give']
  if poster_id_receive != g.current_user:
      return jsonify({'result': 'failure'})
  
  id_receive = ObjectId(temp_id_receive)
  result = db.post.delete_one({'_id': id_receive})

  if result.deleted_count == 1:
      return jsonify({'result': 'success'})
  else:
      return jsonify({'result': 'failure'})

@app.route('/main/post/like', methods=['POST'])
def handle_like():
  temp_id_receive = request.form['post_id_give']
  id_receive = ObjectId(temp_id_receive)
  db.post.update_one({'_id': id_receive}, {'$inc': {'like': 1}})
  return jsonify({'result': 'success'})

@app.route('/main/post/dislike', methods=['POST'])
def handle_dislike():
  temp_id_receive = request.form['post_id_give']
  id_receive = ObjectId(temp_id_receive)
  db.post.update_one({'_id': id_receive}, {'$inc': {'dislike': 1}})
  return jsonify({'result': 'success'})


#POST HTML
@app.route('/post')
def post():
  return render_template('post.html',
                          title="글 작성",
                          heading="글 작성",
                          post="게시하기",
                          back="뒤로가기",
                          upload="사진 불러오기",
                          check="장소 확인",
                          )

#USER_INFO HTML
@app.route('/user_info/<poster_id>')
def user_info(poster_id):
   return render_template('user_info.html',
                          title="사용자 정보",
                          classroomNum="수강실",
                          poster_id=poster_id,
                          )

# @app.route('/user_info/<poster_id>', methods=['GET'])
# def get_user_info(poster_id):

#LOGIN
# 로그인 부분 (JWT 할당)
@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/login/signIn', methods=["POST"])
def login_user():
    ID_receive = request.form['ID_give']
    password_receive = request.form['password_give']

    if not ID_receive or not password_receive:
        return jsonify({"result": "error", "message": "아이디과 비밀번호를 입력하세요."})

    # 사용자 조회
    user = db.users.find_one({"ID": ID_receive})
    if not user:
        return jsonify({"result": "error", "message": "사용자가 존재하지 않습니다. 회원가입 해주세요."})

    # 비밀번호 검증
    if not check_password_hash(user['password'], password_receive):
        return jsonify({"result": "error", "message": "비밀번호가 틀렸습니다."})

    # JWT 생성
    payload = {
        "user_id": str(user["ID"]),
        "exp": datetime.now() + timedelta(hours=1)  # 토큰 만료 시간 설정
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    response = make_response(jsonify({"result": "success", "token": token}))
    response.set_cookie('access_token', token, httponly=True, secure=False, samesite='Strict', max_age=3600)

    return response

@app.route('/login/logout', methods=["POST"])
def logout_user():
    response = make_response(jsonify({"result": "success", "message": "로그아웃 되었습니다."}))
    response.set_cookie('access_token', '', max_age=0)  # 쿠키 삭제
    return response

# 보호된 API 예시 (JWT 인증)
@app.route("/protected", methods=["GET"])
def protected():
    token = request.headers.get("Authorization")
    
    if not token:
        return jsonify({"result": "error", "message": "토큰이 필요합니다."})
    
    try:
        token = token.split(" ")[1]  # "Bearer <token>" 형식에서 토큰만 추출
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload["user_id"]
        return jsonify({"result": "success", "message": "인증된 사용자 ID: {user_id}"})
    except jwt.ExpiredSignatureError:
        return jsonify({"result": "error", "message": "토큰이 만료되었습니다."})
    except jwt.InvalidTokenError:
        return jsonify({"result": "error", "message": "유효하지 않은 토큰입니다."})

# 회원가입 API
@app.route("/register")
def register():
   return render_template('register.html')

@app.route("/register", methods=["POST"])
def register_user():
    # 데이터 유효성 검사
    username_receive = request.form['username_give']
    classR_receive = request.form['classR_give']
    OS_receive = request.form['OS_give']
    Email_receive = request.form['Email_give']
    ID_receive = request.form['ID_give']
    password_receive = request.form['password_give']
    place_receive = request.form['place_give']

    if not username_receive or not classR_receive or not ID_receive or not password_receive:
        print('a')
        return jsonify({"result": "error", "message": "아이디와 비밀번호를 입력하세요."})

    # 기존 아이디 중복 확인
    existing_user = db.users.find_one({"ID": ID_receive})
    if existing_user:
        print('b')
        return jsonify({"result": "error", "message": "이미 가입된 아이디 입니다."})

    # 비밀번호 해싱 (보안을 위해)
    hashed_password = generate_password_hash(password_receive, method="pbkdf2:sha256")

    # 사용자 정보 저장
    user = {
        "username": username_receive,
        "classR": classR_receive,
        "OS": OS_receive,
        "email": Email_receive,
        "ID": ID_receive,
        "password": hashed_password,
        "place": place_receive
    }

    try:
        db.users.insert_one(user)
        return jsonify({"result": "success", "message": "회원가입 완료! 로그인 페이지로 이동합니다."})
    except Exception as e:
        return jsonify({"result": "error", "message": "회원가입 중 오류가 발생했습니다: {str(e)}"})



if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)