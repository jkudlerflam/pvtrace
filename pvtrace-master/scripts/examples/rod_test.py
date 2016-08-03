
from __future__ import division
import sys
sys.path.insert(0, "/Users/jkudlerflam/Desktop/pvtrace-master/")
import sqlite3
import numpy as np 
from pvtrace.external import transformations as tf
from pvtrace import *

''' Simulation of a rectangular homogeneously doped LSC

Steps:
1) Define sizes
2) Create a light source
3) Load absorption and emission data for orgnaic dye
4) Load linear background absorption for PMMA
5) Create LSC object and start tracer
6) Calculate statistics.

'''

# 1) Define some sizes
L = 0.05
W = 0.05
H = 0.0025
reflectance = []
for x in np.linspace(0,.999,100):
    # 2) Create light source from AM1.5 data, truncate to 400 -- 800nm range
    file = os.path.join(PVTDATA,'sources','AM1.5g-full.txt')
    oriel = load_spectrum(file, xbins=np.arange(400,800))
    source = SimpleSource(position = (x*L,.1,.001), direction=(0,-1,0)) # Incident light AM1.5g spectrum
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
    #lsc = LSC(origin=(0,0,0), size=(L,W,H) )
    #lsc.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
    #lsc.name = "LSC"
    
    lsc = Rod(radius = L, length = H)
    lsc.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
    lsc.name = "LSC"
    lsc.shape.append_transform(tf.translation_matrix((2*L,0,0)))
    lsc2 = Rod(radius = L, length = H)
    lsc2.material = CompositeMaterial([pmma, fluro_red], refractive_index = 1.5)
    lsc2.name = "LSC2"
    
    
    scene = Scene()
    scene.add_object(lsc2)
    scene.add_object(lsc)
    
    # Ask python that the directory of this script file is and use it as the location of the database file
    pwd = os.getcwd()
    sql_file = str(x) + 'homogen_db2.sql'
    dbfile = os.path.join(pwd, sql_file) # <--- the name of the database file
    
    trace = Tracer(scene=scene, source=source, seed=1, throws=1000, database_file=dbfile, use_visualiser=False, show_log=False)
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
    photon_number = 10
    #for photon_number in range(100):
   	#conn = sqlite3.connect(sqlite_file)
   	#c = conn.cursor()
    #
   	#c.execute('SELECT uid FROM photon WHERE pid={p_num}'.\
  		#format(p_num = photon_number))
   	#uids = c.fetchall()
    #
    ##print 'uids:',  uids
   	#uid2 = []
   	#for i in uids:
  		#for j in i:
 			#uid2.append(j)
   	#if len(uid2) != 0:
  		#max_u = max(uid2)
  		#min_u = min(uid2)
    ##print max_u, min_u
    #
  		#c.execute('SELECT x, y, z FROM position WHERE uid<={mx} AND uid>={mn}'.\
 			#format(mx = max_u, mn = min_u))
  		#positions = c.fetchall()
    ##			print 'positions:', positions
  		#c.execute('SELECT surface_id FROM state WHERE uid<={mx} AND uid>={mn}'.\
    #     			format(mx = max_u, mn = min_u))
  		#final_surf = c.fetchall()
  		##print final_surf
  		#hits = []
  		#for i in final_surf:
 			#for j in i:
    #				if j == 'hull':
   	#				hits.append(False)
    #				elif j == 'base':
   	#				hits.append(True)
    #				elif j == 'cap':
   	#				hits.append(True)
    #				elif j == 'None':	
   	#				hits.append(False)
  		##print hits
  		#if True in hits:
 			#hit +=1
  		#else:
 			#lost += 1
    #print lost, 'photons lost and', hit, 'photons hit'
    ref = 0
    no_ref = 0
    for photon_number in range(1000):
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
    
                    c.execute('SELECT ray_direction_bound FROM state WHERE uid={mn}+1'.\
                            format(mn = min_u))
                    final_surf = c.fetchall()
    
                    reflects = []
                    for i in final_surf:
                            for j in i:
                                    if j == 'In':
                                            no_ref +=1
                                    elif j == 'Out':
                                        if len(uid2) <= 2:
                                            ref +=1
                                        else:
                                        
                                            c.execute('SELECT ray_direction_bound FROM state WHERE uid={mn}+2'.\
                                                    format(mn = min_u))
                                            final_surf2 = c.fetchall()
                                            for k in final_surf2:
                                                for l in k:
                                                    if l == 'In':
                                                        no_ref +=1
                                                    elif l == 'Out':
                                                        if len(uid2) <= 3:
                                                            ref +=1
                                                        else:
    
                                                            c.execute('SELECT ray_direction_bound FROM state WHERE uid={mn}+3'.\
                                                                    format(mn = min_u))
                                                            final_surf3 = c.fetchall()
                                                            for m in final_surf3:
                                                                for n in m:
                                                                    if l == 'In':
                                                                        no_ref +=1
                                                                    elif l == 'Out':
                                                                        ref +=1
    
    
    print ref, 'out of', (ref + no_ref), 'reflected'
    #print 'final surface intersection: ', final_surf
    reflectance.append(ref/(ref+no_ref))
    conn.close()

np.save('/Users/jkudlerflam/Desktop/reflectance.npy', reflectance)
plt.plot(np.linspace(0,100,11), reflectance)
plt.show()

