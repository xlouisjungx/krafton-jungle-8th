from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.jungle_sunday
#이미지, 게시자ID, 설명, 링크, 좋아요, 시간

#db.post.insert_one({'image':'url', 'poster_id':'poster_id', 'explain': 'explain', 'link': 'link', 'likes': '0', 'post_time': 'post_time'})

@app.route('/main')
def main():
    return render_template('main.html',
                           title="Jungle Sunday",
                           heading="Jungle Sunday",
                           sub_head="일요일을 맛있게 보내자!",
                           post="글쓰기",
                           )

@app.route('/main_post', methods=['GET', 'POST'])
def handle_post():
    if request.method == 'GET':
      result = list(db.post.find({}, {'_id': 0}))
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
      }

      db.post.insert_one(post)
      return jsonify({'result': 'success'})
    
@app.route('/post')
def post():
   return render_template('post.html',
                          title="글 작성",
                          heading="글 작성",
                          post="게시하기",
                          back="뒤로가기",
                          upload="사진 불러오기",
                          )

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)