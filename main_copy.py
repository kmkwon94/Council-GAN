# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, after_this_request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from test_on_folder import runImageTransfer
from utils import get_config, get_data_loader_folder, pytorch03_to_pytorch04
from trainer_council import Council_Trainer
from torch import nn
from scipy.stats import entropy
import torch.nn.functional as F
from torch.autograd import Variable
from data import ImageFolder
import numpy as np
import torchvision.utils as vutils
try:
    from itertools import izip as zip
except ImportError: # will be 3.x series
    pass
import torch
import os 
import random
import string
import uuid
import shutil
from queue import Queue, Empty
import threading
from tqdm import tqdm
#import PIL
#from PIL import Image, ImageOps
#import base64
#import io
from after_response import AfterResponse, AfterResponseMiddleware

app = Flask("after_response")

app.config['JSON_AS_ASCII'] = False
AfterResponse(app)
CORS(app)
path = "./static"

############################################################
#preload model
def loadModel(config, checkpoint, a2b):
    seed = 1

    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    # Load experiment setting
    config = get_config(config)
    input_dim = config['input_dim_a'] if a2b else config['input_dim_b']
    council_size = config['council']['council_size']

    style_dim = config['gen']['style_dim']
    trainer = Council_Trainer(config)
    only_one = False
    if 'gen_' in checkpoint[-21:]:
        state_dict = torch.load(checkpoint)
        try:
            print(state_dict)
            if a2b:
                trainer.gen_a2b_s[0].load_state_dict(state_dict['a2b'])
            else:
                trainer.gen_b2a_s[0].load_state_dict(state_dict['b2a'])
        except:
            print('a2b should be set to ' + str(not a2b) + ' , Or config file could be wrong')
            a2b = not a2b
            if a2b:
                trainer.gen_a2b_s[0].load_state_dict(state_dict['a2b'])
            else:
                trainer.gen_b2a_s[0].load_state_dict(state_dict['b2a'])
                
        council_size = 1
        only_one = True
    else:
        for i in range(council_size):
            try:
                if a2b:
                    tmp_checkpoint = checkpoint[:-8] + 'a2b_gen_' + str(i) + '_' + checkpoint[-8:] + '.pt'
                    state_dict = torch.load(tmp_checkpoint)
                    trainer.gen_a2b_s[i].load_state_dict(state_dict['a2b'])
                else:
                    tmp_checkpoint = checkpoint[:-8] + 'b2a_gen_' + str(i) + '_' + checkpoint[-8:] + '.pt'
                    state_dict = torch.load(tmp_checkpoint)
                    trainer.gen_b2a_s[i].load_state_dict(state_dict['b2a'])
            except:
                print('a2b should be set to ' + str(not a2b) + ' , Or config file could be wrong')
                
                a2b = not a2b
                if a2b:
                    tmp_checkpoint = checkpoint[:-8] + 'a2b_gen_' + str(i) + '_' + checkpoint[-8:] + '.pt'
                    state_dict = torch.load(tmp_checkpoint)
                    trainer.gen_a2b_s[i].load_state_dict(state_dict['a2b'])
                else:
                    tmp_checkpoint = checkpoint[:-8] + 'b2a_gen_' + str(i) + '_' + checkpoint[-8:] + '.pt'
                    state_dict = torch.load(tmp_checkpoint)
                    trainer.gen_b2a_s[i].load_state_dict(state_dict['b2a'])

    trainer.cuda()
    trainer.eval()

    return [trainer, config, council_size, style_dim]

peson2anime_preloadModel = loadModel("pretrain/anime/256/anime2face_council_folder.yaml", "pretrain/anime/256/01000000", 0)
male2female_preloadModel = loadModel("pretrain/m2f/256/male2female_council_folder.yaml", "pretrain/m2f/256/01000000", 1)
noglasses_preloadModel = loadModel("pretrain/glasses_removal/128/glasses_council_folder.yaml", "pretrain/glasses_removal/128/01000000", 1)
############################################################

#handling over request by status code 429
requests_queue = Queue()
BATCH_SIZE = 3
CHECK_INTERVAL = 0.1
remember_user_key = ''
model_type = ''
def handle_requests_by_batch():
    while True:
        #BATCH_SIZE보다 크면 안에 있는 루프를 빠져나와서 requests_batch를 초기화한다.
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE): #BATCH_SIZE 보다 작을때만 돈다 
            try:
                #request_queue에 있는 내용물들을 꺼내서 requests_batch에 담는다.
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue

threading.Thread(target=handle_requests_by_batch).start()

# 업로드 HTML 렌더링
@app.route('/')
def render_file():
    return render_template('upload.html')

@app.route('/healthz', methods=['GET'])
def healthz():
    return "", 200

@app.route('/fileUpload', methods=['GET','POST'])
def fileupload():
    #내가 전달 받는 request는 'file'과 'check_model'

    check_value = request.form['check_model']
    f = request.files['file']

    if requests_queue.qsize() >= BATCH_SIZE:
        return Response("Too many requests plese try again later", status=429)
    req = {
        'input': [check_value, f]
    }
    requests_queue.put(req)
    print("here1")
    try:
        # 저장할 경로 + 파일명
        # redirect할 것을 method명으로 처리함
        #randomDirName = str(uuid.uuid4()) #사용자끼리의 업로드한 이미지가 겹치지 않게끔 uuid를 이용하여 사용자를 구분하는 디렉터리를 만든다.
        randomDirName = str(uuid.uuid4())
        print("here2")
        if check_value == "ani":
            os.mkdir('/home/user/upload/person2anime/' + randomDirName)
            f.save('/home/user/upload/person2anime/' + randomDirName +'/' +
            secure_filename(f.filename))
            person_To_anime(randomDirName)
            #return redirect(url_for('person_To_anime', input_dir = randomDirName))
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
    except Exception as e:
        print(e)
        return Response("upload file and load model is fail", status=400)

