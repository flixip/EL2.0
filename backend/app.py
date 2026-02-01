from flask import Flask,request,jsonify,send_from_directory
from flask_cors import CORS
import ultralytics
import os
import json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

app = Flask(__name__)
CORS(app)

model = ultralytics.YOLO(f'{BASE_DIR}/utils/model/best.pt')



@app.route('/data')
def index():
    return jsonify(
        {'message': 'Hello, Vue!'}
        )

@app.route('/temp/<path:filename>')
def serve_temp_dir(filename):
    return send_from_directory(TEMP_DIR, filename)


# 提供中国省界以及省界下二级区划的geojson文件
@app.route('/geodata/<path:filename>')
def get_geojson(filename):
    return send_from_directory(f'{BASE_DIR}/src/ChinaGeodata', filename)

# 提供中国地理数据映射表
@app.route('/geodataMap')
def get_geodata_map():
    with open(f'{BASE_DIR}/src/geodataUrlMap.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)


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