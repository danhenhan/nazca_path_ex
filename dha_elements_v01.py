import numpy as np 
import nazca as nd
import math 
import scipy.integrate as integrate



class dha:
	def __init__(self, name='dha_mask_oject', layer=1111, width=2, owidth=10, olayer=1110, return_path=True):
		self.points = []
		self.ww =[]
		self.layer = layer
		self.olayer = olayer
		self.width = width
		self.owidth = owidth
		self.name = name
		self.start = [0,0,180]
		self.end = [0,0,0]
		self.positive = True
		self.return_path = return_path


	def _plot(self):
		nd.Polyline(points=self.points, width=self.width,olayer=self.olayer, layer=self.layer).put()
		nd.export_gds()
		return

	def get_points(self):
		return self.points

	def getcell(self):
		with nd.Cell(name=self.name) as dha_cell:
			inpin = nd.Pin(name='a0').put(self.start[0],self.start[1],self.start[2])
			nd.Pin(name='b0').put(self.end[0],self.end[1],self.end[2])
			a,b = self.outline()
			
			if self.return_path == True:
				nd.Polygon(nd.util.polyline2polygon(xy=self.points, width=self.ww), layer=self.layer).put()
				nd.Polyline(width=self.owidth, points=a, layer=self.olayer).put(inpin.rotate(180))
				nd.Polyline(width=self.owidth, points=b, layer=self.olayer).put(inpin.rotate(180))
			else:
				nd.Polygon(nd.util.polyline2polygon(xy=self.points, width=self.ww), layer=self.layer).put()
				nd.Polygon(nd.util.polyline2polygon(xy=a, width=self.owidth),layer=self.olayer).put(inpin.rotate(180))
				nd.Polygon(nd.util.polyline2polygon(xy=b, width=self.owidth),layer=self.olayer).put(inpin.rotate(180))
				
		return dha_cell

	def _add_points(self, x=np.array([0]), y = np.array([0]),w = np.array([0]), angle=0.0):
			#transform and append a given set of points to path
		spos = self.end

		x_0 = spos[0]
		y_0 = spos[1]

		a  = 2*np.pi*spos[2]/360
		M_r = np.array([[np.cos(a), -np.sin(a)],[np.sin(a), np.cos(a)]])
		M = np.array([x,y]) 
		M = np.matmul(M_r, M)
		M = M+np.array([[x_0],[y_0]])
		p = M.transpose().tolist()
		w = w.tolist()

		for i in range(0,len(x)):
			self.points.append(p[i])
			self.ww.append(w[i])
		self.end = self.points[-1]+ [self.end[2] + angle]

		i=0
		while 1:
			if self.points[i] == self.points[i+1]:
				self.points.pop(i+1)
				self.ww.pop(i+1)
			else:
				i +=1
			if i >= len(self.points) - 2:
				break


	def arc(self, radius=10, angle = 90.0):
		s= np.sign(angle)
		angle = np.abs(angle)
		a = 2*math.pi*angle/360
		N = int(abs(angle))
		t = np.linspace(0,a,N,endpoint=True)
		
		x = radius*np.cos(t)
		y = radius*np.sin(t)
		x = x-x[0]
		y = y-y[0]
		
		a = -np.pi/2
		M_r = np.array([[np.cos(a), -np.sin(a)],[np.sin(a), np.cos(a)]])
		M = np.array([x,y]) 
		M = np.matmul(M_r, M)
		x = M[:][0]
		y = s*M[:][1]
	
		w = t*0+self.width   
		self._add_points(x,y,w=w, angle=s*angle)
		return 
	

	def strt(self, length = 10, N=2):
		t = np.linspace(0,1,N)
		x = t*length
		y = t*0
		w = t*0 + self.width  
		self._add_points(x, y, w=w)

	def sinebend(self, N=50, length=50, offset=20):
		t = np.linspace(0,1,N)
		x = length*t
		y = offset*(np.cos(t*np.pi)-1)
		w = t*0 + self.width  
		self._add_points(x,y,w=w)

	def eulerbend(self, p=0.2, radius=10, angle=90,N=None):
		def int_x(s,R_0):
			return np.cos(s**2/(2*R_0**2))
		def int_y(s,R_0):
			return np.sin(s**2/(2*R_0**2))
			
		def f(s,R_0):
			xp = np.array([])
			yp = np.array([])
			try:
				for i in range(len(s)):
					x = integrate.quad(int_x, 0, s[i], args=R_0)
					y = integrate.quad(int_y, 0, s[i], args=R_0)
					xp = np.append(xp,x[0])
					yp = np.append(yp,y[0])
				return xp, yp
			except:
				xp = integrate.quad(int_x, 0, s, args=R_0)
				yp = integrate.quad(int_y, 0, s, args=R_0)
				return xp[0], yp[0]
		if N==None:
			N = int(abs(angle))
		else:
			N = N
		ss = np.sign(angle)
		angle = abs(angle)
		a = angle*2*np.pi/360
		R_0 = 1/np.sqrt(2)  
		s_p = R_0*np.sqrt(p*a)
		R_p = R_0/np.sqrt(p*a)
		s_0 = 2*s_p + R_p*a*(1-p)
		x_p, y_p =  f(s_p,R_0)
		D_x = x_p - R_p*np.sin(p*a/2)
		D_y = y_p - R_p*(1-np.cos(p*a/2))
		
		s_1 = np.linspace(0  , s_p   , int(p*N+0.5))
		s_2 = np.linspace(s_p, s_0/2 , int((1-p)*N/2+0.5))

		x_1, y_1 = f(s_1,R_0)

		x_2 = R_p*np.sin((s_2-s_p)/R_p + p*a/2) + D_x
		x = np.append(x_1,x_2)
		y_2 = R_p*(1-np.cos((s_2-s_p)/R_p +p*a/2)) + D_y
		y = np.append(y_1,y_2)  

		scale = radius/(y[-1] + x[-1]/np.tan(a/2))

		M_ref = np.array([[np.cos(a),-np.sin(a)],[np.sin(a), np.cos(a)]])
		M = np.array([-x,y]) 

		M = np.matmul(M_ref, M)
		x_r = M[:][0]
		y_r = M[:][1]
		x_r = x_r - x_r[-1] + x[-1]
		y_r = y_r - y_r[-1] + y[-1]
		x = np.append(x,x_r[::-1])
		y = np.append(y,y_r[::-1])
		x = x*scale
		y = ss*y*scale
		w = x*0 + self.width  
		self._add_points(angle = ss*angle,w=w, x=x, y=y)
		return
	
	def outline(self):
		width_outer = self.owidth
		h = width_outer/2 + np.array(self.ww)/2
		lp = []
		mp = self.points
		up = []
		for i in range(len(mp)-1):
			dx = mp[i+1][0] - mp[i][0]
			dy = mp[i+1][1] - mp[i][1]
			l = np.sqrt(dx**2 + dy**2)
			cosa = dx/l 
			sina = dy/l
			x = -sina*h[i]+ mp[i][0] 
			y = cosa*h[i]+mp[i][1]
			up.append([x,y])
			x = sina*h[i]+ mp[i][0] 
			y = -cosa*h[i]+mp[i][1]
			lp.append([x,y])
			
		dx = mp[-1][0] - mp[-2][0]
		dy = mp[-1][1] - mp[-2][1]
		l = np.sqrt(dx**2 + dy**2)
		cosa = dx/l 
		sina = dy/l
		x = -sina*h[-1]+ mp[-1][0] 
		y = cosa*h[-1]+mp[-1][1]
		up.append([x,y])
		x = sina*h[-1]+ mp[-1][0] 
		y = -cosa*h[-1]+mp[-1][1]
		lp.append([x,y])

		return up, lp
	
	def split_if_longer(self, path, maxlen):
		length = 0
		out = []
		idx_start=0
		split = 0
		for i in range(len(path)-1):
			dx = path[i+1][0] - path[i][0]
			dy = path[i+1][1] - path[i][1]
			l = np.sqrt(dx**2 + dy**2)
			length = length + l
			if length >= maxlen:
				out.append(path[idx_start:i+1])
				idx_start = i
				length = 0
				split = 1
		if split == 1:
			if i - idx_start > 1:
				out.append(path[idx_start:])
		else:
			out.append(path)
		return out

	def taper(self, width1 = None, width2 = 1, length=10, N=2):
		if width1 == None:
			width1 = self.width
		t = np.linspace(0,1,N)
		x = t*length
		y = t*0
		w = width1 + (width2-width1)*t  
		self.width=width2
		self._add_points(x, y, w=w)
		return

