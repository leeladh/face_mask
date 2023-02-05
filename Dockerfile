FROM tensorflow/tensorflow:2.3.0
WORKDIR /work/mask_detection/
COPY . /work/mask_detection/

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install -r requirements.txt
RUN pip install fastapi confluent-kafka uvicorn[standard]

RUN ["chmod", "+x", "init.sh"]
EXPOSE 9096
ENTRYPOINT ["./init.sh", "9096"]