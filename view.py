# written by Mathias D. Kallick 2-23-2016
# lab # 3, defines a class that allows data to be represented in 3d.

import numpy as np
import math

class View:

	def __init__(self):
		self.reset()
	
	# reset method that just sets all of the variables back to their default values
	def reset(self):
		self.vrp = np.matrix([0.,.5,1.])
		self.vpn = np.matrix([0.,0.,-1.])
		self.vup = np.matrix([0.,1.,0.])
		self.u = np.matrix([-1.,0.,0.])
		self.extent = [1,1,1]
		self.screen = [400,400]
		self.offset = [20,20]
		self.build()

	# allows for easy setting of variables from external file
	def setVariables(self,vrp,vpn,vup,u,extent,screen,offset):
		self.vrp = np.copy(vrp)
		self.vpn = np.copy(vpn)
		self.vup = np.copy(vup)
		self.u = np.copy(u)
		self.extent = extent[:]
		self.screen = screen[:]
		self.offset = offset[:]
		self.build()
		
	# normalizes a 3-vector
	def normalize(self, vector):
		v0 = vector[:,0]
		v1 = vector[:,1]
		v2 = vector[:,2]
# 		print "v0: ",v0,"v1: ",v1,"v2: ",v2
		vNorm = np.matrix([v0,v1,v2])
		length = math.sqrt(v0*v0 + v1*v1 + v2*v2)
		
		vNorm[0] = v0/length
		vNorm[1] = v1/length
		vNorm[2] = v2/length
		
		return vNorm.T
		
# 		max = vector[(1,2,3),0].max()
# 		min = vector[(1,2,3),0].min()
# 		
# 		vector[(1,2,3),0] = (vector[(1,2,3),0]-min)/(max-min)
	
	# builds a rotation matrix for rotating the data about the origin
	def rotateVRC(self, vupAngle, uAngle):
		t1 = np.identity( 4, float )
		Rxyz0 = self.u.tolist()[0]
		Rxyz0.append(0)
		Rxyz1 = self.vup.tolist()[0]
		Rxyz1.append(0)
		Rxyz2 = self.vpn.tolist()[0]
		Rxyz2.append(0)
		Rxyz3 = [0, 0, 0, 1]
		Rxyz = np.matrix( [ Rxyz0,
							Rxyz1,
							Rxyz2,
							Rxyz3] ).astype(float)
		r1 = np.matrix( [[math.cos(vupAngle), 0.,math.sin(vupAngle) , 0.],
						 [0., 1., 0., 0.],
						 [-math.sin(vupAngle), 0., math.cos(vupAngle), 0.],
						 [0., 0., 0., 1.] ] )
		r2 = np.matrix( [[1., 0., 0., 0.],
						 [0., math.cos(uAngle), -math.sin(uAngle), 0.],
						 [0., math.sin(uAngle), math.cos(uAngle), 0.],
						 [0., 0., 0., 1.] ] )
		t2 = np.identity( 4, float )
		vrp0 = self.vrp.tolist()[0]
		vrp0.append(1)
		tvrc = np.matrix( [vrp0, Rxyz0, Rxyz1, Rxyz2] ).astype(float)
# 		print t2, "\n\n", Rxyz, "\n\n", Rxyz.T, "\n\n", r2, "\n\n", r1, "\n\n", Rxyz, "\n\n", t1, "\n\n", tvrc.T
		tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T
		self.vrp = np.matrix([[tvrc[0,0].tolist(),tvrc[0,1].tolist(),tvrc[0,2].tolist()]])
		self.u = np.matrix([[tvrc[1,0].tolist(),tvrc[1,1].tolist(),tvrc[1,2].tolist()]])
		self.vup = np.matrix([[tvrc[2,0].tolist(),tvrc[2,1].tolist(),tvrc[2,2].tolist()]])
		self.vpn = np.matrix([[tvrc[3,0].tolist(),tvrc[3,1].tolist(),tvrc[3,2].tolist()]])
# 		print "u: ", self.u
		self.u = self.normalize(self.u.A)
		self.vup = self.normalize(self.vup.A)
		self.vpn = self.normalize(self.vpn.A)
		return tvrc
		
	# builds a vtm from the information stored in the class
	def build(self):
		viewTranslationMatrix = vtm = np.identity( 4, float )
		Translation1 = t1 = np.matrix(  [[1., 0., 0., -self.vrp[0, 0]], # first translation matrix 
         					           	 [0., 1., 0., -self.vrp[0, 1]], # translates by the VRP.
                		  				 [0., 0., 1., -self.vrp[0, 2]],
                		  				 [0., 0., 0., 1.] ] )
		vtm = t1 * vtm
		
		TempUp = tu = np.cross(self.vup, self.vpn)
		TempViewUp = tvup = np.cross(self.vpn, tu)
		TempViewPlaneNormal = tvpn = np.array(self.vpn)
#  		print "tu: ", tu
# 		print "tvup: ", tvup
# 		print "tvpn: ", tvpn
		self.u = self.normalize(tu)
		self.vup = self.normalize(tvup)
		self.vpn = self.normalize(tvpn)
	
		Rotation1 = r1 = np.matrix( [[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
                   					 [ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
                  		  			 [ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
                  					 [ 0.0, 0.0, 0.0, 1.0 ] ] )

		vtm = r1 * vtm
		
		Translation2 = t2 = np.matrix(  [[1., 0., 0., (.5*self.extent[0])],
										 [0., 1., 0., (.5*self.extent[1])],
										 [0., 0., 1., 0.],
										 [0., 0., 0., 1.] ] )
		vtm = t2 * vtm
		Scale1 = s1 = np.matrix( [[(-self.screen[0]/self.extent[0]), 0., 0., 0.],
								  [0., (-self.screen[1]/self.extent[1]), 0., 0.],
								  [0., 0., (1.0/self.extent[2]), 0.],
								  [0., 0., 0., 1.] ] )
		vtm = s1 * vtm
		Translation3 = t3 = np.matrix(  [[1., 0., 0., (self.screen[0] + self.offset[0])],
										 [0., 1., 0., (self.screen[1] + self.offset[1])],
										 [0., 0., 1., 0.],
										 [0., 0., 0., 1.] ] )
		vtm = t3 * vtm
		return vtm
	
	# returns a copy of the current state of the view class
	def clone(self):
		viewClone = View()
		viewClone.vrp = np.copy(self.vrp)
		viewClone.vpn = np.copy(self.vpn)
		viewClone.vup = np.copy(self.vup)
		viewClone.u = np.copy(self.u)
		viewClone.extent = self.extent[:]
		viewClone.screen = self.screen[:]
		viewClone.offset = self.offset[:]
		return viewClone
		
if __name__ == "__main__":
	test = View()
	print test.build()
 	clone = test.clone()
 	print clone.build()