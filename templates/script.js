// script.js
document.addEventListener('DOMContentLoaded', () => {
    const commentButton = document.querySelector('.comment-button');
    const commentSection = document.querySelector('.comment-section');
    const submitComment = document.querySelector('.submit-comment');
    const commentInput = document.querySelector('.comment-input');
    const commentsList = document.querySelector('.comments-list');

    commentButton.addEventListener('click', () => {
        // 댓글창 토글
        commentSection.style.display = commentSection.style.display === 'none' ? 'block' : 'none';
    });

    submitComment.addEventListener('click', () => {
        const commentText = commentInput.value;
        if (commentText) {
            // 댓글 추가
            const newComment = document.createElement('div');
            newComment.textContent = commentText;
            commentsList.appendChild(newComment);
            commentInput.value = ''; // 입력창 초기화
        }
    });
});
