import numpy as np
#from ev3control import Robot
from detection.opencv import get_lego_boxes
from detection.opencv import detection_lego_outside_white
from detection.opencv import get_brown_box
from detection.opencv import get_purple_lego
import time
import cv2

#robot to camera 29 cm

def cam2rob(pos, H):

	####cam [[[ 270.03048706  448.53890991]]]

	pixel_size =  0.653947100514

	# CENTER OF THE CAMERA
	cam= np.array([242.54,474.87])
	cam2rob_dist = 25

	Lego_list = []
	for i in range(0,1):

		y = pos[0]
		x = pos[1]
		print('X y Y : ', x,' ',y)

		output_vector=np.array([[[y,x]]],dtype=np.float32)
		print("dentro del cam2rob",output_vector)
		#output_vector=cv2.perspectiveTransform(input_vector,np.linalg.inv(H))
		
		#distance_x =  (-output_vector[0,0,1]+cam[1])*pixel_size +cam2rob_dist
		distance_x = -0.28*output_vector[0,0,1] +160 
		#distance_y = -(output_vector[0,0,0] - cam[0])*pixel_size 
		distance_y =  -(output_vector[0,0,0] - cam[0]) *(0.0063*distance_x)

		print("data: ", distance_x,distance_y)

		angle = np.arctan2(distance_y,distance_x)
		
		distance = np.sqrt(np.power(distance_x,2) + np.power(distance_y,2))
	return 1

def load_camera_params():
    data = np.load('camera_parameters.npz')
    mtx=data["cam_matrix"]
    dist=data["dist_coeff"]
    return mtx,dist


data = np.load('Homographygood.npz')
H=data["arr_0"]
print(H)
data2=np.load('newcameramtx.npz')
newcameramtx=data2["arr_0"]
print(newcameramtx)
mtx,dist=load_camera_params()
print("mtx",mtx)
print("dist",dist)
mtx=np.array(mtx)
dist=np.array(dist)

