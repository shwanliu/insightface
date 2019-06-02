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
import io

# 特征入库操作 数据库
from flaskext.mysql import MySQL


SERVER_DIR_KEYS = ['/home/shawnliu/workPlace/Face_server/images/test/test/']
SERARCH_TMP_DIR = '/home/shawnliu/workPlace/Face_server/images/searchImg'

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1'
app.config['MYSQL_DATABASE_DB'] = 'faceFeatureData'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#用于连接对话，执行完增删改的操作记得要执行commit.commit
connect = mysql.connect()
cursor = connect.cursor()

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


# /  
@app.route("/")
def homePage():
    success = 0
    json_result = collections.OrderedDict()
    cursor.execute("SELECT * from FaceFeature ")
    data = cursor.fetchall()
    json_result["success"] = success
    return json.dumps(json_result)

# 人脸数据库的操作

# 获取人脸数据库的长度
@app.route("/getDbSize")
def getDbSize():
    success = 0
    json_result = collections.OrderedDict()
    try:
        cursor.execute("select count(*) from FaceFeature ")
        _len = cursor.fetchall()
        json_result["success"] = success
        print('The number of face in DB is: ',_len)
        json_result["length"] = _len
    except Exception as e:
        print("catch error : ",str(e))
        status = "addFailed"
        success = 1
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
    name = request.form.get('name')
    print(name)
    if file is None:
        status = "badrRequest"
        json_result["success"] = success
        json_result["status "] = status
        return json.dumps(json_result) 

    filename = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))+str(random.randint(0,100))+'.jpg'
    # 写死保存目录，需修改
    filepath = os.path.join('/home/shawnliu/workPlace/Face_server/images/test','test',filename)
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
            bytes_feature = feature.tostring()
            cursor.execute('insert into FaceFeature values(%s,%s,%s,%s)',(['',name,bytes_feature,filename])) 
            # 执行sql语句之后要记的commit，不然当前对话是不会成功的修改到数据库
            connect.commit()
            #特征编码入库,使用数据库之后就不用这一步了，直接从数据库里面获取
            # feature_list.append(feature)
            # print('feature_list length: ',len(feature_list))

            #特征编码索引
            # feature = feature.tolist()[0]
            # index.add_item(get_i(),feature)
            # add_i()

            #图片数据入库
            # image_list.append(filepath)
            # print('image_list length: ',len(image_list))

            # 用于保存annoy的model
            cursor.execute('select * from FaceFeature')
            data = cursor.fetchall()

            # 特征编码有512维度
            index = AnnoyIndex(512)
            for faceId, faceName, feature, imgPath in data:
                dBFeature = np.frombuffer(feature,dtype=np.float32)
                # 特征编码索引
                _dBFeature=dBFeature.tolist()
                index.add_item(get_i(),_dBFeature)
                add_i()
            index.build(512)
            index.save('faceModel.ann') 

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

    file = request.files.get('image')
    if file is None:
        status = "badrRequest"
        json_result["success"] = success
        json_result["status "] = status
        return json.dumps(json_result) 
    
    # 写死保存目录，需修改
    filename = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))+str(random.randint(0,100))+'.jpg'
    filepath = os.path.join(SERARCH_TMP_DIR,filename)
    file.save(filepath)

     # 生成上传图片的特征编码
    image = cv2.imread(filepath, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    try:
        face_img = model.get_aligned_face(image)
        if face_img is None:
            status = "noFace"
        else:
            cursor.execute('select * from FaceFeature')
            data = cursor.fetchall()

            # 从数据库读取数据的地方，获取入库的人脸信息
            # faceId    人员ID（系统生成,唯一）
            # faceName  人员名称
            # feature   提取的特征
            # imgPath   入库图片的名称，用于返回识别结果的库的人脸

            feature_list = []
            image_list = []
            faceInfo=[]
        
            for faceId, faceName, feature, imgPath in data:
                dBFeature = np.frombuffer(feature,dtype=np.float32)
                feature_list.append(dBFeature)
                image_list.append(imgPath)
                faceInfo.append({"faceId":faceId,"faceName":faceName,"imgPath ":imgPath})

                # 特征编码索引
                # _dBFeature=dBFeature.tolist()
                # index.add_item(faceId,_dBFeature)
                # add_i()

            print(faceInfo[0])
            print('image_list length: ',len(image_list))
            print('feature_list length: ',len(feature_list))

            feature = model.get_feature(face_img)
            source_feature = feature
            feature = feature.tolist()[0]

            # 找出最近的6个特征
            # 10个查找树
            # index.build(512)
            # index.save('faceModel.ann') 
            u = AnnoyIndex(512)
            u.load('faceModel.ann')
            I = u.get_nns_by_vector(feature,3)

            print(I)
            # 根据annoy分析后得到的近似向量的下标，取出相应的向量计算他们之间的相似度
            target_feature = np.array(feature_list)[I]

            sim = dot(source_feature,target_feature)

            for id, value in enumerate(sim):
                # 判断这个分数，如果小于设定的阈值，将它丢弃
                if value <= 0.7:
                    I.__delitem__(id)
                    sim.__delitem__(id)

            _sim_image = np.array(image_list)[I].tolist()

            for key in SERVER_DIR_KEYS:
                print(key)
                for _,_,files in os.walk(key):
                    for image in _sim_image:
                        if str(image) in files:
                            sim_image.append(args.file_server +'/'+key.split('images/')[1] + image)
            json_result["sim_image"] = sim_image
            json_result["sim"] = sim

    except Exception as e:
        print(str(e))
        success = 1
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
    parser.add_argument('--model', default='/home/shawnliu/workPlace/insightface/models/model,00', help='path to load model.')
    parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
    parser.add_argument('--file_server_image_dir', type=str,help='Base dir to the face image.', default='/home/shawnliu/workPlace/Face_server/images')
    parser.add_argument('--file_server', type=str,help='the file server address', default='http://192.168.1.157:8082')
    parser.add_argument('--port', default=5000, type=int, help='api port')
    parser.add_argument('--gpu', default=0, type=int, help='gpu devices')
    return parser.parse_args(argv)


args = paresulte_arguments('')
model = face_model.FaceModel(args)
i = 0

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = args.port, threaded=True)

