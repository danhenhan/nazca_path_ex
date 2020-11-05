import nazca as nd
from dha_elements_v01 import dha
import matplotlib.pyplot as plt

w_trench = 5

nd.add_layer2xsection(xsection='xs1', layer=11, accuracy = 0.0001)
nd.add_layer2xsection(xsection='xs1', layer=12, accuracy = 0.0001, growx=w_trench)
ic1 = nd.interconnects.Interconnect(width=0.5)

def	yjunction(radius=20, angle=45):
	with nd.Cell('y_junction') as yj:
		b1 = ic1.bend(angle=angle, radius=radius,xs='xs1').put(0,0,0)
		b2 = ic1.bend(angle=-angle, radius=radius,xs='xs1').put(0,0,0)
		nd.Pin(name='a0').put(b1.pin['a0'])
		nd.Pin(name='b0').put(b1.pin['b0'])
		nd.Pin(name='b1').put(b2.pin['b0'])
	return yj

def	stts(w1=1,w2=0.3,w3=5, l1=2000,l2=1000,l3=4000,l4=1000,l5=2000, layer=1, olayer=2):
	with nd.Cell('straight_taper_straight') as sts:
		path = dha(layer=layer,olayer=olayer,width=w1, owidth=w_trench)
		path.strt(length=l1)
		path.taper(length=l2, width1=w1, width2=w2)
		path.strt(length= l3)
		path.taper(length=l4, width1=w2, width2=w3)
		path.strt(length=l5)
		path.getcell().put()
	return sts
	
def bendtest(L=10000,r1=200, r2=200, layer=1,l1=500, w1=0.5, w2=2,n=4,olayer=2):
	with nd.Cell('Bend_test') as bt:
		path = dha(layer=1, width=w1,olayer=olayer, owidth=w_trench)
		path.strt(length=l1/4)
		path.taper(length=l1, width1=w1, width2=w2)
		L = L-4*l1
		l = L/(2*n) - (r1+r2)
		for i in range(n):
			path.strt(length = l)
			path.arc(angle=90,radius=r1)
			path.arc(angle=-180,radius=r2)
			path.arc(angle=90,radius=r1)
			path.strt(length = l)
		
		path.taper(length=l1, width1=w2, width2=w1)
		path.strt(length=l1*(7/4))
		path.getcell().put()
		return bt
	
def eulbendtest(L=10000,r1=200, r2=200,l1=500, layer=1, w1=1, w2=0.5, p=0.2,n=4,olayer=2):
	with nd.Cell('Bend_test') as ebt:
		path = dha(layer=1, width=w1,olayer=olayer, owidth=w_trench)
		
		path.strt(length=l1/4)
		path.taper(length=l1, width1=w1, width2=w2)
		L = L-4*l1
		l = L/(2*n) - (r1+r2)
		for i in range(n):
			path.strt(length = l)
			path.eulerbend(angle=90,radius=r1,p=p)
			path.eulerbend(angle=-180,radius=r2,p=p)
			path.eulerbend(angle=90,radius=r1,p=p)
			path.strt(length = l)
		path.taper(length=l1, width1=w2, width2=w1)
		path.strt(length=l1*(7/4))
		path.getcell().put()
	return ebt
	
	
# define chip size rectangle 10mmx6mm
p = nd.geometries.frame(sizel=10002,sizeh=6002)
nd.Polygon(p, layer=22).put(0,0)
y = 6000

# Make straith taper straight section 1
widths = [0.8, 0.8, 0.5, 0.5, 0.3, 0.3, 0.25, 0.25, 0.15, 0.15]
for i in range(len(widths)):
	ypos = 5980-25*i
	stts(w1=1.5,w2=widths[i],w3=1.5).put(0,ypos)


y = 5500
# Make straight taper straight section 2

widths = [0.8, 0.8, 0.5, 0.5, 0.3, 0.3, 0.25, 0.25, 0.15, 0.15]
for i in range(len(widths)):
	ypos = 5700-20*i
	stts(w1=1,w2=widths[i],w3=1).put(0,ypos)
y = 5500
widths = [0.2,0.3,0.4,0.5,0.8,1,1.5,2,3,5,10,20]
for i in widths:
	straight = dha(name='Straight guides', layer=1, olayer=2, width=i, owidth=w_trench, maxlength=5000)
	straight.strt(length=10000)
	y-=20
	straight.getcell().put(0,y)



y=5000
r1 = [220,150,100,68,47,33,22,15]#,10,6.8]
for i in range(len(r1)):
	bendtest(r1=r1[i],r2=r1[i],w1=1,w2=0.5,n=4, L=10000).put(10000,y+i*20, flip=True, flop=True)
	#bendtest(r1=r1[i],r2=r1[i],w1=1,w2=0.5,n=2, L=5010).put(5010,y+i*20, flip=True, flop=True)
		
y=4250
r1.reverse()
for i in range(len(r1)):
	eulbendtest(r1=r1[i],r2=r1[i],w1=1,w2=0.5,n=4, L=10000).put(0,y+i*20)
	#eulbendtest(r1=r1[i],r2=r1[i],w1=1,w2=0.5,n=2, L=5010).put(4990,y+i*20)
	
y= 3000

w_1 = 0.5
w_2 = 2
t_len = 10


q = dha(layer=1,olayer=2,width=w_1,owidth=w_trench)
q.strt(length=1000)
q.taper(width1=w_1,width2=w_2)
q.strt(length=10)
pin = q.getcell().put(0,y)
ic1.strt(length=10, width=w_2).put(pin.pin['b0'].move(-5))
ic1.taper(length=t_len,width1=w_2, width2=w_1).put()
p = yjunction(radius=20).put()
ic1.strt(length=10).put()
ic1.bend(radius = 20, angle=-45).put()
y2 = yjunction().put()

ic1.strt(length=10).put(p.pin['b1'])
ic1.bend(radius = 20, angle=45).put()
y3 = yjunction().put()

ic1.bend(angle=-45,radius=20).put(y2.pin['b0'])
ic1.taper(width1=w_1,width2=w_2, length=t_len).put()
o1 = ic1.strt(length=5,width=w_2).put()

ic1.bend(angle=45,radius=20).put(y2.pin['b1'])
ic1.taper(width1=w_1,width2=w_2, length=t_len).put()
o2 = ic1.strt(length=5,width=w_2).put()


ic1.bend(angle=-45,radius=20).put(y3.pin['b0'])
ic1.taper(width1=w_1,width2=w_2, length=t_len).put()
o3 = ic1.strt(length=5,width=w_2).put()

ic1.bend(angle=45,radius=20).put(y3.pin['b1'])
ic1.taper(width1=w_1,width2=w_2, length=t_len).put()
o4 = ic1.strt(length=5,width=w_2).put()

taperdown = dha(name='taper down', layer=1, olayer=2, owidth=w_trench)
taperdown.strt(length=5)
taperdown.taper(length=t_len, width1 = w_2, width2=w_1)
taperdown.strt(length=100)
t = taperdown.getcell()
t.put(o1.pin['b0'].move(-5))
t.put(o2.pin['b0'].move(-5))
t.put(o3.pin['b0'].move(-5))
t.put(o4.pin['b0'].move(-5))

nd.export_gds(filename='testchip.gds')