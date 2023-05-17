import os
from src.utils.config import get_config_from_json
from src.models.feature_extractor import run_inference_on_images_feature
import os
import sys
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
    for i in range(0,len(img_list),50):
        run_inference_on_images_feature(img_list[i:i+5], model_dir, output_dir)
        print("Step3: find k value")
        os.system(cmd3)
        print("Step4: run k mean algorithm")
        os.system(cmd4)


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
    extract_feature(img_dir, config.paths.model_dir, vector_dir)
