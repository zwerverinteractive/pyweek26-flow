import os
import pygame

files = [f for f in listdir(".") if isfile(join(".", f))]
images = []
for file in files:
    if file[-4:] == ".png":
        
