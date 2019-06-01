# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import os,shutil
import numpy as np 
import json 
import collections
import time
# import tensorflow as tf
import argparse
import sys
import face_model
import cv2
from annoy import AnnoyIndex
import datetime
import random

SERVER_DIR_KEYS = ['/opt/images/test/test']
SERARCH_TMP_DIR = '/opt/images/searchImg'

app = Flask(__name__)

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(JsonEncoder, self).default(obj)

# 计算两个特征之间的相似度
def dot(source_feature, target_feature):
    simlist = []
    length = len(target_feature)
    for i in range(length):
      sim = np.dot(source_feature, np.expand_dims(target_feature[i], axis=0).T)
      if sim[0][0] < 0:
        sim[0][0] = 0
      simlist.append(sim[0][0])
    return simlist

@app.route("/")
def homePage():
    success = 0
    json_result = collections.OrderedDict()
    json_result["success"] = success
    return json.dumps(json_result)

# 人脸入库接口
# 接口返回说明 success表示http请求的状态（0表示成功，1表示失败），status表示人脸入库的状态，added表示入库成功,addFailed表示入库失败
# {
#   "success": 0, 
#   "status ": "added"
# }
@app.route("/addFace", methods=['POST'])
def addFace():

    success = 0
    status = "added"
    json_result = collections.OrderedDict()

    file = request.files.get('image')
    if file is None:
        status = "badrRequest"
        json_result["success"] = success
        json_result["status "] = status
        return json.dumps(json_result) 

    filename = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))+str(random.randint(0,100))+'.jpg'
    # 写死保存目录，需修改
    filepath = os.path.join('/opt/images/test','test',filename)
    print('addFace file save path: ',filepath)
    file.save(filepath)

    try:
        #生成特征编码
        image = cv2.imread(filepath,cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

        face_img = model.get_aligned_face(image)
        if face_img is None:
            status = "noFace"
        else:
            feature = model.get_feature(face_img)

            #特征编码入库
            feature_list.append(feature)
            print('feature_list length: ',len(feature_list))
            #特征编码索引
            feature = feature.tolist()[0]
            print(index)
            index.add_item(get_i(),feature)
            add_i()
            print(index)
            #图片数据入库
            image_list.append(filepath)
            print('image_list length: ',len(image_list))
    except Exception as e:
        print("catch error : ",str(e))
        status = "addFailed"
        success = 1

    json_result["success"] = success
    json_result["status "] = status

    return json.dumps(json_result,cls=JsonEncoder) 

#人脸搜索请求
@app.route("/faceIdentity", methods=['POST'])
def identity():

    success = 0
    status = "identited"
    json_result = collections.OrderedDict()

    # 用于保存相似分数以及相似度
    sim_image = []
    sim = []
    
    print('feature_list length: ',len(feature_list))
    print('image_list length: ',len(image_list))

    file = request.files.get('image')
    if file is None:
        status = "badrRequest"
        json_result["success"] = success
        json_result["status "] = status
        return json.dumps(json_result) 
    
    # 写死保存目录，需修改
    filename = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))+str(random.randint(0,100))+'.jpg'
    filepath = os.path.join(SERARCH_TMP_DIR,filename)
    print('searchFace file save path: ',filepath)
    file.save(filepath)

     # 生成上传图片的特征编码
    image = cv2.imread(filepath, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # try:
    face_img = model.get_aligned_face(image)
    print("get face_img")
    if face_img is None:
        status = "noFace"
    else:
        feature = model.get_feature(face_img)
        print("get 111")
        source_feature = feature
        feature = feature.tolist()[0]

        print("get 312313")
        # 找出最近的6个特征
        # 10个查找树
        index.build(10) 
        print(index)
        I = index.get_nns_by_vector(feature,3)
        print('I',I)
        # 计算相似度
        target_feature = np.squeeze(np.array(feature_list)[I],1)
        print('I',I)
        sim = dot(source_feature,target_feature)
        _sim_image = np.array(image_list)[I].tolist()

        for image in _sim_image:
            for key in SERVER_DIR_KEYS:
                if key in image:
                    sim_image.append(args.file_server + key + image.split(key)[1])
        json_result["sim_image"] = sim_image
        json_result["sim"] = sim

    # except Exception as e:
    #     print(str(e))
    #     success = 1
    json_result["success"] = success
    return json.dumps(json_result,cls=JsonEncoder)


def add_i():
    global i 
    i += 1

def get_i():
    global i 
    return i

def paresulte_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-size', default='112,112', help='')
    parser.add_argument('--model', default='/Users/liuxiaoying/workplace/CV_Code/insightface/models/model,00', help='path to load model.')
    parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
    parser.add_argument('--file_server_image_dir', type=str,help='Base dir to the face image.', default='/opt/images')
    parser.add_argument('--file_server', type=str,help='the file server address', default='http://localhost:8082')
    parser.add_argument('--port', default=5001, type=int, help='api port')
    return parser.parse_args(argv)


args = paresulte_arguments('')
# 特征编码有512维度
index = AnnoyIndex(512)
model = face_model.FaceModel(args)
feature_list = []
image_list = [] 
i = 0

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = args.port, threaded=True)

