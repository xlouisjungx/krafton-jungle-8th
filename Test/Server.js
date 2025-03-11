// MongoDB에 연결하는 서버

const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
const port = 5001;

// MongoDB 연결
mongoose.connect("mongodb://localhost:27017/jungle_sunday", {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
    .then(() => console.log("MongoDB 연결 성공 ✅"))
    .catch(err => console.error("MongoDB 연결 실패 ❌", err));

// 미들웨어 설정
app.use(cors());
app.use(bodyParser.json());

// User 스키마 생성
const UserSchema = new mongoose.Schema({
    username: String,
    classR: String,
    OS: String,
    ID: String,
    password: String
});

const User = mongoose.model("User", UserSchema);

// 회원가입 API
app.post("/register", async (req, res) => {
    const { username, classR, OS, ID, password } = req.body;

    // 데이터 유효성 검사
    if (!username || !classR || !ID || !password) {
        return res.status(400).json({ result: "error", message: "아이디와 비밀번호를 입력하세요." });
    }

    // 기존 아이디 중복 확인
    const existingUser = await User.findOne({ ID });
    if (existingUser) {
        return res.status(400).json({ result: "error", message: "이미 가입한 아이디 입니다." });
    }

    // 사용자 정보 저장
    const newUser = new User({ username, classR, OS, ID, password });

    try {
        await newUser.save();
        res.json({ result: "success", message: "회원가입이 완료되었습니다." });
    } catch (error) {
        res.status(500).json({ result: "error", message: "회원가입 중 오류가 발생했습니다." });
    }
});

// 서버 실행
app.listen(port, () => {
    console.log(`✅ 서버가 실행 중입니다: http://localhost:${port}`);
});