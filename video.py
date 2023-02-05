import cv2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import os
import argparse
import json
from confluent_kafka import Producer

parser = argparse.ArgumentParser()
parser.add_argument('--inputs', required=True, type = str,  
                    help="Path to inputs")
parser.add_argument('--meeting_id', type=str, 
                    help="Path to meeting_id")

args = parser.parse_args()

TOPIC_NAME = ""
KAFKA_TOPIC_IP = ""
# TOPIC_NAME = os.environ["kafka_topic"]
# KAFKA_TOPIC_IP = os.environ["kafka_ip"]
if len(KAFKA_TOPIC_IP.strip())<1:
    SEND_KAFKA=False
else:
    SEND_KAFKA=True

prototxtPath = ('face_detector/deploy.prototxt')
weightsPath = ('face_detector/res10_300x300_ssd_iter_140000.caffemodel')
net = cv2.dnn.readNet(prototxtPath, weightsPath)
model = load_model('results/Xception-size-64-bs-32-lr-0.0001.h5')

if SEND_KAFKA:
    topic = TOPIC_NAME

    producer = Producer({
        #config.KAFKA_SERVER: config.KAFKA_TOPIC_IP
        'bootstrap.servers':KAFKA_TOPIC_IP
    })

    delivered_records = 0

    def acked(err, msg):
        global delivered_records

        if err is not None:
            print("Failed to deliver message: {}".format(err))
        else:
            delivered_records += 1
cap = cv2.VideoCapture(args.inputs)
if cap.isOpened():
    c = 0
    while(True):
        ret, frame = cap.read()
        frame = cv2.resize(frame,(720,720))
        if not ret:
            break
        if cv2.waitKey(1) & 0xFF== ord('q'):
            break
        
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0, mean=(104.0, 177.0, 123.0))


        net.setInput(blob)
        detections = net.forward()
        cv2.imshow("frame",frame)

        a = frame.shape[0]
        b = frame.shape[1]
        # count = 0
        pers = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence < 0.5:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))
    
            if startX < b and endX < b:
                if startY < a and  endY < a:
                    # count+=1

                    try:
                        face = frame[startY:endY, startX:endX]
                        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                        face = cv2.resize(face, (64, 64))
                        face = img_to_array(face)
                        face = preprocess_input(face)
                        face = np.expand_dims(face, axis=0)
                        

                        mask = model.predict(face)[0]

                        label = "Mask" if mask < 0.5 else "No Mask"
                        pers.append(label)
                        l = list(enumerate(pers,1))
                        

                        # color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                    except Exception as e:
                        print(e)
            # display the label and bounding box rectangle on the output frame
        c+=1
        

        d = {'meeting_id':args.meeting_id, 'person':l, 'frame_no':c}

        json_obj = json.dumps(d)
        print(json_obj)



        if SEND_KAFKA:
            record_value = json.dumps(json_obj)
            print("Producing record: {}".format(record_value))
            producer.produce(topic,value=record_value, on_delivery=acked)
            producer.poll(0)


else:
    print("capture not found")



    if SEND_KAFKA:
        producer.flush()