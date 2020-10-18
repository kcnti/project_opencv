import cv2
import mysql.connector
import numpy
from PIL import Image, ImageFile
import os
from db.database import insert, queryDB, _fname, _lname, _gate, _terminal, _seat
from imutils.video import FPS
import imutils
id = 0

def draw(img, cascade, scaleFactor, minNeighbors, color, clf):
    global id
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    features = face.detectMultiScale(gray, scaleFactor, minNeighbors)
    treshold = 70
    for x,y,w,h in features:
        #cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
        id, con = clf.predict(gray[y:y+h,x:x+h])
        #print(type(id))
        #print(id-1)
        if con <= treshold:
            cv2.rectangle(img, (415, 0), (640, 44), (243, 107, 147), -1)
            cv2.rectangle(img, (415, 45), (640, 205), (230, 154, 185), -1)
            cv2.putText(img, "BOARDING GUIDE", (425,30), cv2.FONT_ITALIC, 0.7, color, 2)
            cv2.putText(img, f"{_fname[id-1]} {_lname[id-1]}",
                        (420,70),
                        cv2.FONT_ITALIC,
                        0.5, color, 2)
            cv2.putText(img, f"Gate: {_gate[id-1]}",
                        (420,110),
                        cv2.FONT_ITALIC,
                        0.5, color, 2)
            cv2.putText(img, f"Terminal: {_terminal[id-1]}",
                        (420,150),
                        cv2.FONT_ITALIC,
                        0.5, color, 2)
            cv2.putText(img, f"Seat: {_seat[id-1]}",
                        (420,190),
                        cv2.FONT_ITALIC,
                        0.5, color, 2)
            #print(f"Name: {_fname[id-1]} Lastname: {_lname[id-1]} Gate: {_gate[id-1]}")
            #print(id, _gate[id-1])
            #print(_gate)
        else:
            id = 1
        #    cv2.putText(img, "Unknown",(400,30), cv2.FONT_ITALIC, 0.8, color, 2)
    return img

def detect(frame, cascade, clf):
   frame = draw(frame, cascade, 1.1, 10, (255,255,255), clf)
   return frame

#draw face
def draw_boundary(img,classifier,scaleFactor,minNeighbors,color,text):
    cvtgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    feature = classifier.detectMultiScale(cvtgray,scaleFactor,minNeighbors) 
    scale = []
    for (x,y,w,h) in feature:
        cv2.rectangle(img,(x,y),(x+w,y+h),color,1)
        cv2.putText(img,text,(x,y-4),cv2.FONT_HERSHEY_TRIPLEX,0.8,color,2)
        scale = [x,y,w,h]
    return img,scale

#function save
def create_modelpicture(pic,id,pic_no):
    cv2.imwrite('.\data\pic.'+str(id)+'.'+str(pic_no)+'.jpg',pic)

#train data
def train_classifier(data_dir):
    path = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]
    face = [] #store face
    ids = [] #id of pic
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    for image in path:
        img = Image.open(image).convert("L") #convert to grayscale from pil
        imagenp = numpy.array(img,'uint8') #save img in imagenp by array
        id = int(os.path.split(image)[1].split('.')[1]) #create id for check that img alrdy train
        face.append(imagenp) #append to face list
        ids.append(id) #id > ids
    ids = numpy.array(ids)
    clf = cv2.face.LBPHFaceRecognizer_create() #remember face
    clf.train(face,ids)
    clf.write("./xml/x.xml")

def openCam():
    cap = cv2.VideoCapture(1)
    while cap.isOpened():
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("just test", gray)
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

#show usage
def usage():
    print("""How to use....
                [U]sage         : Enter U to show this message
                [D]ata          : Enter D to show data in database
                [I]ntertData    : Enter I to insert data to database
                [C]reateDataset : Enter C to capture your face into dataset
                [T]rainData     : Enter T Train data to .xml
                [S]tart         : Enter S to Start""")
def main():
    global id
    global face
    try:
        queryDB()
        face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        fps = FPS().start()
        pic_no = 0
        while True:
            choice = input("[U]sage, [D]ata, [I]nsertData To DB, [C]reateDataset, [T]rainDataset, [S]tart : ")
            if choice in ["U","u"]:
                usage()
            elif choice in ["d","D"]:
                index = len(_fname)
                for i in _fname:
                    print(i, end=', ')
                print(f'\n{index} indexes\n')
            elif choice in ["I","i"]:
                insert()
            elif choice in ["C","c"]:
                id = input("Enter id: ")
                while True:
                    ret,frame = cap.read()
                    frame = imutils.resize(frame)
                    if ret:
                        frame, scale = draw_boundary(frame, face, 1.1, 10, (0,0,255), 'face')
                        if len(scale) == 4:
                    #          id = 1
                            pic_crop = frame[scale[1]:scale[1]+scale[3],scale[0]:scale[0]+scale[2]]
                                    #    y         (y+h)             x          (x+w)
                            create_modelpicture(pic_crop,id,pic_no)
                        pic_no += 1
                        cv2.imshow('Creating Dataset', frame)
                        print(f"id : {id}, no: {pic_no}")
                        if(cv2.waitKey(1) & 0xFF == ord('q')):
                            break
            elif choice in ["T","t"]:
                path = input("Path to dataset: ")
                if os.path.exists(path) != True:
                    print("Enter the exist path!")
                else:
                    train_classifier(path)
                    print("Train Successfully")
            elif choice in ["S","s"]:
                clf = cv2.face.LBPHFaceRecognizer_create()
                clf.read("./xml/x.xml")
                while True:
                    ret,frame = cap.read()
                    frame = imutils.resize(frame)
                    if ret:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        features = face.detectMultiScale(gray, 1.1, 10)
                        treshold = 70
                        frame = detect(frame, face, clf)
                        qrcode_pic = cv2.imread("qr.png")
                        #print(id)
                        gate_pic = cv2.imread(f"./gate/gate_{_gate[id-1]}.png")
                        gate_pic = cv2.resize(gate_pic, (160,160))
                        #frame1 = cv2.addWeighted(qrcode_pic[0:100,0:100],1, frame[0:100,0:100,:], 1, 0)
                        qrcode_pic = cv2.resize(qrcode_pic, (100,100))
                        qr_x_offset, qr_y_offset = 10,10
                        gate_x_offset, gate_y_offset = 0,200
                        frame[qr_y_offset:qr_y_offset+qrcode_pic.shape[0], qr_x_offset:qr_x_offset+qrcode_pic.shape[1]] = qrcode_pic
                        frame[gate_y_offset:gate_y_offset+gate_pic.shape[0], gate_x_offset:gate_x_offset+gate_pic.shape[1]] = gate_pic
                        cv2.imshow('Real', frame)
                        if (cv2.waitKey(1) & 0xFF == ord('q')):
                            break
            else:
                print("Enter the correct one!")
            #cap.release()
            cv2.destroyAllWindows()
    except KeyboardInterrupt:
        print("\nExit!")

if '__main__' == __name__:
    main()