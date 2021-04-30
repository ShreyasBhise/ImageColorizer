#python3 -m pip install --upgrade Pillow
from PIL import Image
import random, math, numpy as np
from collections import Counter

image_tocolor = 'imagedeepfried.jpg'

img = Image.open(image_tocolor)
pixels = img.load()

gray_img = Image.open(image_tocolor)
gray_pixels = gray_img.load()

final_img = Image.open(image_tocolor)
final_pixels = final_img.load()

width = img.size[0]
height = img.size[1]


def setup():
     for i in range(width):
          for j in range(height):
               p = gray_pixels[i,j]
               gray = int(0.21*p[0] + 0.72*p[1] + 0.07*p[2])
               gray_pixels[i,j] = (gray, gray, gray)

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

centers = list()
pixel_cluster = list()
#5-means clustering for left side of the image to get 5 major colors to use
def clustering():
     #randomly assign 5 inital centers

     for _ in range(5):
          r = random.randint(0,255)
          g = random.randint(0,255)
          b = random.randint(0,255)
          centers.append((r,g,b))
     print(centers)


     #repeat until centers do not change
     change = True


     #assign a cluster value to each pixel
     for i in range(int(width/2)):
          pixel_cluster.append(list())
          for j in range(height):
               pixel_cluster[i].append(-1)

     while change:
          # assign each pixel to closest center
          avg_clusters = [(0,0,0)]*5
          cluster_count = [0]*5

          for i in range(int(width/2)):
               for j in range(height):
                    p = pixels[i,j]
                    min_distance = -1
                    for cluster_num in range(5):
                         center = centers[cluster_num]
                         c_r = center[0]
                         c_g = center[1]
                         c_b = center[2]
                         distance = (p[0]-c_r)**2 + (p[1]-c_g)**2 + (p[2]-c_b)**2
                         if min_distance == -1:
                              min_distance = distance
                              cluster = cluster_num
                         elif min_distance > distance:
                              min_distance = distance
                              cluster = cluster_num
                    pixel_cluster[i][j] = cluster
                    cluster_count[cluster]+=1
                    new_tuple = avg_clusters[cluster]
                    r = new_tuple[0] + pixels[i,j][0]
                    g = new_tuple[1] + pixels[i,j][1]
                    b = new_tuple[2] + pixels[i,j][2]
                    avg_clusters[cluster] = (r,g,b)
          
          #compute new center for each cluster using average
          change = False
          for i in range(5):
               if cluster_count[i]==0: continue
               new_center = avg_clusters[i]
               r = int(new_center[0]/cluster_count[i])
               g = int(new_center[1]/cluster_count[i])
               b = int(new_center[2]/cluster_count[i])
               if abs(centers[i][0]-r)>1 or abs(centers[i][1]-g)>1 or abs(centers[i][2]-b)>1:
                    change = True
                    
               centers[i] = (r,g,b)
          print(centers)

#Find the six most similar 3x3 grayscale pixel patches in the training data (left half of the black and whiteimage).
def find_six_closest(patch):
     closest_values = [-1]*6
     six_closest = [-1]*6
     for i in range(1, int(width/2)-1,3):
          for j in range(1, height-1,3):
               left_patch = patch_data[i][j]
               dist = 0
               for _ in range(9):
                    dist += (patch[_]-left_patch[_])**2
               # dist = np.linalg.norm(patch-left_patch) 
               
               replace = -1
               difference = -1
               for _ in range(6):
                    if six_closest[_] == -1:
                         six_closest[_] = dist
                         closest_values[_] = (i,j)
                         break
                    elif six_closest[_] > dist and six_closest[_]-dist > difference:
                         difference = six_closest[_]-dist
                         replace = _
               six_closest[replace] = dist
               closest_values[replace] = (i,j)
     
     return closest_values, six_closest

if __name__ == '__main__':
     setup()
     clustering()
     
     #For each pixel in the left half of the color image, replace the true color with the nearest representative color from the clustering.
     for i in range(int(width/2)):
          for j in range(height):
               pixels[i,j] = centers[pixel_cluster[i][j]]
               final_pixels[i,j] = centers[pixel_cluster[i][j]]

     #For each 3x3 grayscale pixel patch in the test data (right half of the black and white image)
     cached_similar = {}
     for i in range(int(width/2),width-1):
          for j in range(1, height-1):
               patch = patch_data[i][j]

               #CACHING THE WHOLE 9 PATCH DATA
               # try:
               #      similar_coordinates = cached_similar[patch.tobytes()][0]
               #      distances= cached_similar[patch.tobytes()][1]
               # except KeyError:
               similar_coordinates, distances = find_six_closest(patch)
               #      cached_similar[patch.tobytes()] = (similar_coordinates,distances)

               #CACHING THE SINGULAR GRAY PIXEL
               # try:
               #      similar_coordinates = cached_similar[gray_pixels[i,j][0]][0]
               #      distances= cached_similar[gray_pixels[i,j][0]][1]
               # except KeyError:
               #      similar_coordinates, distances = find_six_closest(patch)
               #      cached_similar[gray_pixels[i,j][0]] = (similar_coordinates,distances)
               # print(similar_coordinates, (i,j))
               
               patch_colors = list()
               for _ in range(6):
                    x = similar_coordinates[_][0]
                    y = similar_coordinates[_][1]
                    patch_colors.append(pixel_cluster[x][y])
               
               new_color = -1
               mode = -1
               multiple_colors = list()
               for c in Counter(patch_colors).most_common():
                    if new_color == -1:
                         new_color = c[0]
                         mode = c[1]
                         multiple_colors.append(c[0])
                    elif mode == c[1]:
                         new_color = -2
                         multiple_colors.append(c[0])
               
               #Find the closest distance to copy color
               if new_color == -2:
                    most_similar = 500
                    for _ in range(6):
                         if most_similar > distances[_] and patch_colors[_] in multiple_colors:
                              new_color = patch_colors[_]
                              most_similar = distances[_]
                    gray_pixels[i,j] = centers[new_color]
                    final_pixels[i,j] = centers[new_color]
               else:
                    gray_pixels[i,j] = centers[new_color]
                    final_pixels[i,j] = centers[new_color]
                         
     img.show()
     gray_img.show()

     final_img.show()
