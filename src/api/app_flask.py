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
from flask_cors import *
import cv2
from annoy import AnnoyIndex
import datetime
import random
import io

# 特征入库操作 数据库
from flaskext.mysql import MySQL


SERVER_DIR_KEYS = ['./images/test/test/']
SERARCH_TMP_DIR = './images/searchImg'

mysql = MySQL()
app = Flask(__name__)

CORS(app, resources=r'/*')
headers = {
    'Cache-Control' : 'no-cache, no-store, must-revalidate',
    'Pragma' : 'no-cache' ,
    'Expires': '0' ,
    'Access-Control-Allow-Origin' : '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token'
}

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1'
app.config['MYSQL_DATABASE_DB'] = 'AIMEET'
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

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)
 
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

# @app.route("/")
# def index():
#     return render_template('index.html')

#获取会议室房间的数量事件
@app.route("/getRoomNum")
def getRoomNum():
    success = 0
    json_result = collections.OrderedDict()
    cursor.execute("SELECT * from roomInfo ")
    data = cursor.fetchall()

    json_result["success"] = success
    json_result["roomNumber"] = len(data)
    return json.dumps(json_result)

#获取所有会议室的信息事件
@app.route("/getRoomInfo")
def getRoomInfo():
    success = 0
    json_result = collections.OrderedDict()
    cursor.execute("SELECT * from roomInfo ")
    data = cursor.fetchall()

    json_result["success"] = success
    json_result["room number"] = data
    return json.dumps(json_result)

#进行条件筛查,以及更新响应的userInfo单次预定的信息事件
@app.route("/previewRoom",methods=["POST"])
def previewRoom():
    success = 0
    json_result = collections.OrderedDict()
    data = request.get_json()      # 获取 JOSN 数据
    # account= request.json['account']     #  以字典形式获取参数
    print(data)
    user_id = request.json['user_id']
    att_nums = request.json['att_nums']
    s_time = request.json['s_time']
    e_time = request.json['e_time']
    # print(user_id,att_nums,s_time,e_time)
    # 首先更新对应的用户的userInfo表，因为每次都是不一样的人数以及时间，历史预定会议室的用户信息将不再保存
    sql = "update userinfo set att_nums=%s,s_time=%s,e_time=%s where userid = %s"
    cursor.execute(sql, (att_nums,s_time,e_time,user_id))
    connect.commit()

    # sql = "select room_id,s_time,e_time from used_room where s_time>%s or e_time<%s and room_id in (select room_id from roomInfo where att_nums >= %s)" #%int(att_nums)
    
    sql2 = "select * from roomInfo where room_id in (select room_id from roomInfo where att_nums >= %s or room_id in (select room_id from used_room where (s_time>%s or e_time<%s) and att_nums>=%s) order by roomInfo.att_nums)" #%int(att_nums)
    
    cursor.execute(sql2,(att_nums,e_time,s_time,att_nums))
    data = cursor.fetchall()
    json_result["success"] = success
    json_result["data"] = data
    # return json.dumps(json_result,cls=DateEncoder)
    return json.dumps(json_result)


#预约会议室事件事件
@app.route("/bookRoom",methods=["POST"])
def bookRoom():
    success = 200
    json_result = collections.OrderedDict()

    user_id = request.form.get('user_id')
    room_id = request.form.get('room_id')
    s_time = request.form.get('s_time')
    e_time = request.form.get('e_time')
    flag = request.form.get('flag')
    json_result = collections.OrderedDict()
    cursor.execute('insert into used_room values(%s,%s,%s,%s,%s,%s)',([0,user_id,room_id,s_time,e_time,1])) 
    connect.commit()
    json_result["success"] = success
    return json.dumps(json_result)

