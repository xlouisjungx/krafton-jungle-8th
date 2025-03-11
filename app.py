from bson import ObjectId

from flask import Flask, render_template, request, jsonify
from flask.json.provider import JSONProvider
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.jungle_sunday

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

#MAIN HTML
@app.route('/main')
def main():
    return render_template('main.html',
                           title="Jungle Sunday",
                           heading="Jungle Sunday",
                           sub_head="일요일을 맛있게 보내자!",
                           post="글쓰기",
                           )

@app.route('/main/post', methods=['GET', 'POST'])
def handle_post():
    if request.method == 'GET':
      result = list(db.post.find({}))
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
                          )

#USER_INFO HTML
@app.route('/user_info')
def user_info():
   return render_template('user_info.html',
                          title="사용자 정보",
                          )

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)