#사용자의 입력을 받아서 각 원하는 결과물을 라우팅
#@app.route('/person2anime', methods=['GET', 'POST'])
def person_To_anime(randomDirName):
    try:
        #input_dir = request.args.get('input_dir', '_unknown_')
        input_dir = randomDirName
        input_ = "/home/user/upload/person2anime/" + input_dir
        a2b = 0
        global model_type
        global remember_user_key
        model_type = 'person2anime'
        remember_user_key = input_dir
        print(input_dir)
        print(input_)
        print(model_type)
        print(remember_user_key)

        file_list = runImageTransfer(peson2anime_preloadModel, input_, input_dir, a2b)
        file_list.sort()
        
        
        output_dir = file_list[0].replace('static/img/','')
        output_dir = output_dir.replace('/_out_0_0.jpg','').strip()
        '''
        for i in file_list:
            imgFile = np.array(PIL.Image.open(i).convert("RGB"))
            imgFile = PIL.Image.fromarray(imgFile)
            img_io = io.BytesIO()
            imgFile.save(img_io, 'jpeg', quality=100)
            img_io.seek(0)
            img = base64.b64encode(img_io.getvalue())
            #return render_template(‘index.html’, img = img.decode(‘ascii’)
        '''
        new_file_list = []
        for i in file_list:
            new_file_list.append(i.replace('static/',''))
        return render_template('showImage.html', image_names = new_file_list)
    except Exception as e:
        print(e)
        return Response("person2anime is fail", status=400)    

@app.route('/male2female', methods=['GET', 'POST'])
def male_To_female():
    try:
        input_dir = request.args.get('input_dir', '_unknown_')
        input_ = "/home/user/upload/male2female/" + input_dir
        a2b = 1
        global model_type
        global remember_user_key
        model_type = 'person2anime'
        remember_user_key = input_dir

        file_list = runImageTransfer(male2female_preloadModel, input_, input_dir, a2b)
        file_list.sort()

        output_dir = file_list[0].replace('static/img/','')
        output_dir = output_dir.replace('/_out_0_0.jpg','').strip()

        new_file_list = []
        for i in file_list:
            new_file_list.append(i.replace('static/',''))
        print(new_file_list)
        return render_template('showImage.html', image_names = new_file_list)
    except Exception as e:
        print(e)
        return Response("male2female is fail", status=400)
   
@app.route('/noglasses', methods=['GET', 'POST'])
def no_glasses():
    try:
        input_dir = request.args.get('input_dir', '_unknown_')
        input_ = "/home/user/upload/no_glasses/" + input_dir
        a2b = 1
        global model_type
        global remember_user_key
        model_type = 'person2anime'
        remember_user_key = input_dir

        file_list = runImageTransfer(noglasses_preloadModel, input_, input_dir, a2b)    
        file_list.sort()
       
        output_dir = file_list[0].replace('static/img/','')
        output_dir = output_dir.replace('/_out_0_0.jpg','').strip()
        
        new_file_list = []
        for i in file_list:
            new_file_list.append(i.replace('static/',''))
        print(new_file_list)
        return render_template('showImage.html', image_names = new_file_list)
    except Exception as e:
        print(e)
        return Response("no_glasses is fail", status=400)


@app.after_response
def remove():
    remove_id = remember_user_key.strip()
    remove_input_dir = '/home/user/upload/' + model_type + '/' + remove_id 
    path = os.path.join('static/img/', remove_id)
    print("now I start to remove file")
    print("user key is " + remove_id)
    print("To delete input path " + remove_input_dir)
    print("To delete output path " + path)

    #output path를 삭제하는 try 문
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            return print("Delete " + path + " is completed")
    except Exception as e:
        return print("Delete" + path + " is failed")
    #input path를 삭제하는 try 문
    try:
        if os.path.isdir(remove_input_dir):
            shutil.rmtree(remove_input_dir)
            return print("Delete" + remove_input_dir + " is completed")
    except Exception as e:
        return print("Delete" + remove_input_dir + " is failed")
'''
#@app.route('/removeInputDir/home/user/upload/<model_type>/<input_dir>', methods=['GET', 'POST'])
@app.after_response
def removeInputDir(model_type, input_dir):
    remove_input_dir = '/home/user/upload/' + model_type + '/' + input_dir 
    print("now I start to remove input file")
    print("input dir is " + remove_input_dir)
    try:
        if os.path.isdir(remove_input_dir):
            shutil.rmtree(remove_input_dir)
            return Response("Delete complete", status=200)
        else:
            return Response("There is nothing to Delete", status=400)
    except Exception as e:
        return Response("There is nothing to delete please Try again", status=400)
'''
if __name__ == '__main__':
    # server execute
    app.run(host='0.0.0.0', port=80, debug=True)