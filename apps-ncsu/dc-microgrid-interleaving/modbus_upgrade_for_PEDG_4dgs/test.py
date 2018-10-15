from math import acos
pi=3.141592
phase_shift = {}
dataValues = {}
dataValues[111] = (10.3331, 0.161)
dataValues[112] = (12.2075, 0.127002)
dataValues[113] = (12.9366, 0.177934)
dataValues[114] = (9, 0.02)


MagPhsortedFromMag = sorted( dataValues.values(),  reverse=True )
IPsortedFromMag = sorted( dataValues, key=dataValues.__getitem__,  reverse=True )
            
I1mag_1 = dataValues[IPsortedFromMag[0]][0]
I1mag_2 = dataValues[IPsortedFromMag[1]][0]
I1mag_3 = dataValues[IPsortedFromMag[2]][0]
I1ph_1  = dataValues[IPsortedFromMag[0]][1]
I1ph_2  = dataValues[IPsortedFromMag[1]][1]
I1ph_3  = dataValues[IPsortedFromMag[2]][1]
            
if (I1mag_1 > I1mag_2 + I1mag_3):       
    phase_shift[IPsortedFromMag[1]] = pi 
    phase_shift[IPsortedFromMag[2]] = pi
else :
    beta  = acos((I1mag_1*I1mag_1+I1mag_2*I1mag_2-I1mag_3*I1mag_3)/2/I1mag_1/I1mag_2)
    alpha = acos((I1mag_1*I1mag_1+I1mag_3*I1mag_3-I1mag_2*I1mag_2)/2/I1mag_1/I1mag_3)
    phase_shift[IPsortedFromMag[1]] = pi-I1ph_1+I1ph_2-beta;  
    phase_shift[IPsortedFromMag[2]] = pi-I1ph_1+I1ph_3+alpha;

print phase_shift