#获取人脸数据库的长度事件
@app.route("/getDbSize")
def getDbSize():
    success = 200
    json_result = collections.OrderedDict()
    try:
        cursor.execute("select count(*) from FaceFeature ")
        _len = cursor.fetchall()
        connect.close()
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

    success = 200
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
    filepath = os.path.join('./images/test','test',filename)
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
            cursor.execute('insert into FaceFeature values(%s,%s,%s,%s)',([0,name,bytes_feature,filename])) 
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

    success = 200
    status = "identited"
    json_result = collections.OrderedDict()

    # 用于保存相似分数以及相似度,以及人员姓名
    sim_image = []
    sim = []
    sim_name = []
    result=[]
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
            # feature   提取的特征 blob
            # imgPath   入库图片的名称，用于返回识别结果的库的人脸

            feature_list = []
            image_list = []
            faceInfo=[]
        
            for faceId, faceName, feature, imgPath in data:
                dBFeature = np.frombuffer(feature,dtype=np.float32)
                feature_list.append(dBFeature)
                image_list.append(imgPath)
                faceInfo.append({"faceId":faceId,"faceName":faceName,"imgPath":imgPath})

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
            _faceInfos = np.array(faceInfo)[I].tolist()

            for key in SERVER_DIR_KEYS:
                print(key)
                for _,_,files in os.walk(key):
                    for image in _sim_image:
                        if str(image) in files:
                            sim_image.append(args.file_server +'/'+key.split('images/')[1] + image)

                            
            for idx, info in enumerate(_faceInfos):
                result.append({'name':info['faceName'],'score':sim[idx],'imgPath':sim_image[idx]})
                sim_name.append(info['faceName'])

    except Exception as e:
        print(str(e))
        success = 1
    json_result["success"] = success

    return json.dumps(result,cls=JsonEncoder)


@app.route("/faceMeet", methods=['POST'])
def faceMeet():

    success = 200
    status = "identited"
    json_result = collections.OrderedDict()

    # 用于保存相似分数以及相似度,以及人员姓名
    sim_image = []
    sim = []
    sim_name = []

    file = request.json['image']

    print(len(file))

    # if file is None:
    #     status = "badrRequest"
    #     json_result["success"] = success
    #     json_result["status "] = status
    #     return json.dumps(json_result) 
    
    # # 写死保存目录，需修改
    # filename = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))+str(random.randint(0,100))+'.jpg'
    # filepath = os.path.join(SERARCH_TMP_DIR,filename)
    # file.save(filepath)

    #  # 生成上传图片的特征编码
    # image = cv2.imread(filepath, cv2.IMREAD_COLOR)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # try:
    #     face_img = model.get_aligned_face(image)
    #     if face_img is None:
    #         status = "noFace"
    #     else:
    #         cursor.execute('select * from FaceFeature')
    #         data = cursor.fetchall()

    #         # 从数据库读取数据的地方，获取入库的人脸信息
    #         # faceId    人员ID（系统生成,唯一）
    #         # faceName  人员名称
    #         # feature   提取的特征 blob
    #         # imgPath   入库图片的名称，用于返回识别结果的库的人脸

    #         feature_list = []
    #         image_list = []
    #         faceInfo=[]
        
    #         for faceId, faceName, feature, imgPath in data:
    #             dBFeature = np.frombuffer(feature,dtype=np.float32)
    #             feature_list.append(dBFeature)
    #             image_list.append(imgPath)
    #             faceInfo.append({"faceId":faceId,"faceName":faceName,"imgPath":imgPath})

    #             # 特征编码索引
    #             # _dBFeature=dBFeature.tolist()
    #             # index.add_item(faceId,_dBFeature)
    #             # add_i()

    #         print(faceInfo[0])
    #         print('image_list length: ',len(image_list))
    #         print('feature_list length: ',len(feature_list))

    #         feature = model.get_feature(face_img)
    #         source_feature = feature
    #         feature = feature.tolist()[0]

    #         # 找出最近的6个特征
    #         # 10个查找树
    #         # index.build(512)
    #         # index.save('faceModel.ann') 
    #         u = AnnoyIndex(512)
    #         u.load('faceModel.ann')
    #         I = u.get_nns_by_vector(feature,3)

    #         print(I)
    #         # 根据annoy分析后得到的近似向量的下标，取出相应的向量计算他们之间的相似度
    #         target_feature = np.array(feature_list)[I]

    #         sim = dot(source_feature,target_feature)

    #         for id, value in enumerate(sim):
    #             # 判断这个分数，如果小于设定的阈值，将它丢弃
    #             if value <= 0.7:
    #                 I.__delitem__(id)
    #                 sim.__delitem__(id)

    #         _sim_image = np.array(image_list)[I].tolist()
    #         _faceInfos = np.array(faceInfo)[I].tolist()

    #         for key in SERVER_DIR_KEYS:
    #             print(key)
    #             for _,_,files in os.walk(key):
    #                 for image in _sim_image:
    #                     if str(image) in files:
    #                         sim_image.append(args.file_server +'/'+key.split('images/')[1] + image)

    #         result=[]
    #         for idx, info in enumerate(_faceInfos):
    #             result.append({'name':info['faceName'],'score':sim[idx],'imgPath':sim_image[idx]})
    #             sim_name.append(info['faceName'])

    # except Exception as e:
    #     print(str(e))
    #     success = 1
    json_result["success"] = success

    return json.dumps(json_result,cls=JsonEncoder)

