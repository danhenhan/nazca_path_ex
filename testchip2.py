import nazca as nd
from dha_elements_v01 import dha
import matplotlib.pyplot as plt
import numpy as np

#global design settings

w_bias = 0.030*2   # writing pocess takes away 30nm on both sides 
w_trench = 2.5       
w_SM = 0.3 + w_bias        
chip_width = 12000
chip_height = 10000
N_repeats = 2
L_io = 1000

# make a grid indicating frames for raster mode


gridline_x = nd.Polyline(points=[[0,0],[12000,0]], layer=3, width=1)
gridline_y = nd.Polyline(points=[[0,0],[6000,0]], layer=3, width=1)


for y in range(-1500,4501,500):
    gridline_x.put(0,y)
for x in range(0,12001,500):
    gridline_y.put(x,-1500,90)


# First section, straight - taper out - straight - taper in straight - taper to output 
y1 = 50
layer_inner = 1
layer_trench = 11
W_straight = np.array([0.05, 0.1, 0.2, 0.3, 0.3, 0.5, 0.8]) + w_bias
W_taper = np.array([5, 5, 5, 2, 5, 5, 5]) + w_bias
L_t = np.array([50, 50, 100, 10, 50, 50, 50])
L_str = 2000
L_t_out = 10 
W_t_out = 2 + w_bias



for i in range(len(W_straight)):
    for j in range(N_repeats):    
        path = dha(name='taper_test_p1'+str(i)+str(j), layer = layer_inner, olayer = layer_trench, width=W_straight[i], owidth=w_trench)
        path.strt(length = chip_width/2 - L_t[i] - L_str/2, N=2)
        path.taper(width1 = W_straight[i], width2 = W_taper[i], length=L_t[i])
        path.strt(length = L_str/2, N=2)
        path.getcell().put(0,y1)
    ##split path in middle    
        path = dha(name='taper_test_p2 asd'+str(i)+str(j), layer = layer_inner, olayer = layer_trench, width=W_taper[i], owidth=w_trench)
        path.strt(length = L_str/2, N=2)
        path.taper(width1 = W_taper[i], width2=W_straight[i], length=L_t[i])
        path.strt(length=chip_width/2 - L_t[i] - L_str/2 - L_t_out - L_io, N=2)
        path.taper(width1=W_straight[i], width2=W_t_out, length=L_t_out)
        path.strt(length=L_io, N=2)
        path.getcell().put()
        y1 += 20


#---------
# make section 2: test of bend radius. using Euler bends with p_parameter=0.2, .3µm
y2 = 550
R_bend = np.array([3.5, 5, 10, 25])
L_in = 3000
L_out = 3000
L_mid = chip_width - L_in - L_out
L_uturn = R_bend*4
L_t_out = 10
W_in = w_SM
W_out = 2 + w_bias
N_bends = 5


for i in range(len(R_bend)):
    for j in range(N_repeats):
        in_section = dha(name='Euler bends: insec', layer=1, olayer=12, width = W_in, owidth=w_trench)
        bend_section = dha(name='Euler bends bendsec', layer=1, olayer=12, width = W_in, owidth=w_trench)
        out_section = dha(name='Euler bends outsec', layer=1, olayer=12, width = W_in, owidth=w_trench)
        
        in_section.strt(length=L_in,N=2)
                
        L_str = (L_mid - N_bends*L_uturn[i])/(N_bends*2)
        for k in range(N_bends):
            bend_section.strt(length=L_str,N=2)
            bend_section.eulerbend(p=0.2, radius=R_bend[i], angle=90)
            bend_section.eulerbend(p=0.2, radius=R_bend[i], angle=-180)
            bend_section.eulerbend(p=0.2, radius=R_bend[i], angle=90)
            bend_section.strt(length=L_str,N=2)
        
        out_section.strt(length=L_out - L_t_out - L_io)
        out_section.taper(width1 = W_in, width2 = W_out, length=L_t_out, N=2)
        out_section.strt(length=L_io, N=2)
        
        in_section.getcell().put(0,y2)
        bend_section.getcell().put()
        out_section.getcell().put()

        y2 += 20 + 2*R_bend[i]            


#--------
# make section 3, crossing test

nd.add_layer2xsection(xsection='xs1', layer=21, accuracy = 0.0001)
nd.add_layer2xsection(xsection='xs1', layer=22, accuracy = 0.0001, growx=w_trench)
ic1 = nd.interconnects.Interconnect(width=w_SM)

