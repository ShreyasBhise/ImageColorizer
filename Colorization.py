#python3 -m pip install --upgrade Pillow
from PIL import Image
import random, math
from collections import Counter

img = Image.open('image.jpg')
width = img.size[0]
height = img.size[1]
pixels = img.load()

for i in range((int)(width/2), width-1):
     for j in range(height):
          p = pixels[i,j]
          gray = int(0.21*p[0] + 0.72*p[1] + 0.07*p[2])
          pixels[i,j] = (gray, gray, gray)


#5-means clustering for left side of the image to get 5 major colors to use

#randomly assign 5 inital centers
centers = list()
for _ in range(5):
     r = random.randint(0,255)
     g = random.randint(0,255)
     b = random.randint(0,255)
     centers.append((r,g,b))
print(centers)


#repeat until centers do not change
change = True
pixel_cluster = list()

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
               min_distance = 500
               for cluster_num in range(5):
                    center = centers[cluster_num]
                    c_r = center[0]
                    c_g = center[1]
                    c_b = center[2]
                    distance = math.sqrt( (p[0]-c_r)**2 + (p[1]-c_g)**2 + (p[2]-c_b)**2 )
                    if min_distance > distance:
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

#For each pixel in the left half of the color image, replace the true color with the nearest representative color from the clustering.
for i in range(int(width/2)):
     for j in range(height):
          pixels[i,j] = centers[pixel_cluster[i][j]]
img.show()