#人脸验证请求
# 上传两张人脸图片进行人脸比对
@app.route("/faceVerify", methods=['POST'])
def faceVerify():
    success = 0
    json_result = collections.OrderedDict()

    file1 = request.files.get('image1')
    file2 = request.files.get('image2')
    if file1 is None or file2 is None:
        status = "badrRequest"
        json_result["success"] = success
        json_result["status "] = status
        return json.dumps(json_result) 
    
    # 写死保存目录，需修改
    filename1 = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))+str(random.randint(0,100))+'_1_'+'.jpg'
    filepath1 = os.path.join(SERARCH_TMP_DIR,filename1)
    file1.save(filepath1)

    filename2 = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))+str(random.randint(0,100))+'_2_.'+'jpg'
    filepath2 = os.path.join(SERARCH_TMP_DIR,filename2)
    file2.save(filepath2)

    # 生成两张上传图片的特征编码
    image1 = cv2.imread(filepath1, cv2.IMREAD_COLOR)
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)

    image2 = cv2.imread(filepath2, cv2.IMREAD_COLOR)
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)

    try:
        face_img1 = model.get_aligned_face(image1)
        face_img2 = model.get_aligned_face(image2)
        if face_img1 is None or face_img2 is None :
            status = "img1 or img2 noFace"
        else:
            feature1 = model.get_feature(face_img1)
            feature2 = model.get_feature(face_img2)

            # 计算两个人脸图的相似度
            sim = dot(feature1,feature2)
            print(sim[0]*100)

    except Exception as e:
        print(str(e))
        success = 1

    json_result["confidence"] = sim[0]*100
    return json.dumps(json_result,cls=JsonEncoder)

def add_i():
    global i 
    i += 1

def get_i():
    global i 
    return i

# def paresulte_arguments(argv):
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--image-size', default='112,112', help='')
#     parser.add_argument('--model', default='/home/shawnliu/workPlace/insightface/models/model,00', help='path to load model.')
#     parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
#     parser.add_argument('--file_server_image_dir', type=str,help='Base dir to the face image.', default='/home/shawnliu/workPlace/Face_server/images')
#     parser.add_argument('--file_server', type=str,help='the file server address', default='http://192.168.1.157:8082')
#     parser.add_argument('--port', default=5000, type=int, help='api port')
#     parser.add_argument('--gpu', default=0, type=int, help='gpu devices')
#     return parser.parse_args(argv)

def paresulte_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-size', default='112,112', help='')
    parser.add_argument('--model', default='../../models/model,00', help='path to load model.')
    parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
    parser.add_argument('--file_server_image_dir', type=str,help='Base dir to the face image.', default='/opt/images')
    parser.add_argument('--file_server', type=str,help='the file server address', default='http://localhost:8082')
    parser.add_argument('--port', default=5001, type=int, help='api port')
    return parser.parse_args(argv)


args = paresulte_arguments('')
model = face_model.FaceModel(args)
i = 0

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = args.port, threaded=True)