def crossing(angle, w_cross, L):
    with nd.Cell('y_junction') as crossing:
        s1 = ic1.strt(width=w_cross, length=L/2,xs='xs1').put()
        s2 = ic1.strt(width=w_cross, length=L/2,xs='xs1').put()
        a1 = ic1.strt(width=w_cross, length=100,xs='xs1').put(s2.pin['a0'].move(0,0,angle))
        a2 = ic1.strt(width=w_cross, length=100,xs='xs1').put(s2.pin['a0'].move(0,0,angle), flop=True)

        nd.Pin(name='a0').put(s1.pin['a0'])
        nd.Pin(name='a1').put(a1.pin['a0'])
        nd.Pin(name='b0').put(s2.pin['b0'])
        nd.Pin(name='b1').put(a2.pin['b0'])
    return crossing

y3 = 1250
W_cross = 2 + w_bias
L_cross = 80
L_s = 10
L_ovl = 5
D_cross = 500
L_t = 10
L_in = 4250
L_out = 3000
W_out = 2 + w_bias
angles = np.array([15, 30, 45, 60, 90])

def Crossings(taper_left = False):
    with nd.Cell(name='crossings') as cr:
        in_section = dha(name='crossing test, input', layer=1, olayer=13, width=w_SM, owidth=w_trench)
        connector = dha(name='crossing test, conn', layer=1, olayer=13, width=W_cross, owidth=w_trench)
        out_section = dha(name='crossing test, output', layer=1, olayer=13, width=W_cross, owidth=w_trench)
        if taper_left == False:
            in_section.strt(length=L_in-70+1000)
            in_section.taper(length=L_t, width1=w_SM, width2=W_cross)
            in_section.strt(length=L_s+L_ovl)
            a = in_section.getcell().put(0,0)
        else:
            in_section = dha(name='crossing test, input', layer=1, olayer=13, width=W_t_out, owidth=w_trench)
            in_section.strt(length=L_io)
            in_section.taper(width2=w_SM,length=L_t_out)
            in_section.strt(L_in-75)
            in_section.taper(L_t, width2=W_t_out)
            in_section.strt(10)
            a = in_section.getcell().put(0,0)

        connector.strt(length=L_s+L_ovl)
        connector.taper(width1=W_cross,width2=w_SM,length=L_t)
        connector.strt(length=D_cross-(2*L_t+2*L_s+L_cross))
        connector.taper(width2=W_cross,width1=w_SM,length=L_t)
        connector.strt(length=L_s+L_ovl)
        con = connector.getcell()

        if taper_left == False:
            out_section.strt(10)
            out_section.taper(width2=w_SM, length=L_t)
            out_section.strt(L_in-555)
            out_section.taper(width2=W_out,length=L_t)
            out_section.strt(L_io)
            out = out_section.getcell()
        else:
            out_section.strt(10)
            out_section.taper(width2=w_SM, length=L_t)
            out_section.strt(L_in-545+1000)
            out = out_section.getcell()

        for j in range(len(angles)-1):
    #    bend
            b = crossing(angles[j], W_cross, L_cross).put(a.pin['b0'].move(-L_ovl))
            a = con.put(b.pin['b0'].move(-L_ovl))   

        crossing(angles[-1], W_cross, L_cross).put(a.pin['b0'].move(-L_ovl))
        out.put(nd.cp.move(-L_ovl))
    return cr
Crossings().put(0,y3)
Crossings(taper_left=True).put(0,y3+500)

# -----------------------------
# make last section, y_splitters



def y_junction(radius=10, width=w_SM, angle=45, height=50,layer=1111, olayer=1112, p=0.2):
    with nd.Cell() as eb:

        a = dha(name='poly_yj1',layer=layer, olayer=olayer,width=W_out, owidth=w_trench, return_path=False)
        b = dha(name='poly_yj2',layer=layer, olayer=olayer,width=w_SM, owidth=w_trench, return_path=False)
        c = dha(name='poly_yj3',layer=layer, olayer=olayer,width=w_SM, owidth=w_trench, return_path=False)
        d = dha(name='poly_yj4',layer=layer, olayer=olayer,width=w_SM, owidth=w_trench, return_path=False)
        #input section
        a.strt(5) 
        a.taper(width2=w_SM, length=10)
        a.strt(5)

        a = a.getcell()
        #bend
        b.strt(1)
        b.eulerbend(radius=radius,angle=angle, p=p,N=40)
        b.strt(1)
        b_height = b.end[1] - b.start[1]
        l = np.sqrt(2)*(height/2 - 2*b_height)+1
        b = b.getcell()
        #diagonals
        c.strt(l)
        c = c.getcell()
        #output
        d.strt(5)
        d.taper(width2=W_out, length=10)
        d.strt(5)
        d = d.getcell()


        a0 = a.put()
        b.put(a0.pin['b0'].move(-1))
        c.put()
        b0 = b.put(flip=True)
        d0 = d.put()

        b.put(a0.pin['b0'].move(-1),flip=True)
        c.put()
        b.put(flip=False)
        d1 = d.put()

        nd.Pin(name='a0').put(a0.pin['a0'])
        nd.Pin(name='b0').put(d0.pin['b0'])
        nd.Pin(name='b1').put(d1.pin['b0'])
    return eb
