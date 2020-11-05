#import nazca and custom path-based class

import nazca as nd
from dha_elements_v01 import dha

# instantiate dha object, and set some parameters:
# layer refers to layer in which central waveguide will be placed, width is initial width used. 
# this will be changed automatically when tapers are used.
# owidth refers to the width of the outline paths, which are played in olayer

path_structure = dha(name='path_structure_1', layer=1, width=0.5, owidth=5, olayer=2) 

# we can then define some structures using the methods in the dha object:

path_structure.strt(length=20)
path_structure.arc(angle=90, radius=20)
path_structure.eulerbend(p=0.2,angle=-90, radius=20) 
path_structure.taper(width1=0.5, width2=5, length=50)
path_structure.strt(length=10)
path_structure.taper(width1=5,width2=0.5, length=20)

# to place the structure, get the cell with the getcell() method, then place that using the cells put() method
# cells can also be place multiple places with specified position

cell = path_structure.getcell()
cell.put()
cell.put(0,-50)

#export to GDS
nd.export_gds(filename='dha_elements_usage_example_1.gds')

# for repeated structures with varying parameters, it is maybe better to define the cell in a function:

def parametrized_cell(w1, w2, bend_radius, length1, length2, trenchwidth=5):
        name = 'parametrized cell with taper lenght = ' + str(length2)
        p = dha(name=name, layer=1, olayer=2, width=w1, owidth=trenchwidth)
        p.strt(length=length1)
        p.taper(width1=w1, width2=w2, length=length2)
        p.eulerbend(radius=bend_radius, angle=90)
        p.taper(width1=w2, width2=w1, length=length2) 
        p.strt(length=length1)
        cell = p.getcell()
        return cell

# the cells can then be created in a loop where some parameter is varied:

taper_lengths=[10, 50, 100, 150]
y_step = 50
y_start = 0
for i in range(len(taper_lengths)):
    cell = parametrized_cell(w1=0.5,w2=5,bend_radius=20, length1=10, length2=taper_lengths[i])
    cell.put(0,y_start+y_step*i+sum(taper_lengths[:i]))

nd.export_gds(filename='dha_elements_usage_example_2.gds')
