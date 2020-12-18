import numpy as np

def triTraj(wps, l):
    '''
    inputs : 
    -> wps, numpy array x|y

    return :
    -> wps_traj, traj_def
    '''
    wps_traj = np.array([wps[0, :]])
    traj_def = []
    for i in range(wps.shape[0]-2):

        phi1 = np.arctan2(wps[i+1, 1] - wps[i, 1], wps[i+1, 0] - wps[i, 0])
        phi2 = np.arctan2(wps[i+2, 1] - wps[i+1, 1], wps[i+2, 0] - wps[i+1, 0])
        
        wps_traj = np.vstack((wps_traj, wps[i+1, :] + np.array([l*np.cos(phi1), l*np.sin(phi1)])))
        traj_def.append(('line', 0))
        wps_traj = np.vstack((wps_traj, wps[i+1, :] + np.array([l*np.cos(phi2), l*np.sin(phi2)])))
        print(np.sign(phi2-phi1))
        traj_def.append(('arc', wps[i+1, 0], wps[i+1, 1], -phi1*180/np.pi, (phi1-phi2)*180/np.pi))

    return wps_traj, traj_def