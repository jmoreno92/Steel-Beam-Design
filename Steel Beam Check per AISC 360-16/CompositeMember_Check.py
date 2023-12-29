# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 07:49:48 2022

@author: JM
"""

#Import libraries
import pandas as pd #Might not use
import numpy as np  #Might not use
import math
import xsect



"""
 Funtion gets geometric properties of section in AISC shape database v15.0
"""

# e.g. A = GetSectProp("W12X35").GetSectProp()
class GetSectProp:
    
    def __init__(self, Sect_string):
        self.Sect_string = Sect_string
    
    def GetSectProp(self):
        try:
            SectProp = xsect.CrossSection.from_aisc(self.Sect_string)
            
            #Define in SectProp other relevant properties
            SectProp.bf = SectProp.meta.get("bf")
            SectProp.flg_ratio = SectProp.meta.get("bf/2tf")
            SectProp.Cw = SectProp.meta.get("Cw")
            SectProp.d = SectProp.meta.get("d")
            SectProp.web_ratio = SectProp.meta.get("h/tw")
            SectProp.ho = SectProp.meta.get("ho")
            SectProp.kdes = SectProp.meta.get("kdes")
            SectProp.rts = SectProp.meta.get("rts")
            SectProp.tf = SectProp.meta.get("tf")
            SectProp.tw = SectProp.meta.get("tw")
            SectProp.type = SectProp.meta.get("type")
            
            return SectProp
        except:
            print("String was not detected or shape was not found")




"""
 Funtion classifies section for local buckling
"""

def LocalBuckling(SectProp, Fy):
    try:
        #Constants
        E = 29000       #ksi
        
        #Members in compression, AISC 360-16 Table B4.1a
        #Flanges: Case 1 for unstiffened elements
        lr_flg_c = 0.56 * math.sqrt(E/Fy)
        if SectProp.flg_ratio <= lr_flg_c:  
            flg_comp_c = "C"
        else:
            flg_comp_c = "S"
        
        #Web: Case 5 for stiffened elements
        lr_web_c = 1.49 * math.sqrt(E/Fy)
        if SectProp.web_ratio <= lr_web_c:  
            web_comp_c = "C"
        else:
            web_comp_c = "S"
            
        
        #Members in flexure, AISC 360-16 Table B4.1b
        #Flanges: Case 10 for unstiffened elements
        lp_flg_f = 0.38 * math.sqrt(E/Fy)
        lr_flg_f = 1.0 * math.sqrt(E/Fy)
        if SectProp.flg_ratio <= lp_flg_f:
            flg_comp_f = "C"
        elif lp_flg_f < SectProp.flg_ratio and SectProp.flg_ratio <= lr_flg_f:
            flg_comp_f = "NC"  
        elif SectProp.flg_ratio > lr_flg_f:
            flg_comp_f = "S"          
        
        #Web: Case 15 for stiffened elements
        lp_web_f = 3.76 * math.sqrt(E/Fy)
        lr_web_f = 5.70 * math.sqrt(E/Fy)
        if SectProp.web_ratio <= lp_web_f:
            web_comp_f = "C"
        elif lp_web_f < SectProp.web_ratio and SectProp.web_ratio <= lr_web_f:
            web_comp_f = "NC"  
        elif SectProp.web_ratio > lr_web_f:
            web_comp_f = "S"          
            
        return flg_comp_c, web_comp_c, flg_comp_f, web_comp_f
        
    except:
        print("Local buckling couldn't be checked")




"""
 Funtion calculates design flexural strength
