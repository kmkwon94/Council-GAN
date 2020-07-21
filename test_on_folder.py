"""
Copyright (C) 2018 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""
from __future__ import print_function
from utils import get_config, get_data_loader_folder, pytorch03_to_pytorch04
from trainer_council import Council_Trainer
from torch import nn
from scipy.stats import entropy
import torch.nn.functional as F
import argparse
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
import shutil
import uuid
from tqdm import tqdm

image_determination = [False,False,False]

def set_image_determination(i):
    image_determination[i] = True

def get_image_determination(i):
    return image_determination[i]

def eraseUploadImage():
    file_list= []
    if get_image_determination(0) == True:
        path= './upload/person2anime'
        file_list = os.listdir(path)
        for i in file_list:
            os.remove(i)
    elif get_image_determination(1) == True:
        path= './upload/male2female'
        file_list = os.listdir(path)
        for i in file_list:
            os.remove(i)
    else:
        path= './upload/no_glasses'
        file_list = os.listdir(path)
        for i in file_list:
            os.remove(i)

def runImageTransfer(config, checkpoint, input_folder, a2b):
    #erase_static_folder()
    output_path = 'static'
    seed = 1
    num_style = 10
    output_only = True
    num_of_images_to_test = 10000
    data_name = 'out'

    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    print(input_folder)
    # Load experiment setting
    config = get_config(config)
    input_dim = config['input_dim_a'] if a2b else config['input_dim_b']
    council_size = config['council']['council_size']


    # Setup model and data loader
    image_names = ImageFolder(input_folder, transform=None, return_paths=True)
    if not 'new_size_a' in config.keys():
        config['new_size_a'] = config['new_size']
    is_data_A = a2b
    data_loader = get_data_loader_folder(input_folder, 1, False,\
                                        new_size=config['new_size_a'] if 'new_size_a' in config.keys() else config['new_size'],\
                                        crop=False, config=config, is_data_A=is_data_A)

    print("data_loader : ",data_loader, " image_names : ", image_names)
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

    encode_s = []
    decode_s = []
    if a2b:
        for i in range(council_size):
            encode_s.append(trainer.gen_a2b_s[i].encode)  # encode function
            decode_s.append(trainer.gen_a2b_s[i].decode)  # decode function
    else:
        for i in range(council_size):
            encode_s.append(trainer.gen_b2a_s[i].encode)  # encode function
            decode_s.append(trainer.gen_b2a_s[i].decode)  # decode function


    # creat testing images
    file_list= []
    user_id = str(uuid.uuid4())
    seed = 1
    curr_image_num = -1
    for i, (images, names) in tqdm(enumerate(zip(data_loader, image_names)), total=num_of_images_to_test):
        #print(i)
        #print(images, names)
        if curr_image_num == num_of_images_to_test:
            break
        curr_image_num += 1
        k = np.random.randint(council_size)
        style_fixed = Variable(torch.randn(10, style_dim, 1, 1).cuda(), volatile=True)
        print(names[1])
        images = Variable(images.cuda(), volatile=True)

        content, _ = encode_s[k](images)
        seed += 1
        torch.random.manual_seed(seed)
        style = Variable(torch.randn(10, style_dim, 1, 1).cuda(), volatile=True)
        
        
        for j in range(10):
            s = style[j].unsqueeze(0)
            outputs = decode_s[k](content, s, images)
            basename = os.path.basename(names[1])
            #output_folder = outputs/council_glasses_removal_128
            output_folder = os.path.join(output_path, 'img')
                
                
            #path = os.path.join(output_folder, checkpoint[-8:] + "_%02d" % j, user_id + '_out_' + str(curr_image_num) + '_' + str(j) + '.jpg')
            path_all_in_one = os.path.join(output_folder, user_id , '_out_' + str(curr_image_num) + '_' + str(j) + '.jpg')
            file_list.append(path_all_in_one)
            print("path_all_in_one = " , path_all_in_one)
            do_all_in_one = True
            if do_all_in_one:
                if not os.path.exists(os.path.dirname(path_all_in_one)):
                    print("haha start working")
                    print(path_all_in_one)
                    os.makedirs(os.path.dirname(path_all_in_one))
            vutils.save_image(outputs.data, path_all_in_one, padding=0, normalize=True)
    '''
    if input_folder == '/home/user/upload/person2anime':
        set_image_determination(0)
    elif input_folder == '/home/user/upload/male2female':
        set_image_determination(1)
    else: set_image_determination(2)
    eraseUploadImage()
    '''
    print(file_list)
    #print(path_all_in_one)
    return file_list