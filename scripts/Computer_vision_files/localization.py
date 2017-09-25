import time
import cv2
import cv2.aruco as aruco
import numpy as np
from time import time
from time import sleep
import math 
import scipy.io as sio




def read_Tc2r():
    test=sio.loadmat('Tc2rtheo.mat')
    Tc2r=test.get('Tc2rtheo')
    return Tc2r

def load_camera_params():
	data = np.load('camera_parameters.npz')
	mtx=data["cam_matrix"]
	dist=data["dist_coeff"]
	return mtx,dist
# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R) :
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype = R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6
 
 
# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R) :
 
    assert(isRotationMatrix(R))
     
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
     
    singular = sy < 1e-6
 
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
 
    return np.array([x, y, z])
def locate_markers_robot(ids,rvec,tvec,marker_list=[1,2,3,4,5],T=np.ones((4,4))):
	rotc2r=T[0:3,0:3]
	transl=tvec
	located_matrix=0*np.ones((len(marker_list),2))

	if len(transl.shape)==3:
		
		for i,value in enumerate(ids):
			p2c=np.concatenate((tvec[i].T,np.array([[1]])),axis=0)
			p2r=T.dot(p2c)
			x=p2r[0,0]
			y=p2r[1,0]
			d=np.sqrt(np.power(x,2)+np.power(y,2))
			theta=np.arctan2(y,x)
			gamma=rvec[i,0,2]
			index_mat=marker_list.index(value)
			located_matrix[index_mat,:]=[d,theta]
	return located_matrix


def get_marker_pose(frame,mtx,dist,arucoParams,marker_list=[1,2,3,4,5]):
	Tc2rtheo=read_Tc2r()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
	corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=arucoParams) # Detect aruco
	if ids != None: # if aruco marker detected
		rvec, tvec = aruco.estimatePoseSingleMarkers(corners, markerLength, mtx, dist) # For a single marker
		for i in range(len(ids)):
			frame = aruco.drawAxis(frame, mtx, dist, rvec[i], tvec[i], 15)
		located_matrix=locate_markers_robot(ids,rvec,tvec,T=Tc2rtheo)  
	else:
		located_matrix=999*np.ones((len(marker_list),2))
	return frame,located_matrix

# Setting dictionary 
aruco_dict = aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

#loading camera parameters
mtx,dist=load_camera_params()





##that should be in the main 

cap = cv2.VideoCapture(0)

# SET the parametes of the markers also marker list
arucoParams = aruco.DetectorParameters_create()
markerLength = 3.5 

while True:
    ret,img=cap.read()
    
    imgwithAruco,located_matrix=get_marker_pose(img,mtx,dist,arucoParams)
    print(located_matrix)
    sleep(0.05)
    cv2.imshow("aruco", imgwithAruco)   # display
    if cv2.waitKey(50) & 0xFF == ord('q'):   # if 'q' is pressed, quit.
        break