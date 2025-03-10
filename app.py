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
                           sub_head="일요일을 맛있게 보내자!")

@app.route('/main_post', methods=['GET', 'POST'])
def handle_post():
    if request.method == 'GET':
      result = list(db.post.find())
      return jsonify({'result': 'success', 'poss': result})
    
    elif request.method == 'POST':
      data = request.get_json()
      db.post.insert_one(data)
      return jsonify({'result': 'success', 'posts': result})

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5001,debug=True)