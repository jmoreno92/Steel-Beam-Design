#!/usr/bin/python3
# JM
# 2022-May-16

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from Member_Check import * ##import functions defined in Member_Check.py

class MemberCheckGUI:

    def __init__(self, master):
        
        master.title('Steel Member Check')
        master.resizable(False, False)
        master.configure(background = '#ffffff')
        
        #Style (color, font, etc)
        self.style = ttk.Style()
        self.style.configure('TFrame', background = '#ffffff')
        self.style.configure('TButton', background = '#ffffff')
        self.style.configure('TLabel', background = '#ffffff', font = ('Arial', 11))
        self.style.configure('Header1.TLabel', font = ('Arial', 16, 'bold'))    
        self.style.configure('Header2.TLabel', font = ('Arial', 12, 'bold'))    
        self.style.configure('Subheader.TLabel', font = ('Arial', 12, 'underline'))   
        
        #FRAME 1: Header
        self.frame_header = ttk.Frame(master)
        self.frame_header.pack()
        
        self.logo = PhotoImage(file = 'RCLogo1.gif')
        ttk.Label(self.frame_header, image = self.logo).grid(row = 0, column = 0, rowspan = 2)
        ttk.Label(self.frame_header, text = 'Rutherford + Chekene', style = 'Header1.TLabel').grid(row = 0, column = 1)
        ttk.Label(self.frame_header, wraplength = 300,
                  text = "Steel Member Flexure Check", style = 'Header2.TLabel').grid(row = 1, column = 1)
        
        #FRAME 2: Content / input values
        self.frame_content = ttk.Frame(master)
        self.frame_content.pack()

        #Labels for entries
        ttk.Label(self.frame_content, text = 'Input parameters:', style = 'Subheader.TLabel').grid(row = 0, column = 0, padx = 5, pady = 10, sticky = 'sw')
        ttk.Label(self.frame_content, text = 'W Section:').grid(row = 1, column = 0, padx = 5, sticky = 'sw')
        ttk.Label(self.frame_content, text = 'Yield strength, Fy (ksi):').grid(row = 2, column = 0, padx = 5, sticky = 'sw')
        ttk.Label(self.frame_content, text = 'Unbraced length, L (ft):').grid(row = 3, column = 0, padx = 5, sticky = 'sw')
        ttk.Label(self.frame_content, text = 'Braced length, Lb (ft):').grid(row = 4, column = 0, padx = 5, sticky = 'sw')
        ttk.Label(self.frame_content, text = 'Results:').grid(row = 10, column = 0, padx = 5, sticky = 'sw')
        
        #Definition of entry boxes
        self.entry_WSection = ttk.Entry(self.frame_content, width = 24, font = ('Arial', 10))
        self.entry_Fy = ttk.Entry(self.frame_content, width = 24, font = ('Arial', 10))
        self.entry_L = ttk.Entry(self.frame_content, width = 24, font = ('Arial', 10))
        self.entry_Lb = ttk.Entry(self.frame_content, width = 24, font = ('Arial', 10))
        self.text_results = Text(self.frame_content, width = 80, height = 30, font = ('Arial', 10))
        #self.text_results.config(wrap = 'word', state = 'disabled')  #we want to wrap text at words, also we don't want user to delete text
        
        #Location (in grid) of entry boxes
        self.entry_WSection.grid(row = 1, column = 1, padx = 5)
        self.entry_Fy.grid(row = 2, column = 1, padx = 5)
        self.entry_L.grid(row = 3, column = 1, padx = 5)
        self.entry_Lb.grid(row = 4, column = 1, padx = 5)
        self.text_results.grid(row = 11, column = 0, columnspan = 2, padx = 5)
        
        #Buttons
        ttk.Button(self.frame_content, text = 'Calculate',
                   command = self.calculate).grid(row = 8, column = 0, padx = 15, pady = 15, sticky = 'e')
        ttk.Button(self.frame_content, text = 'Clear',
                   command = self.clear).grid(row = 8, column = 1, padx = 15, pady = 15, sticky = 'w')

    def calculate(self):        
        #Print results in console
        print('W Section: {}'.format(self.entry_WSection.get()))
        print('Fy: {}'.format(self.entry_Fy.get()))
        print('L: {}'.format(self.entry_L.get()))
        print('Lb: {}'.format(self.entry_Lb.get()))
        print('Results: {}'.format(self.text_results.get(1.0, 'end')))
        # Call SectProp Function
        Result = M_Strength(self.entry_WSection.get(), float(self.entry_Fy.get()), float(self.entry_L.get()), float(self.entry_Lb.get()))
        #print(Result)
        
        #Print results in textbox
        messagebox.showinfo(title = 'Rutherford + Chekene', message = 'Calculation completed') 
        self.text_results.insert('end', 'Section: ' + self.entry_WSection.get() + '\n')
        self.text_results.insert('end', 'Fy: ' + self.entry_Fy.get() + ' ksi \n')
        self.text_results.insert('end', 'L: ' + self.entry_L.get() + ' ft \n')
        self.text_results.insert('end', 'Lb: '+ self.entry_Lb.get() + ' ft \n')
        try:
            self.text_results.insert('end', Result[2])  #print 'Result_Output' from 'Member_Check.py'
        except:
            self.text_results.insert('end', 'Moment capacity calculation failed. Input not valid or shape was not found.')  #print 'Result_Output' from 'Member_Check.py'
        

        
    def clear(self):
        self.entry_WSection.delete(0, 'end')
        self.entry_Fy.delete(0, 'end')
        self.entry_L.delete(0, 'end')
        self.entry_Lb.delete(0, 'end')
        self.text_results.delete(1.0, 'end')   #1.0 refers to the position at the beginning of the text box
         
def main():            
    
    root = Tk()
    gui = MemberCheckGUI(root)
    root.mainloop()
    
if __name__ == "__main__": main()
