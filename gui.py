# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 15:31:04 2020

@author: hp
"""

import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import _thread
import json



from tkinter import *

window = Tk()

window.title("Local Video Player")


class Home:
    

    def __init__(self):
         self.btn_submit=tkinter.Button(window, text="Submit", width=30,command =  self.join )
         self.btn_submit.pack(anchor=tkinter.CENTER, expand=True)
    
    
    def join(self):
        textExample = tkinter.Text(window, height=10)
        textExample.pack()
        btn_submit1=tkinter.Button(window, text="Join rooom", width=30 )
        btn_submit1.pack(anchor=tkinter.CENTER, expand=True)
        
        
Home()
window.mainloop()

#class Home:
#    
#
#
#
#
#
#
#Home(tkinter.Tk(), "Tkinter and OpenCV")






