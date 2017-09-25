from rick.motion_control import euclidian_path_planning_control, euclidian_kalman
import numpy as np
import matplotlib.pyplot as plt

rob = [0,0,0]
real_rob_pos = [0,0,0]
path = np.ones([5,3])
itera = 0
R = []
R2 = []
plotc = 0
obj = [80,-200]
vel_wheels = np.array([0,0])

P = np.identity(3)

marker_map = np.array([[0,0,0],[50, 0 , 0],[100,0,0],[0,100,0],[100,100,0]])

camino = np.array([np.array(rob[0:2]),np.array(obj)])
print(camino)

while 1:


    Ts = 0.1

    #rob,vel_wheels,path = euclidian_path_planning_control(rob,obj, Ts, path=path,iteration = itera, odom_r = vel_wheels[0]*Ts , odom_l = vel_wheels[1]*Ts, P=P , marker_map = marker_map, marker_list = [])
    
    #KALMAN
    rob,vel_wheels,path, P, real_rob_pos = euclidian_kalman(rob,obj, Ts, path=path,iteration = itera, odom_r = vel_wheels[0]*Ts , odom_l = vel_wheels[1]*Ts, P=P ,
                                                             marker_map = marker_map, marker_list = [], real_bot= real_rob_pos)
    

    print("odometry: ", vel_wheels[0]*Ts, "  y ", vel_wheels[1]*Ts)
    print('robot_position: ',rob)
    print('wheels vel:', vel_wheels)
    print("Time last: ", itera*Ts)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    #print('path: ', path)
    itera = itera+1


    R.append(rob)
    R2.append(real_rob_pos)
    robot_pos = np.array(R)
    R22 = np.array(R2)

    if plotc>10:

        plt.figure(1)
        plt.plot(robot_pos[:,0],robot_pos[:,1])

        plt.plot(R22[:,0],R22[:,1])

        plt.plot(camino[:,0],camino[:,1])
        plt.axis([-100, 150, -100, 150])
        plt.show()
        plotc = 0

    plotc = plotc +1




