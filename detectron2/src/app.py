import sys
sys.path.append('../')
import cv2
from typing import Optional
from fastapi import FastAPI, Depends
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Required, BaseModel, Field
import torch
from models.detector import *
import gc
import uvicorn
import cv2
from websockets.exceptions import ConnectionClosedError
from database import connect
from utils import *
torch.backends.cudnn.benchmark = True




# camera = Camera(0)
# camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# camera = Camera('http://192.168.8.109:8080/video')
# camera = Camera('rtsp://user:user@192.168.8.107/live/ch00_0')
detector = Detector(model_type='PS')
templates = Jinja2Templates(directory="templates")

# Assign an instance of the FastAPI class to the variable "app".
# You will interact with your api using this instance.
app = FastAPI(title='Deploying a ML Model with FastAPI')

# CORS setup
origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# RUNNING THE DATABASE CONNECTION INSTANCE HERE

client = connect()

if client is not None:
    db = client["segmentation"]

    # CONNECTING TO USER COLLECTION
    users_collection = db["Users"]
    # posted_user = users_collection.insert_one(user)
else:
    print('Connection to database not extablish!, restart you Network')

# BASE MODELS

class User(BaseModel):
    name: str
    email: str
    password: str
    camera_choice: Optional[str]

    @classmethod
    def load_from_db(cls, user_model):
        return cls(name= user_model.name, email=user_model.email, password = user_model.password, camera_choice= user_model.camera_choice)

class Login(BaseModel):
    email: str
    password: str

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("segments.html", {"request": request})


@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    # print(token)
    # data = 
    # camera = Camera(0)
    try:
        await websocket.accept()
        token = await websocket.receive_text()
        decoded_data = Login.parse_raw(decode_token(token)['sub']).dict()
        users_data = users_collection.find_one({'email': decoded_data.get("email")})

        choice = users_data.get("camera_choice")
        if choice == 'webcam':
            camera = Camera(0)
        if choice == 'external':
            url = users_data.get("camera_url")
            # print(url)
            camera = Camera(url)


        del choice, users_data, decoded_data, token
    except NameError:
        print('Connection to database not extablish!, restart you Network')
  
    # user = User.load_from_db(users_data)
    
    # print(token)
    try:
        while True:
            frame = camera.getFrame()
            if frame is not None:
                resized_img  =  cv2.resize(frame, (600, 400), interpolation = cv2.INTER_NEAREST) 
                result = await detector.test(resized_img)
        
                ret, buffer = cv2.imencode('.jpg', result)
                await websocket.send_bytes(buffer.tobytes())

                del frame, result
                gc.collect()
                torch.cuda.empty_cache() 
            else:
                print('No frame is rendered') 
                pass 

    except (WebSocketDisconnect,ConnectionClosedError):
        print("Client disconnected") 
        del camera

#############   User Authetication ####################         



@app.post("/register")
async def register(user: User):
    user = jsonable_encoder(user)
    try:
        found_user = users_collection.find_one({"email": user["email"]})
        print(found_user)
        if found_user:
            return {
            "message": "Email already registered",
            "status": "failure"
        }
        user["password"] = get_hashed_password(user["password"])
        user['camera_choice'] = 'webcam'
        user_model = User.parse_obj(user)
        users_collection.insert_one(user)
        return {
            "message": "User Registration Successful",
            "user" : user_model.json(),
            "status": "success",
        }
    except: 
        return {
            "message": "Unable to Register User",
            "status": "failure"
        }


@app.post("/login")
async def login(loginPayload : Login):
    try:
        user = jsonable_encoder(loginPayload)
        found_user = users_collection.find_one({"email":user['email']})
        # print(found_user._id)
        if found_user == None:
            return {
            "message": "User not found",
            "status": "failure"
        }
        if verify_password(user["password"], found_user["password"]) == False: 
            return {
            "message": "Incorrect Password",
            "status": "failure"
        }

        access_token = create_access_token(loginPayload.json())

        return {
            "message": "Login Successful",
            "status": "success",
            "access_token": access_token,
            "data": str(found_user)
        }
    except NameError:
        print('Connection to database not extablish!, restart you Network')


########## Generate Camera Address #############

class Address(BaseModel):
    camera_id: Union[str, int] = 0 

class CameraChoice(BaseModel):
    choice: str

@app.post("/camera")
async def choice(camera_choice: CameraChoice, token: str = Depends(oauth2_scheme)):
    decoded_data = Login.parse_raw(decode_token(token)['sub']).dict()
    if camera_choice.choice != "webcam" and camera_choice.choice != "external":
        return {
            'message': "Camera Choice not Supported",
            'status': 'failure'
        }
    
    users_collection.update_one({'email': decoded_data.get("email")}, { "$set": { "camera_choice": camera_choice.choice } })
    return {
        'message': 'Choice Noted',
        'status': 'success'
    }

@app.post("/camera_id")
async def camera(address: Address, token: str = Depends(oauth2_scheme)):
    decoded_data = Login.parse_raw(decode_token(token)['sub']).dict()
    webcam = address.camera_id.isnumeric() or address.camera_id.endswith('.txt') or address.camera_id.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))
    
    # print(decoded_data.get("email"))
    # array = ast.literal_eval(decoded_data)
    # print('---------------------------')
    # print(array.keys())
    # updated_data = users_collection.update_one({"email": })
    if webcam:
        updated_data = users_collection.update_one({'email': decoded_data.get("email")}, { "$set": { "camera_url": address.camera_id } })
        print(updated_data)
        return address
    else:
        return {
           'message': "Incorrect Camera Address",
           'status': address.camera_id,
           "expect_input":  "The camera address should be (0, 1) or startwith ('rtsp://', 'rtmp://', 'http://', 'https://')"
            
        }


@app.get("/test")
async def test(token: str = Depends(oauth2_scheme)):
    # print(decode_token(token)['sub'])
    return {
        "message": "Decoded"
    }
    

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)