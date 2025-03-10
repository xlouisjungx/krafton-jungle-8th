express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');

const app = express();
const port = 5001;

const cors = require('cors');
app.use(cors());

// MongoDB 연결
mongoose.connect('mongodb://localhost:27017/jungleSunday', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('MongoDB 연결 성공'))
    .catch(err => console.log('MongoDB 연결 실패:', err));

// 사용자 모델
const UserSchema = new mongoose.Schema({
    username: String,
    password: String
});

const User = mongoose.model('User', UserSchema);

// JSON 데이터를 처리할 수 있게 설정
app.use(bodyParser.json());

// POST 요청 처리
app.post('/save_id', async (req, res) => {
    const { username, password } = req.body;

    // 데이터가 없으면 에러 메시지 반환
    if (!username || !password) {
        return res.json({ result: 'error', message: '아이디와 비밀번호를 모두 입력하세요!' });
    }

    // 사용자 정보 저장
    const newUser = new User({ username, password });

    try {
        await newUser.save();
        res.json({ result: 'success', message: '회원가입이 완료되었습니다.' });
    } catch (error) {
        res.json({ result: 'error', message: '회원가입 중 오류가 발생했습니다.' });
    }
});

// 서버 시작
app.listen(port, () => {
    console.log(`서버가 http://localhost:${port}에서 실행 중`);
});