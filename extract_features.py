import os
from src.utils.config import get_config_from_json
from src.models.feature_extractor import run_inference_on_images_feature
import os
import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal
import time

IMAGE_EXTENSION = ('jpg', 'jpeg', 'bmp', 'png')


def extract_feature(img_dir, model_dir, output_dir):
    """
    Extract image features of all images in img_dir and save feature vectors to output_dir
    :param img_dir: (string) directory containing images to extract feature
    :param model_dir: (string) directory containing extractor model
    :param output_dir: (string) directory to save feature vector file
    :return:
    """
    # Get list of image paths
    img_list = [os.path.join(img_dir, img_file) for img_file in os.listdir(img_dir) if img_file.endswith(IMAGE_EXTENSION)]

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(__file__)

    cmd3 = "python " + os.path.join(application_path, "find_k.py")
    cmd4 = "python " + os.path.join(application_path, "run_k_mean.py")

    # Run getting feature vectors for each image

    #############batch by batch
    batch_num = 50
    print(len(img_list),'img llllllllllllllllllllllllllllllllllll')
    for i in range(0,len(img_list),batch_num):
        run_inference_on_images_feature(img_list[i:i+batch_num], model_dir, output_dir)
        print("Step3: find k value")
        os.system(cmd3)
        print("Step4: run k mean algorithm")
        os.system(cmd4)


class FeatureExtractionThread(QThread):
    progress_updated = pyqtSignal(int)

    def __init__(self, img_dir, model_dir, output_dir):
        super().__init__()
        self.img_dir = img_dir
        self.model_dir = model_dir
        self.output_dir = output_dir

    def run(self):
        img_dir = self.img_dir.encode('ascii').decode('utf-8')
        model_dir = self.model_dir.encode('ascii').decode('utf-8')
        output_dir = self.output_dir.encode('ascii').decode('utf-8')

        img_list = [os.path.join(img_dir, img_file) for img_file in os.listdir(img_dir) if img_file.endswith(IMAGE_EXTENSION)]
        total_images = len(img_list)

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(__file__)

        print('problem 1')
        cmd3 = "python " + os.path.join(application_path, "find_k.py")
        cmd4 = "python " + os.path.join(application_path, "run_k_mean.py")
        print('problem 2')

        print('img_dir, model_dir, output_dir',img_dir, model_dir, output_dir,end='\n')
        print('cmd', cmd3,cmd4)


        batch_num = 200

        for i in range(0, len(img_list), batch_num):
            end = (i+batch_num)
            if len(img_list)-1 - (i+batch_num) < batch_num:
                print('last batch')
                end = len(img_list)

            run_inference_on_images_feature(img_list[i:end], model_dir, output_dir)
            print("Step3: find k value")
            os.system(cmd3)
            print("Step4: run k mean algorithm")
            os.system(cmd4)

            progress = int((end) / len(img_list) * 100)
            self.progress_updated.emit(progress)

        print('end::::',end)


if __name__ == "__main__":
    # Get config
    config, _ = get_config_from_json("configs\\configs.json")

    object_name = config.model.object_name
    img_dir = os.path.join(config.paths.image_dir, object_name)
    #img_dir = "D:\desktop\image_clustering\data\raw"
    vector_dir = os.path.join(config.paths.vector_dir, object_name)
    print("vector dir is: ",vector_dir) #可删除，目的为了看看在哪里
    print("config:", config)
    print("img_dir: ", os.path.join(config.paths.image_dir, object_name))

    # Extract feature for all images in image directory
    extract_feature_thread = FeatureExtractionThread(img_dir, config.paths.model_dir, vector_dir)
    extract_feature_thread.run()



    # extract_feature(img_dir, config.paths.model_dir, vector_dir)
