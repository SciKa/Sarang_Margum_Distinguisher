import engine
import tkinter.filedialog as tk
import os
import shutil

engine.brainer()

origin_path = tk.askdirectory(title="select original images' folder")
neko_move_path = tk.askdirectory(title="select where to send the cat pictures. ")

images = os.listdir(origin_path)


neko_list = []
for img in images:
    imgpath = origin_path + "/" + img
    result = engine.judge(imgpath)
    if result == 1:
            neko_list.append(imgpath)


print(neko_list)

for img in neko_list:
    shutil.move(img,neko_move_path)
