import numpy as np
#from ev3control import Robot
from detection.opencv import get_lego_boxes
from detection.opencv import detection_lego_outside_white
from detection.opencv import get_brown_box
from detection.opencv import get_purple_lego
import time
import cv2

#robot to camera 29 cm

def cam2rob(landmarks, H):

	pixel_size =  0.653947100514
	# CENTER OF THE CAMERA
	input_vector_cam_pos=np.array([[[320,480]]],dtype=np.float32)
	
	cam=cv2.perspectiveTransform(input_vector_cam_pos,np.linalg.inv(H))

	#landmark_rob = np.array([landmarks.shape[0],2])
	#print("cam pos in torcida is",cam)
	input_vector_list=[]
	for i in range(landmarks.shape[0]):
		input_vector_list.append(landmarks[i,:])
	input_vector = np.expand_dims(np.array(input_vector_list,dtype=np.float32), axis=0)

	output_vector=cv2.perspectiveTransform(input_vector,np.linalg.inv(H))
	#print("Vector after transformation",output_vector)
	# Compute the distance and angle from the center

	#landmark_rob[1] = np.sqrt(np.power(output_vector[0,0,0]-cam[0,0,0],2) + np.power(output_vector[0,0,1]-cam[0,0,1],2))*pixel_size
	#landmark_rob[0] = np.arctan2(output_vector[0,0,1]-cam[0,0,1], output_vector[0,0,0]-cam[0,0,0])

	# En principio si recibo una lista con (angle, distance) me es suficiente en plan Lego_list = [[angle1,d1],[angle2,d2]]
	output_location=pixel_size*(output_vector[0,:,:]-cam[0,0,:])

	return output_location

def load_camera_params():
    data = np.load('camera_parameters.npz')
    mtx=data["cam_matrix"]
    dist=data["dist_coeff"]
    return mtx,dist


data = np.load('Homography.npz')
H=data["arr_0"]
print(H)

cap = cv2.VideoCapture(1)
while True:

	mtx, dist = load_camera_params()
	ret,frame=cap.read()
	cv2.imshow("frame",frame)

	h,  w = frame.shape[:2]
	newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
	frame = cv2.undistort(frame, mtx, dist, None, newcameramtx)

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
	land_rob=cam2rob(landmarks, H)
	print("LANDMARKS FROM CAM",landmarks)
	print("LAND_ROBOTS",land_rob)


	cv2.circle(dst,(output_vector[0,0,0],output_vector[0,0,1]),3,(255,0,0),3)
	#print(output_vector[0,0,0],output_vector[0,0,1])

	cv2.imshow("dst",dst)



	## GET DISTANCE OF PIXELS
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

	ret, corners = cv2.findChessboardCorners(gray, (9,6),None, 1 | 4)

	#print("corners: ",corners)
	imgPts = np.ones([4,2])

	board_w = 10;
	board_h = 7;

	if(isinstance(corners, np.ndarray)):

		imgPts[0,:] = corners[0,:];
		imgPts[1,:] = corners[board_w-2,:];
		imgPts[2,:] = corners[(board_h-2)*(board_w-1),:];
		imgPts[3,:] = corners[(board_h-2)*(board_w-1) + board_w-2,:];

		saved_output = np.ones([4,2])
		for i in range(0,4):

			input_vector=np.array([[[imgPts[i,0],imgPts[i,1]]]],dtype=np.float32)

			output_vector=cv2.perspectiveTransform(input_vector,np.linalg.inv(H))

			if i==0:
				cv2.circle(dst,(output_vector[0,0,0],output_vector[0,0,1]),3,(255,0,0),3)

			saved_output[i,:] = output_vector[0,0,:]
		

			cv2.imshow("dst",dst)

		pixel_distance = np.ones([4])
		pixel_distance[0] = saved_output[1,0] - saved_output[0,0]
		pixel_distance[1] = saved_output[1,1] - saved_output[0,1]

		print("Y:", saved_output[0,1]," X:", saved_output[0,0])

		distance_x = -0.35*saved_output[0,1] +200
		distance_y =  -(saved_output[0,0] - cam[0,0,0]) *0.35


		print("X:", distance_x , "  Y ditnce", distance_y)
		print("Y2:",saved_output[2,1])
		print("lateral distance: ", pixel_distance[0])

		pixel_size = 20/np.sqrt(np.power(pixel_distance[0],2)+np.power(pixel_distance[1],2))
		#print("pixel size: ",pixel_size)
		pixel_distance[2] = saved_output[2,0] - saved_output[0,0]
		pixel_distance[3] = saved_output[2,1] - saved_output[0,1]

		dist = pixel_size * np.sqrt(np.power(pixel_distance[2],2)+np.power(pixel_distance[3],2))
		print(pixel_size)
		#print("estimated measure : ", dist)

		#print("y: ", pixel_distance[0], " x : ", pixel_distance[1], "other y: ", pixel_distance[2] , "other x: ", pixel_distance[3])

	if cv2.waitKey(1) & 0xFF == 27:
			break