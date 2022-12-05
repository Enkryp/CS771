import cv2 as cv
import numpy as np
import time
import os
import matplotlib.pyplot as plt
import tensorflow as tf
import pickle as pkl
import math
import random
from sklearn.cluster import KMeans
def load_reference_images(folder):
    ref_dir = {}
    for filename in os.listdir(folder):
        img = cv.imread(os.path.join(folder, filename))
        ref = filename.split(".")[0]
        ref_dir[ref] = img
        # Make black background white
        ref_dir[ref][ref_dir[ref] == 0] = 255
    return ref_dir

def remove_stray_lines(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Dilate then erode to remove noise
    # Stronger dilation than erosion
    kernel1 = np.ones((3,3),np.uint8)
    kernel2 = np.ones((4,4),np.uint8)
    img = cv.dilate(img,kernel2,iterations = 1)
    img = cv.erode(img,kernel1,iterations = 1)
    return img


def morph_grad_and_threshold(img):
    # Morphological gradient
    kernel3 = np.ones((6,6),np.uint8)
    img = cv.morphologyEx(img, cv.MORPH_GRADIENT, kernel3)
    img = cv.threshold(img, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
    return img


def find_largest_connected_component(img):
    # find connected components
    nlabels, labels, stats, centroids = cv.connectedComponentsWithStats(img, connectivity=8, ltype=cv.CV_32S)
    # find the largest component
    largest = 0
    largest_area = 0
    for i in range(1, nlabels):
        area = stats[i, cv.CC_STAT_AREA]
        if area > largest_area:
            largest_area = area
            largest = i
    # Make largest connected component black
    img[labels == largest] = 0
    return img
def get_parent(hierarchy, index):
    return hierarchy[0][index][3]

def contour_based_segmentation(img):

    contours, hierarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    img = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
    useful_contours = []
    outer_contours = []
    for i in range(len(contours)):
        level = 1
        parent = get_parent(hierarchy, i)
        while parent != -1:
            level  = level + 1
            parent = get_parent(hierarchy, parent)
        if level == 1:
            outer_contours.append(contours[i])
        elif level == 2:
            useful_contours.append(contours[i])
        else:
            # Fit polygon to contour
            epsilon = 0.12*cv.arcLength(contours[i],True)
            approx = cv.approxPolyDP(contours[i],epsilon,True)
            # If area of polygon is close to contour area, it is a useful contour
            if(approx is not None and cv.contourArea(approx) > 0.9*cv.contourArea(contours[i])):
                useful_contours.append(contours[i])
    
    
    # Solid fill the contours
    # Sort useful contours by area
    outer_contours = sorted(outer_contours, key=cv.contourArea, reverse=True)
    # Find the largest decreasing area
    useful_contours.append(outer_contours[0])
    for i in range(1,len(outer_contours)):
        if cv.contourArea(outer_contours[i]) < cv.contourArea(outer_contours[i-1]) * 0.1:
            break
        useful_contours.append(outer_contours[i])
    # Add inner contours
    empty_img = np.zeros(img.shape, np.uint8)

    cv.drawContours(empty_img, useful_contours, -1, (255,0,0), -1)
    img = empty_img
    return img

def show_image(img,name = "image"):
    
    cv.imshow(name, img)
    cv.waitKey(0)
    cv.destroyAllWindows()


def process(img):
    # Get time for each step
    img = remove_stray_lines(img)
    img = morph_grad_and_threshold(img)
    img = find_largest_connected_component(img)
    img = contour_based_segmentation(img)
    # Show image

    images = better_image_splitter(img)
    if(images is None):
        return []
    if(len(images) != 3):
        pass
    return images   

def better_image_splitter(image,x_step = 5,y_step = 5):
    # Randomly sample 10000 pixels
    # Store if they are white
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = cv.threshold(image, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]

    white_pixels = []

    for j in range(0,image.shape[1],x_step):
        for i in range(0,image.shape[0],y_step):
            if image[i,j] == 255:
                white_pixels.append([i,j])

    # Kmeans clustering
    # sort by x
    centers = []
    # Find two largest gaps in x
    
    curr_x = 0
    curr_y = 0
    num = 0
   
    for i in range(1,len(white_pixels)):
        if(white_pixels[i][1] - white_pixels[i-1][1] > 35):
            centers.append([curr_x/num,curr_y/num])
            curr_x = 0
            curr_y = 0
            num = 0
        else:
            curr_x = curr_x + white_pixels[i][0]
            curr_y = curr_y + white_pixels[i][1]
            num = num + 1
    # add last center
    centers.append([curr_x/num,curr_y/num])
    # Sort by x position
    centers = sorted(centers, key=lambda x: x[1])
    if(len(centers) != 3):
        return
    split_images = []
    for i in range(3):
        # Each box is 140x140
        # Center of box is center of cluster
        x = centers[i][1] - 70
        y = centers[i][0] - 70
        # Take floor for all values
        x = math.floor(x)
        y = math.floor(y)
        if(x < 0):
            x = 0
        if(y < 0):
            y = 0
        split_images.append(image[y:y+140, x:x+140])
    return split_images

def make_preds(images, model, ref_dir):
    # Get predictions
    letters = []
    for i in range(len(images)):
        # Resize to 140x140
        # Apply gaussian blur
        images[i] = cv.GaussianBlur(images[i], (5,5), 0)
        images[i] = cv.resize(images[i], (140, 140))
        # Normalize
        images[i] = images[i] / 255
        # Get preds
        preds = model.predict(images[i].reshape(1, 140, 140, 1))
        # Get index of max value
        index = np.argmax(preds)
        # Get letter
        letter = ref_dir[index]
        letters.append(letter)
    return letters

def generate_training_data(num_images = 1500):
    names = []
    labels = []
    dataset = []
    with open(os.path.join("curr_train", "labels.txt"), "r") as f:
        for line in f:
            line = line.strip()
            line = line.split(",")
            names.append([line[0], line[1], line[2]])  
    i = 0
    for file  in os.listdir("curr_train"):
        if(file.endswith(".png")):
            index = int(file.split(".")[0])
            img = cv.imread(os.path.join("curr_train", file))
            images = process(img)
            if(len(images) != 3):
                img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                images = [img[0:140, 13:153], img[9:140+9, 200:200+140], img[0:140, 340:340+140]]
            # join dataset and images
            for j in range(len(images)):
                images[j] = cv.resize(images[j], (64, 64))
                images[j] = images[j] / 255
                dataset.append(images[j])
                labels.append(names[index][j])
    
    return dataset, labels