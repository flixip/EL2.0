from flask import Flask,request,jsonify,send_from_directory
from flask_cors import CORS
import ultralytics
import os


app = Flask(__name__)
CORS(app)

model = ultralytics.YOLO('backend/utils/model/best.pt')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

@app.route('/data')
def index():
    return jsonify(
        {'message': 'Hello, Vue!'}
        )

@app.route('/temp/<path:filename>')
def serve_temp_dir(filename):
    return send_from_directory(TEMP_DIR, filename)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    filename = file.filename
    file.save(f'{TEMP_DIR}/{filename}')
    results = model.predict(
        source=f'{TEMP_DIR}/{filename}',
        conf = 0.5,
        save = True,
        project = TEMP_DIR,
        name = 'predict',
        exist_ok = True,
        )
    
    img_url = f'http://localhost:5000/temp/predict/{filename}'
    # 预测之后生成jpg了，但是url是png
    # 所以前端要显示jpg，要自己处理一下
    img_url = img_url.split('.')[0] + '.jpg'
    print(img_url)
    
    return jsonify(
        {'message': 'Upload success!',
        'img_url': img_url,
        'status':'success',
        }
        )
if __name__ == '__main__':
    app.run(debug=True)