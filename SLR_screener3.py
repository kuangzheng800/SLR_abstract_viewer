import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog 
import pandas as pd

class CustomText(tk.Text):
    '''A text widget with a new method, highlight_pattern()

    example:

    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=True):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=1)
        self.grid()

        # initiation function
        self.create_widgets()
                
        root.bind("<space>",self.next_line)
        root.bind("<Up>",self.prev_line)
        root.bind("<Down>",self.next_line)
        root.bind("<Return>",self.goto_line)


    def create_widgets(self):
        # create layout frames

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.frame1 = tk.Frame(self,width = 800, height = 10)
        self.frame1.columnconfigure(1, weight=2)
        self.frame1.rowconfigure(1, weight=1)
        self.frame1.grid_columnconfigure(0, weight=1)
        self.frame1.grid(row = 0, sticky = "ew")

        self.inc_screen = ''
        self.exc_screen = ''


        #module for opening files
        self.label1 = tk.Label(self.frame1,text = r"Full SLR file directory (name refence ID as Ref:)")
        self.label1.grid(row = 0, column = 0,padx=10,sticky = "E",pady = 2)
        self.file_link = tk.StringVar() 
        self.linkbox = tk.Entry(self.frame1,textvariable = self.file_link,takefocus = 0)
        self.linkbox.grid(row = 0,column = 1,padx=10,sticky = "EW",pady = 2)
        
        self.linkbutton = tk.Button(self.frame1,text = "Open file directory",command = self.openlink,width = 20,takefocus = 0)
        self.linkbutton.grid(row = 0, column = 2,padx= 10,pady = 2,sticky = "W")

        self.openbutton = tk.Button(self.frame1,text = "Read file...", command = self.openexplorer,width = 20,takefocus = 0)
        self.openbutton.grid(row = 0, column = 3,padx= 10,pady = 2,sticky = "W")


        # model for highlighting words
        self.label2 = tk.Label(self.frame1, text = "Input words to highlight separated by ','    BLUE:")
        self.label2.grid(row = 1, column = 0,padx=10,sticky = "E",pady = 2)
        self.label3 = tk.Label(self.frame1, text = "(case insensitive, takes regex)        RED:")
        self.label3.grid(row = 2, column = 0,padx=10,sticky = "E",pady = 2)
        
        self.inc_line = tk.StringVar()
        self.incbox = tk.Entry(self.frame1,textvariable = self.inc_line,takefocus = 0)
        self.incbox.grid(row = 1, column = 1,columnspan = 3,padx=10,sticky = "EW",pady = 2)
        

        self.exc_line = tk.StringVar()
        self.excbox = tk.Entry(self.frame1,textvariable = self.exc_line,takefocus = 0)
        self.excbox.grid(row = 2,column = 1,columnspan = 3,padx=10,sticky = "EW",pady = 2)

        self.screenbutton = tk.Button(self.frame1,text = "Highlight",command = self.highlight,width = 15,takefocus = 0)
        self.screenbutton.grid(row = 1,column = 4, rowspan = 2,padx=10,sticky = "SN",pady = 2)

        # model for controlling

        self.previous = tk.Button(self.frame1,text = "Previous entry (Up)",command = self.prev_line,width = 30,takefocus = 0)
        self.previous.grid(row = 3, column = 1,padx=10,sticky = "EW",pady = 2)

        self.next = tk.Button(self.frame1,text = "Next entry (Down, Space)",command = self.next_line,width = 30,takefocus = 0)
        self.next.grid(row = 3, column = 2,padx=10,pady = 2)
        self.goto_index = tk.IntVar()
        self.index = tk.Entry(self.frame1,textvariable = self.goto_index)
        self.index.grid(row = 3,column = 3,padx=10,sticky = "EW",pady = 2)
        self.goto = tk.Button(self.frame1,text = "Go to index (Return)", command = self.goto_line,width = 15,takefocus = 0)
        self.goto.grid(row = 3, column =4,padx=10,pady = 2)

        # text model
        self.text = CustomText(self,font =("calibri", 16),width = 130,height = 40,wrap="word")
        self.i = 0



    def openlink(self,event = None):
        try:
            self.data = pd.read_csv(self.file_link.get())
            self.text.config(state = tk.NORMAL)
            self.text.delete("1.0", "end")
            self.text.insert("1.0","File\n\n"+self.file_link.get()+"\n\n is opened! \n\n now press Tab and put in an reference number to start screening!")
            self.text.config(state = tk.DISABLED)
            root.focus()
        except:
            messagebox.showinfo('Warning!','File not readable, please try again!')

    def openexplorer(self,event = None):
        try:
            self.file_link =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
            print(self.file_link)
            self.data = pd.read_csv(self.file_link)
            print(self.data)
            print(self.text)
            self.text.config(state = tk.NORMAL)
            self.text.delete("1.0", "end")
            self.text.insert("1.0","File\n\n"+self.file_link+"\n\n is opened! \n\n now press Tab and put in an reference number to start screening!")
            self.text.config(state = tk.DISABLED)
            tk.Grid.columnconfigure(self.text, 0, weight=1)
            self.text.grid(row = 4,sticky = "nswe")
            root.focus()
        except:
            messagebox.showinfo('Warning!','File not readable, please try again!')

    def highlight(self,event = None):
        inc_key_words = self.inc_line.get().split(',')
        print(inc_key_words)
        exc_key_words = self.exc_line.get().split(',')
        self.inc_screen = '(?i)(('+')|('.join(inc_key_words)+'))'
        self.exc_screen = '(?i)(('+')|('.join(exc_key_words)+'))'
        self.print_line()
        root.focus()
                                    
    def next_line(self,event=None):
        self.i += 1
        if self.i == self.data.shape[0] or self.i < 0:
            self.destroy()
        self.print_line()

    def prev_line(self,event=None):
        self.i -= 1
        if self.i < 0:
            self.i = 0
        self.print_line()

    def goto_line(self,event=None):
        index = self.goto_index.get()
        all_index = self.data['Ref']
        root.focus()
        try:
            self.i = all_index[all_index == index].index[0]
            print(self.goto_index)
            self.print_line()
        except IndexError:
            self.text.config(state = tk.NORMAL)
            self.text.delete("1.0", "end")
            self.text.insert("1.0","Ref index does not exist! \nTry another one")
            self.text.config(state = tk.DISABLED)

    def print_line(self):
        line = self.data.iloc[self.i,]
        line = '\n\n'.join([str(i) for i in line.tolist()])
        self.text.config(state = tk.NORMAL)
        self.text.delete("1.0", "end")
        self.text.insert("1.0",line)
        self.text.config(state = tk.DISABLED)
        self.text.tag_configure("inc", foreground="#003fff",font = "helvetica 18 bold")
        self.text.highlight_pattern(self.inc_screen, "inc")
        self.text.tag_configure("exc", foreground="#ff0000",font = "helvetica 18 bold")
        self.text.highlight_pattern(self.exc_screen, "exc")
        self.text.grid(row = 4,sticky = "nswe")
        
root = tk.Tk() #main window
root.title('SLR Viewer')
#inc_key_words = "male,HPV,RRP,hand and neck,genital warts,anal,penile,prevalence,incidence,cohort,case-control, review".split(",")
#exc_key_words = "female,trial,cost,animal".split(",")
#key_words = ['QOL','Quality','Eczema','Atopic Dermatitis','QALY','cost','conclusion','review','children','index']
#inc_screen = '(?i)(('+')|('.join(inc_key_words)+'))'
#exc_screen = '(?i)(('+')|('.join(exc_key_words)+'))'

#data = pd.read_csv("C:/Users/KuangZ/Documents/HPV_epi_screening/Screenfile.csv")
#data = pd.read_csv("C:/Users/KuangZ/Desktop/test.csv")
app = Application(master=root)
app.mainloop() # main window
