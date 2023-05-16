import os
import sys
import time
import tkinter
from tkinter.filedialog import (askopenfilename,
                                askopenfilenames,
                                askdirectory,
                                asksaveasfilename)
# def run_main():
#     if getattr(sys, 'frozen', False):
#         application_path = os.path.dirname(sys.executable)
#     else:
#         application_path = os.path.dirname(__file__)
#
#     print("Current Path:::::::::::::::::", (application_path))
#
#     cmd1="python "+ os.path.join(application_path,"build_data.py")
#     cmd2="python "+ os.path.join(application_path,"extract_features.py")
#     cmd3="python "+ os.path.join(application_path,"find_k.py")
#     cmd4="python "+ os.path.join(application_path,"run_k_mean.py")
#
#     print("Step1: Build data")
#     os.system(cmd1)
#     print("Step2: extract_features")
#     os.system(cmd2)
#     print("Step3: find k value")
#     os.system(cmd3)
#     print("Step4: run k mean algorithm")
#     os.system(cmd4)
#
#
#
# def createEntry(root,cl,rw,txt = 'Please enter', btn_txt = "confirm", clikced = None, bt = None):
#     """
#
#     """
#     lbl = tkinter.Label(root , text = txt)
#     lbl.grid(column=cl, row = rw)
#
#     #adding Entry Field
#     # txt = tkinter.Entry(root, width = 10)
#     # txt.grid(column=cl + 1, row = rw)
#
#     def click():
#         lbl.configure(text = askdirectory())
#
#     #if meed a button
#     if bt:
#         btn = tkinter.Button(root, text = btn_txt, fg = "black",command=click)
#         btn.grid(column=cl+2, row = rw)
#
#
#
# def User_gui():
#
#     root = tkinter.Tk()
#     root.title("Image cluster")
#
#     createEntry(root,cl = 0, rw = 0, txt = "Select your album directory", bt = True, btn_txt = "Select")
#     createEntry(root, cl=0, rw=1, txt="Select your output path", bt=True, btn_txt="Select")
#
#     btn_run  = tkinter.Button(root, text = "Run", fg = "red", command = run_main)
#     btn_run.grid(column=0, row =2)
#
#     root.mainloop()
#
#
# if __name__ =='__main__':
#     User_gui()

start_time = time.time()
if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
else:
        application_path = os.path.dirname(__file__)

print("Current Path:::::::::::::::::", (application_path))

cmd1="python "+ os.path.join(application_path,"build_data.py")
cmd2="python "+ os.path.join(application_path,"extract_features.py")
cmd3="python "+ os.path.join(application_path,"find_k.py")
cmd4="python "+ os.path.join(application_path,"run_k_mean.py")

print("Step1: Build data")
os.system(cmd1)
print("Step2: extract_features")
os.system(cmd2)
print("Step3: find k value")
os.system(cmd3)
print("Step4: run k mean algorithm")
os.system(cmd4)

end_time = time.time()

print('total cost = ',end_time - start_time, 's')