"""

def M_Strength(Sect_string, Fy, L, Lb, flg_comp_f = "C", web_comp_f = "C"):
    try:
        #Call 'GetSectProp' and store it in 'W'. Short for wide-flange section
        W = GetSectProp(Sect_string)
        
        #Call 'LocalBuckling' to check member compactness 
        flg_comp_c, web_comp_f, flg_comp_f, web_comp_f = LocalBuckling(W, Fy)
        
        #Constants
        Phi = 0.9       #Flexure reduction factor
        E = 29000       #ksi
        Cb = 1.00      #Assume uniform moment
        c = 1       #Coefficient for doubly symmetric I-shapes per F2-8a        

        #Perform calculations
        if flg_comp_f == "C" and web_comp_f == "C":
            #Yielding, AISC 360-16 F2.1
            Mp = Fy * W.plast_sect_mod_x
            
            #Lateral-Torsional Buckling, AISC 360-16 F2.2 
            Lp = 1.76 * W.gyradius_y * math.sqrt(E/Fy)   # Limiting length, Lp
            
            Lr = 1.95 * W.rts * (E / (0.7*Fy) ) * \
                math.sqrt( ((W.inertia_t * c) / (W.elast_sect_mod_x * W.ho)) + \
                          math.sqrt( ((W.inertia_t * c) / (W.elast_sect_mod_x * W.ho))**2 + 6.76 * (0.7*Fy / E)**2) ) # Limiting length, Lr
            
            Fcr = ( (Cb * math.pi**2 * E) / ( (Lb*12) / W.rts)**2 ) * \
                math.sqrt(1 + 0.078 * W.inertia_t * c / (W.elast_sect_mod_x * W.ho) * ( (Lb*12) / W.rts)**2 )
                    
            if Lb*12 <= Lp:
                MnLTB = Mp
                cond = "Lb <= Lp"
            elif Lp < Lb*12 and Lb*12 <= Lr:
                MnLTB = min( Mp, Cb* ( Mp - ( Mp - 0.7 * Fy * W.elast_sect_mod_x ) * (Lb*12 - Lp) / (Lr - Lp)  ) )
                cond = "Lp < Lb <= Lr"
            elif Lb*12 > Lr:
                MnLTB = min( Mp, Fcr*W.elast_sect_mod_x )
                cond = "Lb > Lr"
                
            Mn = min(Mp, MnLTB)
            FactMn = Phi*Mn
            
            print("")
            print("AISC 360-16: DESIGN OF MEMBER FOR FLEXURE")
            print("")
            print("Local buckling for members subject to flexure")
            print("Flange classification:", flg_comp_f)
            print("Web classification:", web_comp_f)
            print("")
            print("Yielding")
            print("Mp =", round(Mp/12,2), "kip-ft")
            print("")
            print("Lateral-Torsional Buckling:")
            print("Lb =", Lb, "ft")
            print("Lp =", round(Lp/12,2), "ft" )
            print("Lr =", round(Lr/12,2), "ft")
            print(cond)
            print("Fcr = ", round(Fcr,2), "ksi") 
            print("MnLTB = ", round(MnLTB/12,2), "kip-ft")
            print("")
            print("Design Flexural strength:")
            print("Mn =", round(Mn/12,2), "kip-ft")
            print("Phi*Mn =", round(FactMn/12,2), "kip-ft")
            
            Result_Output = str(" \
\n\
AISC 360-16: DESIGN OF MEMBER FOR FLEXURE \n\n \
Local buckling for members subject to flexure \n \
Flange classification: " +  str(flg_comp_f) + "\n \
Web classification: " + str(web_comp_f) + "\n \n \
Yielding: \n \
Mp = " + str(round(Mp/12,2)) + " kip-ft \n \n \
Lateral-Torsional Buckling: \n \
Lb = " + str(Lb) + " ft \n \
Lp = " + str(round(Lp/12,2)) + " ft \n \
Lr = " + str(round(Lr/12,2)) + " ft \n"
+ str(cond) + "\n \
Fcr = " + str(round(Fcr,2)) + " ksi \n \
MnLTB = " + str(round(MnLTB/12,2)) + " kip-ft \n \n \
Design Flexural strength: \n \
Mn = " + str(round(Mn/12,2)) + " kip-ft \n \
Phi*Mn = " + str(round(FactMn/12,2)) + " kip-ft \n \
")
    
                                      
            return Mn, W, Result_Output
                    
            
        elif (flg_comp_f == "NC" or flg_comp_f =="S") and web_comp_f == "C":
            print("calc to be implemented per AISC 360-16 Sect F3. In progress")
        else:
            print("In progress")    
            
    except:
        print("Moment capacity failed. Input not valid or shape was not found")   


############################################################################

#Input parameters
#Name = str(input("Enter the section: "))
#Fy = float(input('Enter yield strength (ksi), Fy = '))
#L = float(input('Enter member unbraced length (ft), L = '))
#Lb = float(input('Enter member braced length (ft), Lb = '))

Name = "W12X35"
Fy = 50
L = 25
Lb = 15

# Call SectProp Function
#Result = M_Strength(Name, Fy, L, Lb)