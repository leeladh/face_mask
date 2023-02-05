from fastapi import FastAPI
from pydantic import BaseModel
import os, sys
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MASK_DETECTION LIVE API", openapi_url="/face_mask/face_mask_detection/v1/openapi.json", docs_url="/face_mask_detection/docs")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class inputs_live(BaseModel):
    inputs:str
    meeting_id:str


class inputs_kill(BaseModel):
    meeting_id:str
       
         
@app.post('/mask_detection/live')
def show_data(data: inputs_live): 
    global saved_data 
    saved_data = data
    print(saved_data)
    print("++++++++++++++++++++")
    print("Executing Lipsync")
    print("+++++++++++++++++++")
    try:
        os.system('bash launch.sh '+saved_data.meeting_id+' '+saved_data.inputs)
        return {"Status": "Success"}
    except:
        return {"Status": "Failed"}

@app.post('/mask_detction/kill')
def kill_app(data: inputs_kill):

    print("++++++++++++++++++++")
    print("Killing Lipsync")
    print("+++++++++++++++++++")

    try:
        # os.system('pkill -f '+data.meeting_id)
        # pid = os.system('pgrep -f '+str(data.meeting_id))
        # os.system('pkill -9 -f '+str(data.meeting_id))
        os.system(f'python3 kill.py --meeting_id {data.meeting_id}')
        return {"Status": "Killed"}
    except:
        return {"Status": "Kill Failed"}