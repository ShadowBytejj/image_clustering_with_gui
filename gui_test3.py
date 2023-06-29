import os
import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
from main import run_function
import math
from src.utils.config import get_config_from_json
from extract_features import FeatureExtractionThread

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化窗口
        self.setWindowTitle('Viewer')
        self.setGeometry(200, 200, 1200, 800)
        self.singleView_mode = True

        # 全局控件，用于添加全局布局
        self.wwg = QWidget()
        # 全局布局, 注意参数wwg
        self.w1 = QVBoxLayout(self.wwg)
        # self.wwg.setLayout(self.w1)

        # 局部布局/控件
            #切换Cluster

            #进度条
        self.pb_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.pb_layout.addWidget(self.progress_bar)

        self.feature_extraction_thread = None

        # 创建 QLabel、Qwidget_grid 和 QScrollArea. Layout可以设置多个Label，但是ScrollArea不可以
        self.label = QLabel()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.widget_gird = QWidget()
        self.widget_gird.setLayout(QGridLayout(self.widget_gird))
        self.widget_gird.layout().addWidget(self.label)


        self.scroll_area.setWidget(self.label)
        #添加到全局布局中
        self.w1.addWidget(self.scroll_area)
        self.w1.addLayout(self.pb_layout)

        #添加cluster button 布局
        self.hlayout = QHBoxLayout()
        self.w1.addLayout(self.hlayout)



        self.setCentralWidget(self.wwg)
        # 初始化图片列表和当前图片的索引
        self.image_list = []
        self.current_image_index = -1


        # 创建“打开”和“下一张”两个 QAction，并添加到菜单栏和工具栏
        self.open_action = QAction('Open Album', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.triggered.connect(self.open_folder)
        self.file_menu = self.menuBar().addMenu('File')
        self.file_menu.addAction(self.open_action)

        self.prev_action = QAction('Previous Page', self)
        self.prev_action.setShortcut('Left')
        self.prev_action.triggered.connect(self.prev_image)
        self.toolbar = self.addToolBar('工具栏')
        self.toolbar.addAction(self.prev_action)

        self.next_action = QAction('Next page', self)
        self.next_action.setShortcut('Right')
        self.next_action.triggered.connect(self.next_image)
        self.toolbar.addAction(self.next_action)

        # 创建View Menu
            # Multiple view
        self.switch_multiple_view_action = QAction('Switch Multiple View', self)  # 添加一个QAction，这里只命名
        self.switch_multiple_view_action.setShortcut('Ctrl+4')  # 添加快捷键
        self.switch_multiple_view_action.triggered.connect(self.switch_multiple_view)  # 添加点击QAction之后触发的内容

            # 16 Multiple view
        self.switch_multiple_view_action_16 = QAction('Switch Multiple View (16)', self)  # 添加一个QAction，这里只命名
        self.switch_multiple_view_action_16.setShortcut('Ctrl+1')  # 添加快捷键
        self.switch_multiple_view_action_16.triggered.connect(self.switch_multiple_view_16)  # 添加点击QAction之后触发的内容

            # 4 Multiple view
        self.switch_multiple_view_action_4 = QAction('Switch Multiple View (4)', self)  # 添加一个QAction，这里只命名
        self.switch_multiple_view_action_4.setShortcut('Ctrl+2')  # 添加快捷键
        self.switch_multiple_view_action_4.triggered.connect(self.switch_multiple_view_4)  # 添加点击QAction之后触发的内容

            # Single view
        self.switch_single_view_action = QAction('Switch Single View', self)  # 添加一个QAction，这里只命名
        self.switch_single_view_action.setShortcut('Ctrl+3')  # 添加快捷键
        self.switch_single_view_action.triggered.connect(self.switch_single_view)  # 添加点击QAction之后触发的内容

        self.view_menu = self.menuBar().addMenu('View')  # 添加Menu中的Bar——View
        self.view_menu.addAction(self.switch_multiple_view_action_16)  # 将QAction:switch_multiple_view_action_16 添加到点击Menu中的View之后的内容
        self.view_menu.addAction(self.switch_single_view_action)  # 将QAction:switch_single_view_action 添加到点击Menu中的View之后的内容
        self.view_menu.addAction(self.switch_multiple_view_action_4)
        self.view_menu.addAction(self.switch_multiple_view_action)


        #创建Option - 删除照片、删除cluster
            #Delete Photo
        self.delete_photo_action = QAction('Delete Photo')
            #Delete Cluster
        self.delete_cluster_action = QAction('Delete Cluster')

            #add into menu
        self.option_menu = self.menuBar().addMenu('Option')

        self.option_menu.addAction(self.delete_photo_action)
        self.delete_photo_action.triggered.connect(self.delete_this_photo)#绑定trigger函数

        self.delete_cluster_action.triggered.connect(self.delete_this_cluster)

        self.option_menu.addAction(self.delete_cluster_action)


        ## 创建clustering选项
        self.run_clustering_action = QAction('clustering image')

        self.clustering_menu = self.menuBar().addMenu('clustering')

        self.clustering_menu.addAction(self.run_clustering_action)

        self.run_clustering_action.triggered.connect(self.start_feature_extraction)


        # 显示窗口
        self.show()

    def start_feature_extraction(self):
        if self.feature_extraction_thread is None or not self.feature_extraction_thread.isRunning():
            self.progress_bar.setValue(0)

            # 实例化自定义线程类并连接信号和槽函数
            config, _ = get_config_from_json("configs\\configs.json")

            object_name = config.model.object_name
            img_dir = os.path.join(config.paths.image_dir, object_name)
            # img_dir = "D:\desktop\image_clustering\data\raw"
            vector_dir = os.path.join(config.paths.vector_dir, object_name)
            print("vector dir is: ", vector_dir)  # 可删除，目的为了看看在哪里
            print("config:", config)
            print("img_dir: ", os.path.join(config.paths.image_dir, object_name))

            # Extract feature for all images in image directory
            # extract_feature_thread = FeatureExtractionThread(img_dir, config.paths.model_dir, vector_dir)


            self.feature_extraction_thread = FeatureExtractionThread(img_dir, config.paths.model_dir, vector_dir)
            self.feature_extraction_thread.progress_updated.connect(self.update_progress_bar)
            self.feature_extraction_thread.progress_updated.connect(self.open_folder)

            # 启动线程
            self.feature_extraction_thread.start()

    def update_progress_bar(self, progress):
        self.progress_bar.setValue(progress)


    def open_folder(self):
        # 弹出文件夹对话框，让用户选择要打开的文件夹

        # folder_name = QFileDialog.getExistingDirectory(self, 'Select album')

        self.res_folder_name = 'results\link\example'

        try:
            if os.listdir(self.res_folder_name):
                self.cluster_list = []
                for dir_name in os.listdir(self.res_folder_name):
                    self.cluster_list.append(os.path.join(self.res_folder_name, dir_name))

                if self.cluster_list:
                    #print(self.cluster_list)
                    self.current_cluster_index = 0
                    self.show_cluster()


            self.cluster_change_layout()

        except:
            pass


        """
        在选择了Ablum之后切换View的模式
        将View Menu添加在已经选择相册后的窗口的Menu中
        此时 image_list已经确认了

        问题：每选一次都会添加一个View
        解决：还是放到主界面初始化的时候
        """
        # self.switch_view_action = QAction('Switch Multiple View', self)  # 添加一个QAction，这里只命名
        # self.switch_view_action.setShortcut('Ctrl+1')  # 添加快捷键
        # self.switch_view_action.triggered.connect(self.switch_multiple_view_16)  # 添加点击QAction之后触发的内容
        # self.view_menu = self.menuBar().addMenu('View')  # 添加Menu中的Bar——View
        # self.view_menu.addAction(self.switch_view_action)  # 将QAction:switch_view_action 添加到点击Menu中的View之后的内容

    def show_cluster(self):

        if self.cluster_list[self.current_cluster_index]:
            self.image_list = []
            for file_name in os.listdir(self.cluster_list[self.current_cluster_index]):
                if file_name.endswith('.jpg') or file_name.endswith('.jpeg') or file_name.endswith('.png'):
                    self.image_list.append(os.path.join(self.cluster_list[self.current_cluster_index], file_name))
            if self.image_list:
                self.current_image_index = 0
                self.switch_multiple_view_16()
                # self.show_image()
        else:
            warn = QMessageBox.question(self, 'non-exist cluster',
                                         f'This cluster does not exist',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


    def switch_multiple_view_16(self):
        # 切换的时候被删除/覆盖了，所以需要重新创建！
        self.singleView_mode = False
        self.widget_gird = QWidget()
        self.widget_gird.setLayout(QGridLayout(self.widget_gird))

        # print(self.label)
        # self.widget_gird.layout().removeWidget(self.widget_gird.layout().itemAt(0).widget())
        # self.widget_gird.layout().itemAt(0).widget().deleteLater()

        if self.image_list:
            image_files = self.image_list
            print(self.image_list)
            self.n_row = 4

            self.scroll_area.setWidget(self.widget_gird)
            end_index = min(self.current_image_index + 16, len(image_files))
            for i, image_file in enumerate(image_files):
                if i >=self.current_image_index and i < end_index:
                    pixmap = QPixmap(self.image_list[i])
                    thumbnail = pixmap.scaled(QSize(200, 200))
                    label2 = QLabel()
                    label2.setPixmap(thumbnail)
                    # edit = QLabel(f"Image {i+1}")
                    self.widget_gird.layout().addWidget(label2, i // self.n_row, i % self.n_row)  # 按照行列数添加控件
                    # grid.addWidget(edit, i // n_row, i % n_row)

    def switch_multiple_view_4(self):
        # 切换的时候被删除/覆盖了，所以需要重新创建！
        self.singleView_mode = False
        self.widget_gird = QWidget()
        self.widget_gird.setLayout(QGridLayout(self.widget_gird))

        # print(self.label)
        # self.widget_gird.layout().removeWidget(self.widget_gird.layout().itemAt(0).widget())
        # self.widget_gird.layout().itemAt(0).widget().deleteLater()
        self.n_row = 2
        if self.image_list:
            image_files = self.image_list
            self.scroll_area.setWidget(self.widget_gird)
            end_index = min(self.current_image_index + 4, len(image_files))

            for i, image_file in enumerate(image_files):
                if i >=self.current_image_index and i < end_index:
                    pixmap = QPixmap(self.image_list[i])
                    thumbnail = pixmap.scaled(QSize(400, 400))
                    label2 = QLabel()
                    label2.setPixmap(thumbnail)
                    # edit = QLabel(f"Image {i+1}")
                    self.widget_gird.layout().addWidget(label2, i // self.n_row, i % self.n_row)  # 按照行列数添加控件
                    # grid.addWidget(edit, i // n_row, i % n_row)

    def switch_multiple_view(self):
        # 切换的时候被删除/覆盖了，所以需要重新创建！
        self.singleView_mode = False
        self.widget_gird = QWidget()
        self.widget_gird.setLayout(QGridLayout(self.widget_gird))

        # print(self.label)
        # self.widget_gird.layout().removeWidget(self.widget_gird.layout().itemAt(0).widget())
        # self.widget_gird.layout().itemAt(0).widget().deleteLater()

        if self.image_list:
            print(self.image_list)
            image_files = self.image_list
            n_row = math.ceil(math.sqrt(len(image_files)))

            self.scroll_area.setWidget(self.widget_gird)

            for i, image_file in enumerate(image_files):
                pixmap = QPixmap(self.image_list[i])
                thumbnail = pixmap.scaled(QSize(100, 100))
                label2 = QLabel()
                label2.setPixmap(thumbnail)
                # edit = QLabel(f"Image {i+1}")
                self.widget_gird.layout().addWidget(label2, i // n_row, i % n_row)  # 按照行列数添加控件
                # grid.addWidget(edit, i // n_row, i % n_row)


    def switch_single_view(self):

        self.singleView_mode = True
        # 切换的时候被删除/覆盖了，所以需要重新创建！
        self.label = QLabel()
        self.show_image()

        if self.label:
            self.scroll_area.setWidget(self.label)
            # self.widget_gird.layout().addWidget(self.label)
            # self.show_image()
        else:
            return

    def prev_image(self):
        # 如果没有打开任何图片，则直接返回
        if (not self.image_list):
            return
        if (self.singleView_mode == False):
            if self.n_row == 4:
                self.current_image_index = (self.current_image_index - (self.n_row)*(self.n_row)) % len(self.image_list)
                self.switch_multiple_view_16()
            if self.n_row == 2:
                self.current_image_index = (self.current_image_index - (self.n_row) * (self.n_row)) % len(self.image_list)
                self.switch_multiple_view_4()
        else:
            # 切换到上一张图片
            self.current_image_index = (self.current_image_index - 1) % len(self.image_list)
            self.show_image()

    def next_image(self):
        # 如果没有打开任何图片，则直接返回
        if (not self.image_list):
            return
        if (self.singleView_mode == False):
            if self.n_row == 4:
                self.current_image_index = (self.current_image_index + (self.n_row)*(self.n_row)) % len(self.image_list)
                self.switch_multiple_view_16()
            if self.n_row == 2:
                self.current_image_index = (self.current_image_index + (self.n_row) * (self.n_row)) % len(self.image_list)
                self.switch_multiple_view_4()
        else:
            # 切换到下一张图片
            self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
            self.show_image()

    def show_image(self):
        # 从文件中加载图片
        pixmap = QPixmap(self.image_list[self.current_image_index])

        # 将图片显示在 QLabel 中，并调整 QLabel 的大小以适应图片大小
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.resize(pixmap.width(), pixmap.height())
        print(self.label)

        # 调整 QScrollArea 的视口以确保图片始终可见
        self.scroll_area.ensureVisible(0, 0)

    def delete_this_photo(self):
        # 获取当前显示的照片路径
        current_photo_path = self.image_list[self.current_image_index]
        # 确认删除操作
        reply = QMessageBox.question(self, 'Confirm Delete', f'This operation is not recovered, confrim deleting it? {current_photo_path}？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 执行删除操作
            os.remove(current_photo_path)
            # 更新显示的照片列表
            self.show_image()

    def delete_this_cluster(self):
        current_cluster_path = self.cluster_list[self.current_cluster_index]
        #confirm deletion
        reply = QMessageBox.question(self, 'Confirm Delete',
                                     f'This operation      is not recovered, confrim deleting it? {current_cluster_path}？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 执行删除操作
            for img in self.image_list:
            # 更新显示的照片列表
                os.remove(img)

            self.show_cluster()



    def cluster_change_layout(self):

        while self.hlayout.count() > 0:
            item = self.hlayout.takeAt(0)
            widget = item.widget()
            self.hlayout.removeWidget(widget)
            widget.deleteLater()

        self.cluster_button_vlayout = QVBoxLayout()

        self.cluster_button_hlayout = QHBoxLayout()

        self.cluster_button_vlayout.addLayout(self.cluster_button_hlayout)
        
        # print(self.cluster_list)
        # self.hlayout = QHBoxLayout()
        for i,dir in enumerate(self.cluster_list):
            print('i,dir::::::',i,dir)
            cluster_button_text = dir.split("\\")[3]
            button_img = QPixmap(os.path.join(dir,os.listdir(dir)[0]))
            # button_img = QPixmap('C:/Users/朱启津/Desktop/Album\\TEST1\\COCO_train2014_000000000575.jpg')

            cluster_button = QPushButton()
            cluster_button.setText(cluster_button_text)
            cluster_button.setIcon(QIcon(button_img))
            cluster_button.setIconSize(cluster_button.sizeHint())

            # 调整按钮大小以适应图像和文本

            cluster_button.clicked.connect(lambda checked, idx=i: self.change_cluster(idx))
            # print("connect")
            self.cluster_button_hlayout.addWidget(cluster_button)

            if (i + 1) % 10 == 0:
                self.cluster_button_hlayout = QHBoxLayout()
                self.cluster_button_vlayout.addLayout(self.cluster_button_hlayout)

        self.w1.addLayout(self.cluster_button_vlayout)
            # self.hlayout.addWidget(cluster_button)


        # self.w1.addLayout(self.hlayout)

    def change_cluster(self,dir_index):

        self.switch_single_view()
        self.current_cluster_index = dir_index
        self.show_cluster()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageViewer()
    sys.exit(app.exec_())
    """
    Start mainloop, event stream processing starts here
    The reason of '_' in 'exec_': Avoid ambiguous with the 'exec' keyword in Python 2.
    """

