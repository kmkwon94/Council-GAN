# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from test_on_folder import runImageTransfer
<<<<<<< HEAD
import os 
import random
import string
import uuid
=======
import os
>>>>>>> f8e00d1b9642c611e6fac4a20e082b59f9c3f8cc

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
<<<<<<< HEAD
        randomDirName = str(uuid.uuid4()) #사용자끼리의 업로드한 이미지가 겹치지 않게끔 uuid를 이용하여 사용자를 구분하는 디렉터리를 만든다.
        if check_value == "ani":
            os.mkdir('/home/user/upload/person2anime/' + randomDirName)
            f.save('/home/user/upload/person2anime/' + randomDirName +'/' +
            secure_filename(f.filename))
            return redirect(url_for('person_To_anime', input_dir = randomDirName))
        elif check_value == "m2f":
            os.mkdir('/home/user/upload/male2female/' + randomDirName)
            f.save('/home/user/upload/male2female/' + randomDirName +'/' +
            secure_filename(f.filename))
            return redirect(url_for('male_To_female', input_dir = randomDirName))
        else:
            os.mkdir('/home/user/upload/no_glasses/' + randomDirName)
            f.save('/home/user/upload/no_glasses/' + randomDirName +'/' +
            secure_filename(f.filename))
            return redirect(url_for('no_glasses', input_dir = randomDirName))

=======
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
>>>>>>> f8e00d1b9642c611e6fac4a20e082b59f9c3f8cc

#사용자의 입력을 받아서 각 원하는 결과물을 라우팅
@app.route('/person2anime', methods=['GET', 'POST'])
def person_To_anime():
<<<<<<< HEAD
    input_dir = request.args.get('input_dir', '_unknown_')
    modelType = "pretrain/anime/256/anime2face_council_folder.yaml"
    checkpoint = "pretrain/anime/256/01000000"
    input_ = "/home/user/upload/person2anime/" + input_dir
    a2b = 0

    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)
    file_list.sort()
    
=======
    modelType = "pretrain/anime/256/anime2face_council_folder.yaml"
    #output = "static/person2anime"
    checkpoint = "pretrain/anime/256/01000000"
    input_ = "/home/user/upload/person2anime"
    a2b = 0
    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)

    file_list.sort()
>>>>>>> f8e00d1b9642c611e6fac4a20e082b59f9c3f8cc
    new_file_list = []
    for i in file_list:
        new_file_list.append(i.replace('static/','')) 
    return render_template('showImage.html', image_names = new_file_list)
    
@app.route('/male2female', methods=['GET', 'POST'])
def male_To_female():
<<<<<<< HEAD
    input_dir = request.args.get('input_dir', '_unknown_')
    modelType = "pretrain/m2f/256/male2female_council_folder.yaml"
    checkpoint = "pretrain/m2f/256/01000000"
    input_ = "/home/user/upload/male2female/" + input_dir
    a2b = 1

    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)
    file_list.sort()

    new_file_list = []
    for i in file_list:
        new_file_list.append(i.replace('static/',''))
=======
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

>>>>>>> f8e00d1b9642c611e6fac4a20e082b59f9c3f8cc
    return render_template('showImage.html', image_names = new_file_list)
   
@app.route('/noglasses', methods=['GET', 'POST'])
def no_glasses():
<<<<<<< HEAD
    input_dir = request.args.get('input_dir', '_unknown_')
    modelType = "pretrain/glasses_removal/128/glasses_council_folder.yaml"
    checkpoint = "pretrain/glasses_removal/128/01000000"
    input_ = "/home/user/upload/no_glasses/" + input_dir
    a2b = 1

    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)    
    file_list.sort()

=======
    modelType = "pretrain/glasses_removal/128/glasses_council_folder.yaml"
    #output = "static/no_glasses"
    checkpoint = "pretrain/glasses_removal/128/01000000"
    input_ = "/home/user/upload/no_glasses"
    a2b = 1
    file_list = runImageTransfer(modelType,checkpoint,input_,a2b)    
    
    #no_glasses_path = path + "/img/01000000_all_in_1"
    #file_list = os.listdir(no_glasses_path)
    file_list.sort()
>>>>>>> f8e00d1b9642c611e6fac4a20e082b59f9c3f8cc
    new_file_list = []
    for i in file_list:
        new_file_list.append(i.replace('static/',''))
    return render_template('showImage.html', image_names = new_file_list)

if __name__ == '__main__':
    # server execute
    app.run(host='0.0.0.0', port=80, debug=True)