# To detect Number Plate from the image

from PIL import Image
import os
from imageai.Detection.Custom import CustomObjectDetection
from ocr import extractnumber



class plate_detector(extractnumber):
    def start_detection(self, img):
        self.img = img
        # to load detection model
        self.model_path = 'models\detection_model-ex-005--loss-0010.397.h5'
        self.json_path = 'json\detection_config.json'
        self.load_model()
        
    

    def load_model(self):
        detector = CustomObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath(self.model_path)
        detector.setJsonPath(self.json_path)
        detector.loadModel()
        self.detect(detector)

    def detect(self, detector):
        directory = r'sample' 
        os.chdir(directory)
        self.detections = detector.detectObjectsFromImage(input_image= self.img , output_image_path='plate-detected.jpg')
        self.save()
    
    def save(self):

        x = 0
        # cropping number plate from image
        for obj in self.detections:
            print (obj['name'])
            print (obj['percentage_probability'])
            print (obj['box_points'])
            x = obj['box_points'][0]
            y = obj['box_points'][1]
            w = obj['box_points'][2]
            h = obj['box_points'][3]
            print ('\n')

        if x!= 0:
            # saveing files
            pil_image = Image.open("plate-detected.jpg")
            os.chdir('../')


            directory = r'detection' 
            os.chdir(directory)
            pil_image.save('plate-detected.jpg')

            os.chdir('../')
            pil_image = pil_image.crop((x, y, w, h))
            directory = r'plates'
            os.chdir(directory)
            pil_image.save('plate-detected.jpg') 



            os.chdir('../')
            directory = r'sample' 
            os.chdir(directory)
            os.remove('plate-detected.jpg')
            os.chdir('../')
            
        else:
            print("can't detect")