y4 = 2250

layer_inner_poly = 31
layer_outer_poly = 32
layer_outer_path = 14
layer_inner_path = 1

def split1_2_4_8(taper_in = True):
    with nd.Cell(name='Yjunction_taper_in') as yj:



        a = dha(name='y_junction_taper_input',layer=layer_inner_path, olayer=layer_outer_path,width=W_t_out, owidth=w_trench, return_path=True)
        b = dha(name='y_junction_connector',layer=layer_inner_path, olayer=layer_outer_path,width=W_t_out, owidth=w_trench, return_path=True)
        c = dha(name='y_junction_connector',layer=layer_inner_path, olayer=layer_outer_path,width=W_t_out, owidth=w_trench, return_path=True)
        if taper_in == True:
            a.strt(1000)
            a.taper(width2=w_SM)
            a.strt(700)
            a.taper(width2=W_out, length=10)
            a.strt(length=10)
            a.getcell().put(0,0)
        else:
            a = dha(name='y_junction_taper_input',layer=layer_inner_path, olayer=layer_outer_path,width=W_t_out, owidth=w_trench, return_path=False)
            a.strt(1710)
            a.taper(width2=W_out, length=10)
            a.strt(length=10)
            a.getcell().put(0,0)

        b.strt()
        b.taper(width2=w_SM,length=10)
        b.strt(375)
        b.taper(width2=W_t_out)
        b.strt()
        b = b.getcell()

        c.strt(100)
        c = c.getcell()


        y0 = y_junction(layer=layer_inner_poly, olayer=layer_outer_poly, height=100).put(nd.cp.move(-5))
        s0_0 = b.put(y0.pin['b0'].move(-5))
        s0_1 = b.put(y0.pin['b1'].move(-5))
        y1_0 = y_junction(layer=layer_inner_poly, olayer=layer_outer_poly,height=50).put(s0_0.pin['b0'].move(-5))
        y1_1 = y_junction(layer=layer_inner_poly, olayer=layer_outer_poly,height=50).put(s0_1.pin['b0'].move(-5))
        s1_0 = b.put(y1_0.pin['b0'].move(-5))
        s1_1 = b.put(y1_0.pin['b1'].move(-5))
        s1_2 = b.put(y1_1.pin['b0'].move(-5))
        s1_3 = b.put(y1_1.pin['b1'].move(-5))

        y=[]
        y.append(y_junction(layer=layer_inner_poly, olayer=layer_outer_poly,height=25).put(s1_0.pin['b0'].move(-5)))
        y.append(y_junction(layer=layer_inner_poly, olayer=layer_outer_poly,height=25).put(s1_1.pin['b0'].move(-5)))
        y.append(y_junction(layer=layer_inner_poly, olayer=layer_outer_poly,height=25).put(s1_2.pin['b0'].move(-5)))
        y.append(y_junction(layer=layer_inner_poly, olayer=layer_outer_poly,height=25).put(s1_3.pin['b0'].move(-5)))

        for i in range(len(y)):
            nd.Pin(name='b'+str(2*i)).put(y[i].pin['b0'].move(-5))
            nd.Pin(name='b'+str(2*i+1)).put(y[i].pin['b1'].move(-5))
    return yj

a = dha(name='y_junction_taper_input',layer=layer_inner_path, olayer=layer_outer_path,width=W_t_out, owidth=w_trench, return_path=True)
a.strt(length=10)
a.taper(width2=w_SM,length=10)
a.strt(length=6425)
a.taper(width2=W_out,length=10)
a.strt(length=10)
a = a.getcell()

yj = split1_2_4_8().put(0,y4)

a.put(yj.pin['b0'])
a.put(yj.pin['b1'])
a.put(yj.pin['b2'])
a.put(yj.pin['b3'])
a.put(yj.pin['b4'])
a.put(yj.pin['b5'])
a.put(yj.pin['b6'])
a.put(yj.pin['b7'])

split1_2_4_8(taper_in=False).put(12000,y4, flop=True)

y4 += 500
yj = split1_2_4_8(taper_in= False).put(0,y4)

a.put(yj.pin['b0'])
a.put(yj.pin['b1'])
a.put(yj.pin['b2'])
a.put(yj.pin['b3'])
a.put(yj.pin['b4'])
a.put(yj.pin['b5'])
a.put(yj.pin['b6'])
a.put(yj.pin['b7'])

split1_2_4_8(taper_in= True).put(12000,y4, flop=True)


nd.export_gds(filename='testchip2.gds', flat=True)
