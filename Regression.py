from PIL import Image
import random, math, numpy as np
from collections import Counter

image_tocolor = 'Namibia_dark_sky.jpg'

img = Image.open(image_tocolor)
pixels = img.load()

gray_img = Image.open(image_tocolor)
gray_pixels = gray_img.load()

final_img = Image.open(image_tocolor)
final_pixels = final_img.load()

width = img.size[0]
height = img.size[1]

gray_matrix = []
matrix = []
weights = []
alpha = 0.0005


def setup():
    for i in range(width):
        gray_row = []
        matrix_row = []
        for j in range(height):
            p = pixels[i,j]
            gray = int(0.21*p[0] + 0.72*p[1] + 0.07*p[2])
            gray_pixels[i,j] = (gray, gray, gray)
            gray_row.append(float(gray)/255.0)
            matrix_row.append([float(p[0])/255.0, float(p[1])/255.0, float(p[2])/255.0])
        gray_matrix.append(gray_row)
        matrix.append(matrix_row)

    patch_d = list()
    for i in range(width):
        patch_d.append(list())
        for j in range(height):
            if i==0 or j==0 or i==width-1 or j==height-1:
                patch_d[i].append(-1)
                continue
            neighbors = [[-1,-1], [-1,0], [-1,1], [0,-1], [0,0], [0,1], [1,-1], [1,0], [1,1]]
            patch = list()
            for _ in range(9):
                neighbor = gray_pixels[i+neighbors[_][0], j+neighbors[_][1]]
                patch.append(neighbor[0])
            patch = np.array(patch)
            patch_d[i].append(patch)
    global patch_data 
    patch_data = np.array(patch_d,  dtype="object")


def stochastic_descent(color):
    neighbors = [[-1,-1], [-1,0], [-1,1], [0,-1], [0,0], [0,1], [1,-1], [1,0], [1,1]]
    x = random.randint(1, width//2-1)
    y = random.randint(1, height-2)
    wx = weights[9]
    for i in range(9):
        wx = wx + weights[i]*float(gray_matrix[x+neighbors[i][0]][y+neighbors[i][1]])
    fx = 1/(1+math.exp(-wx))
    loss = fx-matrix[x][y][color]
    for i in range(9):
        weights[i] = weights[i]-alpha*loss*float(gray_matrix[x+neighbors[i][0]][y+neighbors[i][1]])*fx*(1-fx)
    #weights[i] = weights[i]-alpha*loss*float(gray_matrix[x+neighbors[i][0]][y+neighbors[i][1]])

if __name__ == '__main__':
    w = 0.000001
    constant = 0.0
    setup()
    red_weights = []
    green_weights = []
    blue_weights = []
    for i in range(9):
        weights.append(w)
    weights.append(constant)
    
    for i in range(1000000): 
        stochastic_descent(0)
    for i in range(10):
        red_weights.append(weights[i])
        weights[i]=w
    weights[9]=constant

    for i in range(1000000):
        stochastic_descent(1)
    for i in range(10):
        green_weights.append(weights[i])
        weights[i]=w
    weights[9]=constant

    for i in range(1000000):
        stochastic_descent(2)
    for i in range(10):
        blue_weights.append(weights[i])
    
    for i in range(width//2, width-1):
        for j in range(1, height-1):
            neighbors = [[-1,-1], [-1,0], [-1,1], [0,-1], [0,0], [0,1], [1,-1], [1,0], [1,1]]
            wx = red_weights[9]
            for k in range(9):
                wx = wx + red_weights[k]*float(gray_matrix[i+neighbors[k][0]][j+neighbors[k][1]])
            fx = 1/(1+math.exp(-wx))
            redvalue = int(fx*255)
            wx = green_weights[9]
            for k in range(9):
                wx = wx + green_weights[k]*float(gray_matrix[i+neighbors[k][0]][j+neighbors[k][1]])
            fx = 1/(1+math.exp(-wx))
            greenvalue = int(fx*255)
            wx = blue_weights[9]
            for k in range(9):
                wx = wx + blue_weights[k]*float(gray_matrix[i+neighbors[k][0]][j+neighbors[k][1]])
            fx = 1/(1+math.exp(-wx))
            bluevalue = int(fx*255)
            final_pixels[i, j] = (redvalue, greenvalue, bluevalue)

    for i in range(width//2, width-1):
        for j in range(1, height-1):
            redvalue = final_pixels[i, j][0]
            greenvalue = final_pixels[i, j][1]
            bluevalue = final_pixels[i, j][2]
            gray = 0.21*redvalue + 0.72*greenvalue + 0.07*bluevalue
            ratio = float(gray_matrix[i][j])/(gray/255)
            final_pixels[i, j] = (int(redvalue*ratio), int(greenvalue*ratio), int(bluevalue*ratio))

    final_img.show()
    print(red_weights)
