from   detectron2.engine.defaults import DefaultPredictor
from   detectron2.config import get_cfg
from   detectron2.data import MetadataCatalog
from   detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2.model_zoo import model_zoo
import threading
from threading import Lock
import time

##read images
import cv2

class Detector():
    def __init__(self, model_type:str='PS'):
        self.cfg = get_cfg()
        self.model_type = model_type
        # self.cfg.MODEL_ROI_HEADS.SCORE_THRESH_TEST = 0.5
        # self.class_list  = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter',
        #                     'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'umbrella', 'handbag', 'suitcase', 
        #                     'bottle', 'chair', 'couch', 'tv',  'cell phone', 'things', 'bridge', 'flower', 'fruit', 'gravel', 'house', 'light', 'net', 'playingfield', 'railroad', 'river', 
        #                     'road', 'roof', 'sand', 'sea', 'snow',  'water', 'window', 'tree', 'fence', 'sky', 'table', 'floor', 'pavement', 'mountain', 'grass', 'dirt',
        #                     'paper', 'food', 'building', 'rock', 'wall']

        #Load Model config and pretrained model
        if model_type == 'OD':
            self.cfg.merge_from_file(model_zoo.get_config_file('COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml'))
            self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url('COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml')
        elif model_type == 'IS': #Instance segmentation
            self.cfg.merge_from_file(model_zoo.get_config_file('COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml'))
            self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url('COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml')
    
        elif model_type == 'PS': #Panoptic segmentation
            self.cfg.merge_from_file(model_zoo.get_config_file('COCO-PanopticSegmentation/panoptic_fpn_R_50_3x.yaml'))
            self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url('COCO-PanopticSegmentation/panoptic_fpn_R_50_3x.yaml')

        self.cfg.INPUT.MIN_SIZE_TEST = 0
        self.cfg.INPUT.MAX_SIZE_TEST = 0
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
        self.cfg.MODEL.DEVICE = "cuda"
        self.predictor = DefaultPredictor(self.cfg)

    async def test(self,frame):
        if self.model_type != 'PS':

            predictions = self.predictor(frame)
            viz = Visualizer(frame[:, :, ::-1], metadata = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]),scale=1.2, instance_mode = ColorMode.IMAGE_BW )
            output = viz.draw_instance_predictions(predictions["instances"].to("cpu"))
            result = output.get_image()[:, :, ::-1]
            del predictions, viz, output
        else:
            
            start_time = time.time()
            predictions, segments_info = self.predictor(frame)['panoptic_seg']
            print("--- %s seconds ---" % (time.time() - start_time))
            viz = Visualizer(frame[:, :, ::-1], metadata = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]),scale=1.2, instance_mode = ColorMode.IMAGE_BW)
            output = viz.draw_panoptic_seg_predictions(predictions.to('cpu'),  segments_info)
            result = output.get_image()[:, :, ::-1]
            del predictions,segments_info, viz, output
        return result


class Camera:
    last_frame = None
    last_ready = None
    lock = Lock()

    def __init__(self, rtsp_link, model_type='PS'):
        capture = cv2.VideoCapture(rtsp_link)
        self.detector = Detector(model_type=model_type)
        
        thread = threading.Thread(target=self.rtsp_cam_buffer, args=(capture,), name="rtsp_read_thread")
        thread.daemon = True
        thread.start()

    def rtsp_cam_buffer(self, capture):
        while True:
            with self.lock:
                self.last_ready, self.last_frame = capture.read()


    def getFrame(self):
        if (self.last_ready is not None) and (self.last_frame is not None):
            return self.last_frame.copy()
        else:
            return None

    # def onVideo(self):
    #     while True:
    #         frame =  self.getFrame()

    #         if frame is not None:
    #             frame = imutils.resize(frame, width=500)
    #             result = self.detector.test(frame)

    #             cv2.imshow('frame', result)
    #             if cv2.waitKey(1) == ord('q'):
    #                 break
    #         else:
    #             pass
    

            


        
        
        

        
