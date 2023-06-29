import os
from src.utils.config import get_config_from_json
from src.models.k_mean import read_vector, reduce_dim_combine, plot_2d, plot_3d, find_best_k
import json
IMAGE_EXTENSION = ('jpg', 'jpeg', 'bmp', 'png')


def find_k(vector_array, save_plot_dir, dim=2):
    """
    Find the best number of cluster by looking at the cost plot
    :param vector_array: (array) (N x D) array of feature vectors
    :param save_plot_dir: (string) directory to save plots
    :param dim: (int) desired dimension after reduction
    :return:
    """

    os.makedirs(save_plot_dir, exist_ok=True)
    print(vector_array.shape[0]) #这是样本数量，本算法建议样本数量大于250，否则可能会出现cluster的数量大于样本数量
    if vector_array.shape[0] >= 250:
        # Plot data distribution after reducing dimension
        if dim == 2:
            plot_2d(vector_array, save_plot_dir)
        elif dim == 3:
            plot_3d(vector_array, save_plot_dir)
        else:
            raise ValueError("Not support dimension")

        # Plot cost chart to find best value of k
        find_best_k(vector_array, save_plot_dir)

    else:
        raise ValueError("If number of image is smaller than 250, it is recommended to use hierarchical cluster.")


if __name__ == "__main__":
    # Get config
    config, _ = get_config_from_json("configs/configs.json")

    object_name = config.model.object_name

    dim = config.model.reduced_dimension

    vector_dir = os.path.join(config.paths.vector_dir, object_name)
    #print(vector_dir)
    save_plot_dir = os.path.join(config.paths.plot_dir, object_name)
    #print(save_plot_dir)

    # Read feature vector from vector dir
    vector_array, vector_files = read_vector(vector_dir)
    # print("before : ",vector_array)
    # Apply dimensional reducing approach
    vector_array = reduce_dim_combine(vector_array, dim=dim)#会报错
    # print("after: ",vector_array)
    # Find best K
    find_k(vector_array, save_plot_dir, dim=dim)
