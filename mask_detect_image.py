# USAGE
# python mask_detect_image.py --image demo_image/1.jpeg

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import cv2
import os


def mask_image():
    # construct the argument parser and parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True, 
                        help="Path to input image")
    parser.add_argument("-f", "--face", type=str, default="face_detector", 
                        help="Path to face detector model directory")
    parser.add_argument("-m", "--model", type=str, default="mask_detector.model", 
                        help="Path to trained face mask detector model")
    parser.add_argument('-s', '--size', type=int, default=64, 
                        help="Size of face image")
    parser.add_argument("-c", "--confidence", type=float, default=0.5, 
                        help="Minimum probability to filter weak detections")
    args = parser.parse_args()

    # load our serialized face detector model from disk
    prototxtPath = os.path.sep.join([args.face, "deploy.prototxt"])
    weightsPath = os.path.sep.join([args.face, "res10_300x300_ssd_iter_140000.caffemodel"])
    net = cv2.dnn.readNet(prototxtPath, weightsPath)

    # load the face mask detector model from disk
    model = load_model(args.model)

    image = cv2.imread(args.image)
    if image is None:
        print('Can not read file: %s' % args.image)
        return

    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, mean=(104.0, 177.0, 123.0))

    net.setInput(blob)
    detections = net.forward()

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence < args.confidence:
            # Drop low confidence detections
            continue

        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        (startX, startY) = (max(0, startX), max(0, startY))
        (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

        try:
            face = image[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (args.size, args.size))
            face = img_to_array(face)
            face = preprocess_input(face)
            face = np.expand_dims(face, axis=0)
            

            mask = model.predict(face)[0]

            label = "Mask" if mask < 0.5 else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
            # display the label and bounding box rectangle on the output frame
            cv2.putText(image, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
            cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)
        except Exception as e:
            print(e)


    # show the output image
    cv2.imshow("Output", image)
    cv2.waitKey(0)

if __name__ == "__main__":
    mask_image()
