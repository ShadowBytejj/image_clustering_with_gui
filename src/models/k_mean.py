import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import pandas as pd
import json


def plot_3d(vector_array, save_plot_dir):
    """
    Plot 3D vector features distribution from vector array
    :param vector_array: (N x 3) vector array, where N is the number of images
    :param save_plot_dir: (string) directory to save plot
    :return: save 3D distribution feature to disk
    """
    principal_df = pd.DataFrame(data=vector_array, columns=['pc1', 'pc2', 'pc3'])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs = principal_df['pc1']
    ys = principal_df['pc2']
    zs = principal_df['pc3']
    ax.scatter(xs, ys, zs, s=50, alpha=0.6, edgecolors='w')

    ax.set_xlabel('pc1')
    ax.set_ylabel('pc2')
    ax.set_zlabel('pc3')

    plt.savefig(save_plot_dir + '/3D_scatter.png')
    plt.close()


def plot_2d(vector_array, save_plot_dir):
    """
    Plot 2D vector features distribution from vector array
    :param vector_array: (N x 2) vector array, where N is the number of images
    :param save_plot_dir: (string) directory to save plot
    :return: save 2D distribution feature to disk
    """
    principal_df = pd.DataFrame(data = vector_array, columns = ['pc1', 'pc2'])
    fig = plt.figure()
    ax = fig.add_subplot(111)

    xs = principal_df['pc1']
    ys = principal_df['pc2']
    ax.scatter(xs, ys, s=50, alpha=0.6, edgecolors='w')

    ax.set_xlabel('pc1')
    ax.set_ylabel('pc2')

    plt.savefig(save_plot_dir + '/2D_scatter.png')
    plt.close()


def read_vector(img_dir):
    """
    Read vector in a directory to array (N x D): N is number of vectors, D is vector's dimension
    :param img_dir: (string) directory where feature vectors are
    :return: (array) N X D array
    """
    vector_files = [f for f in os.listdir(img_dir) if f.endswith(".npz")]
    vector_array = []
    for img in vector_files:
        vector = np.loadtxt(os.path.join(img_dir, img))
        vector_array.append(vector)
    vector_array = np.asarray(vector_array)
    return vector_array, vector_files


def find_best_k(vector_array, save_plot_dir, max_k=100):#这里本来设置为100，10只是为了测试小样本
    """
    Find best number of cluster
    :param vector_array: (array) N x D dimension feature vector array
    :param save_plot_dir: (string) path to save cost figure
    :param max_k: (int) maximum number of cluster to analyze
    :return: plot the elbow curve to figure out the best number of cluster
    """

    cost = []
    dim = vector_array.shape[1]
    min_diff_k = 1
    # diff = []
    min_diff = 10000
    for i in range(1, max_k):
        kmeans = KMeans(n_clusters=i, random_state=0)
        kmeans.fit(vector_array)
        cost.append(kmeans.inertia_)
        if i>=2 and min_diff >= 10000:
            min_diff = abs(cost[-2]-cost[-1])
            min_diff_k = i

            # diff.append(abs(cost[-2]-cost[-1]))
        # else:
        #     min_diff = cost[-1]
    print('cost:::::::::::::::::::\n',cost)
    print('find min_diff:::::::::::::::::::::\n',min_diff)
    print('k value:',min_diff_k)
    # print('difffffffffffffff\n',diff)
    # plot the cost against K values
    plt.plot(range(1, max_k), cost, color='g', linewidth='3')
    plt.xlabel("Value of K")
    plt.ylabel("Squared Error (Cost)")
    plt.savefig(save_plot_dir + '/cost_' + str(dim) + 'D.png')
    plt.close()

    import json

    # 打开 JSON 文件并加载内容
    with open("configs/configs.json", 'r') as f:
        config = json.load(f)

    # 修改 k 的值
    config['model']['k'] = min_diff_k

    # 将更改保存回 JSON 文件
    with open("configs/configs.json", 'w') as f:
        json.dump(config, f, indent=4)

    return min_diff_k
    

def k_mean(vector_array, k):
    """
    Apply k-mean clustering approach to assign each feature image in vector array to suitable subsets
    :param vector_array: (array) N x D dimension feature vector array
    :param k: (int) number of cluster
    :return: (array) (N x 1) label array
    """
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(vector_array)
    labels = kmeans.labels_
    return labels


def reduce_dim_combine(vector_array, dim=2):
    """
    Applying dimension reduction to vector_array
    :param vector_array: (array) N x D dimension feature vector array
    :param dim: (int) desired dimension after reduction
    :return: (array) N x dim dimension feature vector array
    """
    # Standardizing the features
    vector_array = StandardScaler().fit_transform(vector_array)

    # Apply PCA first to reduce dim to 50, 但是到当样本数少的时候50会报错。因为必须要小于min(n_samples, n_features)
    pca = PCA(n_components=50)
    vector_array = pca.fit_transform(vector_array)

    # Apply tSNE to reduce dim to #dim
    model = TSNE(n_components=dim, random_state=0)
    vector_array = model.fit_transform(vector_array)
    
    return vector_array

    
if __name__ == "__main__":
    # Mode: investiagate to find the best k, inference to cluster
    # MODE = "investigate"
    MODE = "inference"

    # Image vectors root dir
    img_dir = "results/image_vectors/"

    # Final dimension
    dim = 2

    for object_name in os.listdir(img_dir):
        print("Process %s" % object_name)
        # object_name = img_dir.split("/")[-1]
        vector_array, img_files = read_vector(os.path.join(img_dir, object_name))
        # k_mean(vector_array)
        
        if vector_array.shape[0] >= 450:
            # Apply dimensional reducing approach
            vector_array = reduce_dim_combine(vector_array, dim)

            if MODE == "investigate":

                # Plot data distribution after reducing dimension
                if dim == 2:
                    plot_2d(vector_array)
                    save_plot_dir = "visualization/2D/"
                elif dim == 3:
                    plot_3d(vector_array)
                    save_plot_dir = "visualization/3D/"
                else:
                    raise ValueError("Not support dimension")

                # Plot cost chart to find best value of k
                k_value = find_best_k(vector_array, object_name, save_plot_dir)
                print('best k value:',k_value)
                continue

            # Find label for each image
            labels = k_mean(vector_array, k=k_value).tolist()
            print('k_mean labels:',labels)
            assert len(labels) == len(img_files), "Not equal length"

            label_dict = [{"img_file": img_files[i].replace(".npz", "").replace(object_name + '_', ""), "label": str(labels[i]), "prob": "1.0"} for i in range(len(labels))]

            # Save to disk
            label_dir = "results/img_cluster/"
            label_outpath = os.path.join(label_dir, object_name + ".json")
            # os.makedirs(label_outpath, exist_ok=True)
            with open(label_outpath, 'w') as fp:
                json.dump({"data": label_dict}, fp)