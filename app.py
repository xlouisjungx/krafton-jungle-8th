from bson import ObjectId

from flask import Flask, render_template, request, jsonify, redirect, url_for, g
from flask.json.provider import JSONProvider
from flask_jwt_extended import JWTManager, verify_jwt_in_request, jwt_required, get_jwt_identity
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.junglesunday

import json

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
    try:
      verify_jwt_in_request(optional=True)  # JWT가 있으면 검증, 없으면 패스
      g.current_user = get_jwt_identity()  # 현재 사용자 정보 저장
    except:
      g.current_user = 'Hi'  # 예외 발생 시 로그인되지 않은 상태로 설정

@app.context_processor
def inject_user():
   return dict(username = g.current_user)


#MAIN HTML
@app.route('/main')
def main():
    try:
      #verify_jwt_in_request(optional=True)
      #current_user = get_jwt_identity()
      if not g.current_user:
         return redirect(url_for('/'))

      return render_template('ach_main.html',
                            title="Jungle Sunday",
                            heading="Jungle Sunday",
                            sub_head="일요일을 맛있게 보내자!",
                            post="글쓰기",
                            delete="삭제",
                            ) 
    except:
      return redirect(url_for('/'))

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

      post = {
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
   

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)