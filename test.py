from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import json
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# JSON 파일 경로
comments_file = 'comments.json'

# 코멘트 로드 함수
def load_comments():
    if os.path.exists(comments_file):
        with open(comments_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# 코멘트 저장 함수
def save_comments(comments):
    with open(comments_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

# 코멘트 가져오기
@app.route('/comments', methods=['GET'])
def get_comments():
    comments = load_comments()
    return jsonify(comments)

# 코멘트 추가하기
@app.route('/comments', methods=['POST'])
def add_comment():
    new_comment = request.json
    if not new_comment or 'text' not in new_comment:
        return jsonify({'error': 'Invalid comment data'}), 400

    comments = load_comments()
    comments.append(new_comment)
    save_comments(comments)
    socketio.emit('new_comment', new_comment)  # 새로운 코멘트를 모든 클라이언트에 전송
    return jsonify(new_comment), 201

# 코멘트 수정하기
@app.route('/comments/<int:index>', methods=['PUT'])
def update_comment(index):
    updated_comment = request.json
    if not updated_comment or 'text' not in updated_comment:
        return jsonify({'error': 'Invalid comment data'}), 400

    comments = load_comments()
    if 0 <= index < len(comments):
        comments[index] = updated_comment
        save_comments(comments)
        socketio.emit('update_comment', {'index': index, 'comment': updated_comment})  # 수정된 코멘트를 모든 클라이언트에 전송
        return jsonify(updated_comment), 200
    return jsonify({'error': 'Comment not found'}), 404

# 코멘트 삭제하기
@app.route('/comments/<int:index>', methods=['DELETE'])
def delete_comment(index):
    comments = load_comments()
    if 0 <= index < len(comments):
        deleted_comment = comments.pop(index)  # 코멘트 삭제
        save_comments(comments)  # 변경사항 저장
        socketio.emit('delete_comment', index)  # 클라이언트로 삭제된 코멘트 알림
        return jsonify(deleted_comment), 200
    return jsonify({'error': 'Comment not found'}), 404

# 정적 파일 제공
@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

if __name__ == '__main__':
    # 모든 IP에서 접근 가능하도록 설정
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