cap = cv2.VideoCapture(1)
while True:
	ret,frame=cap.read()
	cv2.imshow("frame",frame)
	dst = cv2.warpPerspective(frame,H,(640,480),flags= cv2.INTER_LINEAR+cv2.WARP_FILL_OUTLIERS+cv2.WARP_INVERSE_MAP)
	BB_legos=get_lego_boxes(dst)
	#print(BB_legos)

	#for box in BB_legos:
	#	cv2.rectangle(frame,(box[0],box[1]),(box[2],box[3]),(0,255,0))

	#print(dst.shape)
	
	input_vector=np.array([[[320,400]]],dtype=np.float32)
	print(input_vector.shape)
	cv2.circle(frame,(input_vector[0,0,0],input_vector[0,0,1]),3,(0,255,0),3)
	h=H[0:3,0:3]
	#input_vector=np.array([input_vector])
	output_vector=cv2.perspectiveTransform(input_vector,np.linalg.inv(H))
	#print("input vector : ",input_vector)
	#print("outpt vect: ",output_vector)


	# CENTER OF THE CAMERA
	input_vector_cam_pos=np.array([[[320,480]]],dtype=np.float32)
	cv2.circle(frame,(320,480),3,(0,255,0),3)
	cv2.imshow("frame",frame)

	cam=cv2.perspectiveTransform(input_vector_cam_pos,np.linalg.inv(H))

	print("CAM POS:",cam)
	cv2.circle(dst,(cam[0,0,0],cam[0,0,1]),3,(255,0,0),3)
	#print("cam", cam)
	cv2.imshow("dst",dst)
	


	# Compute the distance and angle from the center

	distance = np.sqrt(np.power(output_vector[0,0,0]-cam[0,0,0],2) + np.power(output_vector[0,0,1]-cam[0,0,1],2))
	angle = np.arctan2(output_vector[0,0,1]-cam[0,0,1], output_vector[0,0,0]-cam[0,0,0])

	# En principio si recibo una lista con (angle, distance) me es suficiente en plan Lego_list = [[angle1,d1],[angle2,d2]]
	landmarks=np.array([[320,480],[320,400]])
	#land_rob=cam2rob(landmarks, H)
	print("LANDMARKS FROM CAM",landmarks)
	#print("LAND_ROBOTS",land_rob)


	cv2.circle(dst,(output_vector[0,0,0],output_vector[0,0,1]),3,(255,0,0),3)
	#print(output_vector[0,0,0],output_vector[0,0,1])

	cv2.imshow("dst",dst)



	## GET DISTANCE OF PIXELS
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

	ret, corners = cv2.findChessboardCorners(gray, (9,6),None, 1 | 4)

	#print("corners: ",corners)
	imgPts = 2.5*np.ones([4,2])

	board_w = 10;
	board_h = 7;

	if(isinstance(corners, np.ndarray)):

		imgPts[0,:] = corners[0,:];
		imgPts[1,:] = corners[board_w-2,:];
		imgPts[2,:] = corners[(board_h-2)*(board_w-1),:];
		imgPts[3,:] = corners[(board_h-2)*(board_w-1) + board_w-2-6,:];

		input_vector=np.array([[[imgPts[0,0],imgPts[0,1]]]],dtype=np.float32)
		print('img:', imgPts[0,0], imgPts[0,1])
		cv2.circle(frame,(input_vector[0,0,0],input_vector[0,0,1]),3,(255,0,0),3)

		cv2.imshow("frame",frame)




		saved_output = np.ones([4,2])
		for i in range(0,4):

			input_vector=np.array([[[imgPts[i,0],imgPts[i,1]]]],dtype=np.float32)


			output_vector=cv2.perspectiveTransform(input_vector,np.linalg.inv(H))

			if i==2:
				
				
				cv2.circle(dst,(output_vector[0,0,0],output_vector[0,0,1]),3,(255,0,0),3)

			saved_output[i,:] = output_vector[0,0,:]
		

			cv2.imshow("dst",dst)

		pixel_distance = np.ones([4])
		pixel_distance[0] = saved_output[1,0] - saved_output[0,0]
		pixel_distance[1] = saved_output[1,1] - saved_output[0,1]

		T = cam2rob(saved_output[1,:] , H)
		print("Y:", saved_output[1,1]," X:", saved_output[1,0])
		#print("Y2:",saved_output[1,1],"X2:", saved_output[1,0])

		print('HOLAAAAA',saved_output[0,:])
		print('HOLAAA1',saved_output[0,1])
		
		print("horizontal number of pixels",saved_output[3,0]-saved_output[2,0])
		


		pixel_size = 20/np.sqrt(np.power(pixel_distance[0],2)+np.power(pixel_distance[1],2))
		#print("pixel size: ",pixel_size)
		pixel_distance[2] = saved_output[2,0] - saved_output[0,0]
		pixel_distance[3] = saved_output[2,1] - saved_output[0,1]

		dist = pixel_size * np.sqrt(np.power(pixel_distance[2],2)+np.power(pixel_distance[3],2))
		print(pixel_size)
		#print("estimated measure : ", dist)
		
		'''cv2.line(topview, (0,400), (640,400), (0,255,0))
		cv2.line(topview, (240,0), (240,480), (0,0,255))
		cv2.line(topview, (280,0), (280,480), (0,0,255))
		cv2.line(topview, (200,0), (200,480), (0,0,255))
		cv2.line(topview, (220,0), (220,480), (0,0,255))
		cv2.line(topview, (300,0), (300,480), (0,0,255))
		cv2.line(topview, (260,0), (260,480), (0,0,255))
		'''
		
		#print("y: ", pixel_distance[0], " x : ", pixel_distance[1], "other y: ", pixel_distance[2] , "other x: ", pixel_distance[3])

	if cv2.waitKey(1) & 0xFF == 27:
			break