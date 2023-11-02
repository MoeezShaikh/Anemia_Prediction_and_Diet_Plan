from datetime import datetime
from flask import Flask, render_template,request,json,redirect 
import mysql.connector                          
from collections.abc import Mapping
from sqlalchemy import true 
from flask   import session
import face_recognition
import cv2 
import bcrypt
import bson.binary 
import base64
from io import BytesIO
import numpy as np
import pandas as pd
from base64 import b64encode
from datetime import datetime
import os
from PIL import Image 
from flask_mail import Mail 
import csv
import xlsxwriter
import openpyxl

app = Flask(__name__)
app.secret_key = 'hello how are you'

#db connection
conn= mysql.connector.connect(host="localhost",user="root",port="3307",password="",database="anemia_detection")


#Sending Email
with open('config.json','r') as c:
    params = json.load(c)["params"]
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail'],
    MAIL_PASSWORD = params['password']
)   # for mail
mail = Mail(app) 

@app.route("/")
def main():
    return render_template('index.html')
  

@app.route('/signup')
def Showsignup():
    return render_template('signup.html')

@app.route('/api/signup',methods=['POST'])
def signUp():
    try:
        username = request.form['inputName']
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        pic=request.files['photo'] 
        # read the image data
        img_data = pic.read()
        # create a binary object from the image data
        img_binary = bytes(img_data)
            # create a numpy array from the image data
        nparr = np.frombuffer(img_data, np.uint8)
        # decode numpy array as image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
        # detect faces in the image
        face_locations = face_recognition.face_locations(img)
        # detect faces in the image
        face_locations = []
        if len(img) > 0:
            face_locations = face_recognition.face_locations(img)
        # check if exactly one face was detected
        if len(face_locations) == 1:                                
                # get the face encoding
                face_encoding = face_recognition.face_encodings(img, face_locations)[0]

                 # create a binary object from the face encoding
                face_encoding_binary = bytes(face_encoding.tobytes()) 

                print(pic)
                if not pic:
                    return 'No pic uploaded!', 400
                filename = pic.filename
                mimetype = pic.mimetype
                if not filename or not mimetype:
                    return 'Bad upload!', 400
                print("pic",pic)

                selectquery = "select * from user where username ='%s' "%username
                cursor=conn.cursor()
                cursor.execute(selectquery)
                data = cursor.fetchall()
                if len(data)== 0:
                    conn.commit()
                    insertquery = "INSERT INTO user (id, username, password, email,filename, img_binary, face_encoding_binary) VALUES (null, %s, %s, %s, %s, %s, %s)"
                    values = (username, password, email, filename, img_binary,face_encoding_binary)
                    cursor.execute(insertquery, values)
                    conn.commit()
                    cursor.close() 
                    return render_template('signup.html')
            
                else:
                    return json.dumps({'error': str(data[0])})
    except Exception as e:
        return json.dumps({'error':str(e)})  

        
@app.route('/signin')
def showSignin():
    return render_template('signin.html')


@app.route('/api/validateLogin',methods=['POST'])
def validateLogin():
    try:
        email = request.form['inputEmail']
        password = request.form['inputPassword']
 
     # connect to mysql
        print("before proce")
        cursor=conn.cursor()
        cursor.execute("select * from user where email ='%s' and password='%s'"%(email,password))
        print('after proc')
        data = cursor.fetchall()
        conn.commit()
        print(data)
        if len(data) > 0:
            session['userid'] = data[0][0]
            print('inside if')
            return  render_template('userhome.html',user=data)
            
        else:
            return render_template('error.html',error = 'Wrong Email address or Password')
 
    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/userHome')     
def userHome():
    if session.get('userid'):
        cursor = conn.cursor(buffered=true)
        username =str(session.get('userid'))
        selectquery="select username from user where username='%s'"%(username)
        print(selectquery)  
        cursor.execute(selectquery) 
        data= cursor.fetchall() 
        print(data)     
        cursor.close()  
        return render_template('userhome.html',username=data)
    else:
        return render_template('error.html',error = 'Unauthorized Access')



@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


if __name__ =='__main__':
    app.run(debug=True)    