
from __future__ import division
import sys
sys.path.insert(0, "/Users/jkudlerflam/Desktop/pvtrace-master/")
import sqlite3
import numpy as np 
from pvtrace.external import transformations as tf
from pvtrace import *
import matplotlib.pyplot as plt

# 1) Define some sizes
L = 0.0005
H = 0.3

# 2) Create light source from AM1.5 data, truncate to 400 -- 800nm range
file = os.path.join(PVTDATA,'sources','AM1.5g-full.txt')
oriel = load_spectrum(file, xbins=np.arange(400,800))
source = PointSource(spectrum = oriel, center = (0*L,0.05,.5*H), phimin = 22/18.0 * np.pi, phimax = 32/18.0*np.pi, thetamin = 4/18.0 * np.pi, thetamax =   14/18.0 * np.pi)
#source = SimpleSource(position=[7*L,0.05,.5*H], direction=[np.sqrt(.0001),-np.sqrt(.1999),-np.sqrt(.8)], wavelength=555., use_random_polarisation=False)
#source.translate((0,.1,0.001))

# 3) Load dye absorption and emission data, and create material
file = os.path.join(PVTDATA, 'dyes', 'fluro-red.abs.txt')
abs = load_spectrum(file)
file = os.path.join(PVTDATA, 'dyes', 'fluro-red-fit.ems.txt')
ems = load_spectrum(file)
fluro_red = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.95, refractive_index=1.5)

# 4) Give the material a linear background absorption (pmma)
abs = Spectrum([0,1000], [2,2])
ems = Spectrum([0,1000], [0,0])
pmma = Material(absorption_data=abs, emission_data=ems, quantum_efficiency=0.0, refractive_index=1.5)

# 5) Make the LSC and give it both dye and pmma materials

lsc = Rod(radius = L, length = H)
lsc.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
lsc.name = "LSC"
lsc.shape.append_transform(tf.translation_matrix((0,0,0)))

#lsc2 = Rod(radius = L, length = H)
#lsc2.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc2.name = "LSC2"
#lsc2.shape.append_transform(tf.translation_matrix((2*L,0,0)))
#
#lsc3 = Rod(radius = L, length = H)
#lsc3.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc3.name = "LSC3"
#lsc3.shape.append_transform(tf.translation_matrix((4*L,0,0)))
#

#lsc4 = Rod(radius = L, length = H)
#lsc4.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc4.name = "LSC4"
#lsc4.shape.append_transform(tf.translation_matrix((6*L,0,0)))#
#
#lsc5 = Rod(radius = L, length = H)
#lsc5.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc5.name = "LSC5"
#lsc5.shape.append_transform(tf.translation_matrix((8*L,0,0)))
##
#lsc6 = Rod(radius = L, length = H)
#lsc6.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc6.name = "LSC6"
#lsc6.shape.append_transform(tf.translation_matrix((10*L,0,0)))
#
#lsc7 = Rod(radius = L, length = H)
#lsc7.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc7.name = "LSC7"
#lsc7.shape.append_transform(tf.translation_matrix((12*L,0,0)))
#
#lsc8 = Rod(radius = L, length = H)#
#lsc8.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc8.name = "LSC8"
#lsc8.shape.append_transform(tf.translation_matrix((14*L,0,0)))
##
#lsc9 = Rod(radius = L, length = H)#
#lsc9.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc9.name = "LSC9"
#lsc9.shape.append_transform(tf.translation_matrix((16*L,0,0)))
##
#lsc10 = Rod(radius = L, length = H)#
#lsc10.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
#lsc10.name = "LSC10"
#lsc10.shape.append_transform(tf.translation_matrix((18*L,0,0)))

scene = Scene()
scene.add_object(lsc)
#scene.add_object(lsc2)#
#scene.add_object(lsc3)
#scene.add_object(lsc4)
#scene.add_object(lsc5)
#scene.add_object(lsc6)
#scene.add_object(lsc7)
#scene.add_object(lsc8)
#scene.add_object(lsc9)
#scene.add_object(lsc10)

# Ask python that the directory of this script file is and use it as the location of the database file
pwd = os.getcwd()
sql_file = 'planar_cyls9.sql'
dbfile = os.path.join(pwd, sql_file) # <--- the name of the database file

trace = Tracer(scene=scene, source=source, seed=1, throws=100000, steps = 1000, database_file=dbfile, use_visualiser=False, show_log=False)
trace.show_lines = True
trace.show_path = True
import time
tic = time.clock()
trace.start()
toc = time.clock()

# 6) Statistics
print ""
print "Run Time: ", toc - tic
print ""

# 7) SQL Analyis

sqlite_file = sql_file
table_name = 'photon'
id_column = 'uid'
lost = 0
hit = 0
tic = time.clock()
for photon_number in range(100000):
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute('SELECT uid FROM photon WHERE pid={p_num}'.\
        format(p_num = photon_number))
    uids = c.fetchall()

    uid2 = []
    for i in uids:
        for j in i:
            uid2.append(j)
    if len(uid2) != 0:
        max_u = max(uid2)
        min_u = min(uid2)

        c.execute('SELECT surface_id FROM state WHERE uid<={mx} AND uid>={mn}'.\
    	   format(mx = max_u, mn = min_u))
        final_surf = c.fetchall()

        hits = []

        for i in final_surf:
            for j in i:
                if j == 'hull':
                    hits.append(False)
                elif j == 'base':
                    hits.append(True)
                    break
            
                elif j == 'cap':
                    hits.append(True)
                    break
                
                elif j == 'None':
                    hits.append(False)

        if True in hits:
            hit +=1
        else:
            lost += 1
    if photon_number%1000 == 0:
        toc = time.clock()
        print photon_number/1000, '% Done Interogating', toc - tic
        tic = toc - tic

print lost, 'photons lost and', hit, 'photons hit'
