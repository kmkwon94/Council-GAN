# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from test_on_folder import runImageTransfer
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)
path = "./static"

# 업로드 HTML 렌더링
@app.route('/')
def render_file():
    return render_template('upload.html')

@app.route('/fileUpload', methods=['GET', 'POST'])
def fileupload():
    check_value = request.form['check_model']

    if request.method == 'POST':
        f = request.files['file']
        # 저장할 경로 + 파일명
        # redirect할 것을 method명으로 처리함
        if check_value == "ani":
            f.save('/home/user/upload/person2anime/' +
            secure_filename(f.filename))
            return redirect(url_for('person_To_anime'))
        elif check_value == "m2f":
            f.save('/home/user/upload/male2female/' +
            secure_filename(f.filename))
            return redirect(url_for('male_To_female'))
        else:
            f.save('/home/user/upload/no_glasses/' +
            secure_filename(f.filename))
            return redirect(url_for('no_glasses'))

#사용자의 입력을 받아서 각 원하는 결과물을 라우팅
@app.route('/person2anime', methods=['GET', 'POST'])
def person_To_anime():
    modelType = "pretrain/anime/256/anime2face_council_folder.yaml"
    #output = "static/person2anime"
    checkpoint = "pretrain/anime/256/01000000"
    input_ = "/home/user/upload/person2anime"
    a2b = 0
    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)

    file_list.sort()
    new_file_list = []
    for i in file_list:
        new_file_list.append(i.replace('static/','')) 
    return render_template('showImage.html', image_names = new_file_list)
    
@app.route('/male2female', methods=['GET', 'POST'])
def male_To_female():
    modelType = "pretrain/m2f/256/male2female_council_folder.yaml"
    #output = "static/male2female"
    checkpoint = "pretrain/m2f/256/01000000"
    input_ = "/home/user/upload/male2female"
    a2b = 1
    
    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)
    
    file_list.sort()
    new_file_list = []
    for i in file_list:
        new_file_list.append(i.replace('static/',''))

    return render_template('showImage.html', image_names = new_file_list)
   
@app.route('/noglasses', methods=['GET', 'POST'])
def no_glasses():
    modelType = "pretrain/glasses_removal/128/glasses_council_folder.yaml"
    #output = "static/no_glasses"
    checkpoint = "pretrain/glasses_removal/128/01000000"
    input_ = "/home/user/upload/no_glasses"
    a2b = 1
    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)    
    
    #no_glasses_path = path + "/img/01000000_all_in_1"
    #file_list = os.listdir(no_glasses_path)
    file_list.sort()
    new_file_list = []
    for i in file_list:
        new_file_list.append(i.replace('static/',''))
    return render_template('showImage.html', image_names = new_file_list)

if __name__ == '__main__':
    # server execute
    app.run(host='0.0.0.0', port=80, debug=True)