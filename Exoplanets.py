#!/usr/bin/env python
'''
Cornell University ASTR 1102 Lab: Star Clusters and Galactic Nebulae
Original Java Applet by Terry Herter et al.
Written by Michael Lam
'''

import random
import glob
import matplotlib
matplotlib.use('TkAgg')

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from matplotlib.figure import Figure
#from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.ticker import *#MultipleLocator, FormatStrFormatter, LogLocator

import sys
import time

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk


DIR='cluster'
SEPARATOR_COLOR="#CCCCCC"
SLEEP_TIME=1

##==================================================
## Physics
##==================================================

##==================================================
## Data Processing
##==================================================

#Masses and Radii for Kepler 4-8, from exoplanets.org
kplr = ['KPLR11853905','KPLR8191672','KPLR10874614','KPLR5780885','KPLR6922244']
names = {'KPLR11853905':'Kepler-4',
         'KPLR8191672':'Kepler-5',
         'KPLR10874614':'Kepler-6',
         'KPLR5780885':'Kepler-7',
         'KPLR6922244':'Kepler-8'}
masses = {'KPLR11853905':'1.223 +0.053/-0.091',
          'KPLR8191672':'1.374 +0.04/-0.059',
          'KPLR10874614':'1.209 +0.044/-0.038',
          'KPLR5780885':'1.35 +4.9e-5/-0.126',
          'KPLR6922244':'1.213 +0.067/-0.063'}
radii = {'KPLR11853905':'1.487 +0.071/-0.084',
         'KPLR8191672':'1.793 +0.043/-0.062',
         'KPLR10874614':'1.391 +0.017/-0.028',
         'KPLR5780885':'1.843 +0.048/-0.066',
         'KPLR6922244':'1.486 +0.053/-0.062'}


def loadData(mode=0):
    if mode==0:
        dtrs = glob.glob("data/hlsp*_dtr.txt")
        dtr = random.choice(dtrs)
        name = dtr.split('_')[4]
        rvb = glob.glob("data/hlsp*%s*rvb.txt"%name)[0]
    else:
        if 4 <= mode <= 8:
            mode -= 4
        name = kplr[mode]
        dtr = glob.glob("data/*%s*_dtr.txt"%name)[0]
        rvb = glob.glob("data/*%s*_rvb.txt"%name)[0]

    time,flux = np.loadtxt(dtr,unpack=True)
    rvtime,rv,rverr = np.loadtxt(rvb,unpack=True,usecols=(0,1,2))

    retval = dict()
    retval['name'] = names[name]
    retval['mass'] = masses[name]
    retval['time'] = time - 2400000#time[0]
    retval['flux'] = flux
    if "v2.0" in dtr: #need to add 1
        retval['flux'] += 1
    retval['rvtime'] = rvtime - 2400000#rvtime[0]
    retval['rv'] = rv
    retval['rverr'] = rverr
    return retval



def loadKepler10b():
    x=np.load("data/Kepler-10.npz")

    retval = dict()
    retval['name'] = 'Kepler-10 (Unsmoothed)'
    retval['mass'] = "0.895 +/- 0.06"
    retval['radius'] = "1.056 +/- 0.021"
    retval['time'] = x['time'] - 2400000#time[0]
    retval['flux'] = x['flux']
    retval['err'] = x['err']
    
    rvtime,rv,rverr = np.loadtxt("data/kepler_10b_rv.txt",skiprows=5,unpack=True)
    retval['rvtime'] = rvtime + 50000
    retval['rv'] = rv
    retval['rverr'] = rverr
    return retval






##==================================================
## GUI 
##==================================================

    

root = Tk.Tk()
#root.geometry('+1400+100')
root.geometry('+100+100')
root.wm_title("Exoplanets")



## ----------
## Build primary GUI containers
## ----------

mainframe = Tk.Frame(root)
mainframe.grid(row=0)

figframe = Tk.Frame(mainframe)#, bd = 6, bg='red')
fig = Figure(figsize=(8.5,5), dpi=75)
canvas = FigureCanvasTkAgg(fig, figframe)
canvas.get_tk_widget().grid(row=0)#,side=Tk.TOP)#,fill='x')
canvas.show()

#canvas._tkcanvas.grid(row=1)#, fill=Tk.BOTH, expand=1)

figframe.grid(row=0,column=0)

## ----------
## Tkinter Variables
## ----------
var_mode = Tk.IntVar()
var_fits_on = Tk.IntVar()
var_message = Tk.StringVar()
var_period = Tk.StringVar()
var_phase = Tk.StringVar()
var_depth = Tk.StringVar()
var_width_top = Tk.StringVar()
var_width_bottom = Tk.StringVar()
var_amplitude = Tk.StringVar()

var_mode.set(-1)

#image_distance_modulus = Tk.PhotoImage(file="DistanceModulus.gif")
#image_period_magnitude = Tk.PhotoImage(file="PeriodMagnitude.gif")

## ----------
## Primary Window
## ----------

ax_lightcurve = fig.add_subplot(211)
ax_rvcurve = fig.add_subplot(212)




def update_main(mode=-1,clear=True):

    if mode == 0:
        mode = random.choice([4,5,6,7,8])
        var_mode.set(mode)

    if mode == -1:
        mode = var_mode.get()
    else:
        var_mode.set(mode)

    if mode==10:
        data = loadKepler10b()
    else:
        data = loadData(mode=mode)#var_mode.get())

    ax_lightcurve_xlim = ax_lightcurve.get_xlim()
    ax_lightcurve_ylim = ax_lightcurve.get_ylim()
    ax_rvcurve_xlim = ax_rvcurve.get_xlim()
    ax_rvcurve_ylim = ax_rvcurve.get_ylim()

    ax_lightcurve.cla()
    ax_rvcurve.cla()

    time = data['time']
    rvtime = data['rvtime']
    mintime = min([min(time),min(rvtime)])
    maxtime = max([max(time),max(rvtime)])
    dtime = maxtime-mintime

    period = var_period.get()
    if period != "":
        try: 
            time = time % float(period)
            rvtime = rvtime % float(period)
        except ValueError:
            busy("Error: Bad Input, ignoring period",sleep=SLEEP_TIME)
            period=""

    fits_on = var_fits_on.get()
    phase = var_phase.get()
    depth = var_depth.get()
    width_top = var_width_top.get()
    width_bottom = var_width_bottom.get()
    amplitude = var_amplitude.get()

    try:
        phi = float(phase)
    except ValueError:
        phi = 0
    try:
        h = float(depth)
    except ValueError:
        h = 0
    try:
        bottom = float(width_bottom)
    except ValueError:
        bottom = 0
    try:
        top = float(width_top)
    except ValueError:
        top = 0
    try:
        amplitude = float(amplitude)
    except ValueError:
        amplitude = 0

    
    

    ax_lightcurve.plot(time,data['flux'],'k.')
    ax_lightcurve.set_ylabel("Fractional Flux")
    ax_lightcurve.set_title("%s: M=%s M_Sun"%(data['name'],data['mass'].split()[0]))

    ax_rvcurve.plot(rvtime,data['rv'],'k.')
    ax_rvcurve.set_ylabel("Radial Velocity [m/s]")




    if period == "":
        if clear:
            ax_lightcurve.set_xlim(mintime-0.05*dtime,maxtime+0.05*dtime)
            ax_rvcurve.set_xlim(mintime-0.05*dtime,maxtime+0.05*dtime)
        else:
            ax_lightcurve.set_xlim(ax_lightcurve_xlim)
            ax_rvcurve.set_xlim(ax_rvcurve_xlim)
            ax_lightcurve.set_ylim(ax_lightcurve_ylim)
            ax_rvcurve.set_ylim(ax_rvcurve_ylim)
        ax_rvcurve.set_xlabel("Time (days)")
        t = np.linspace(mintime-0.05*dtime,maxtime+0.05*dtime,1000)
    else:
        P = float(period)
        if clear:
            ax_lightcurve.set_xlim(-0.05*P,1.05*P)
            ax_rvcurve.set_xlim(-0.05*P,1.05*P)
        else:
            ax_lightcurve.set_xlim(ax_lightcurve_xlim)
            ax_rvcurve.set_xlim(ax_rvcurve_xlim)
            ax_lightcurve.set_ylim(ax_lightcurve_ylim)
            ax_rvcurve.set_ylim(ax_rvcurve_ylim)
        ax_rvcurve.set_xlabel("Wrapped Time (days)")
        t = np.linspace(-0.05*P,1.05*P,1000)
        if fits_on != 0:
            a = phi - top / 2.0 #a,b,c,d are where the points falls
            b = phi - bottom / 2.0
            c = phi + bottom / 2.0
            d = phi + top / 2.0
            trap = np.piecewise(t, [t<a, np.logical_and(a<=t,t<b),np.logical_and(b<=t,t<c),np.logical_and(c<=t,t<d),t>=d],[1,lambda x: 1-h*(x-a)/(b-a),1-h,lambda x: 1-h*(d-x)/(d-c),1])

            ax_lightcurve.plot(t,trap,'r')
            
            ax_rvcurve.plot(t,-1*amplitude*np.sin((2*np.pi/P)*(t - phi)),'r')
    

    canvas.draw()

def update_mainclear(mode=-1):
    update_main(mode=mode,clear=False)


toolbarframe = Tk.Frame(mainframe)
toolbarframe.grid(row=1,sticky=Tk.W)
toolbar = NavigationToolbar2TkAgg(canvas, toolbarframe)
toolbar.update()
toolbar.grid(row=1,sticky=Tk.W)

separator = Tk.Frame(mainframe,width=600,height=2,bg=SEPARATOR_COLOR,bd=1, relief=Tk.SUNKEN).grid(row=2,pady=2)

frame_buttons = Tk.Frame(mainframe)
frame_buttons.grid(row=3,sticky=Tk.W)


# display the menu
#root.config(menu=menubar)
#separator = Tk.Frame(frame_buttons,width=2,height=100, bg=SEPARATOR_COLOR,bd=1, relief=Tk.SUNKEN).grid(row=0,column=1,padx=2)


frame_period = Tk.Frame(frame_buttons)
frame_period.grid(row=0,column=0)



label_period = Tk.Label(frame_period,text="Period Estimate [days]:")
label_period.grid(row=1,column=0)
entry_period = Tk.Entry(frame_period,width=7,textvariable=var_period)
entry_period.grid(row=1,column=1)


#Yes, these are flipped, need to fix that
button_redrawclear = Tk.Button(frame_period,text="Update",command=lambda: update_mainclear(mode=-1))
button_redrawclear.grid(row=2,column=1)
button_redraw = Tk.Button(frame_period,text="Redraw",command=lambda: update_main(mode=-1))
button_redraw.grid(row=2,column=0)



separator = Tk.Frame(frame_buttons,width=2,height=100, bg=SEPARATOR_COLOR,bd=1, relief=Tk.SUNKEN).grid(row=0,column=1,padx=2)

frame_parameters = Tk.Frame(frame_buttons)
frame_parameters.grid(row=0,column=2)


checkbutton_fits = Tk.Checkbutton(frame_parameters,text="Overplot Fits",variable=var_fits_on,command=lambda: update_main(mode=-1))
checkbutton_fits.grid(row=0,column=0)



label_phase = Tk.Label(frame_parameters,text="Phase [days]:")
label_phase.grid(row=1,column=0)
entry_phase = Tk.Entry(frame_parameters,width=7,textvariable=var_phase)
entry_phase.grid(row=1,column=1)

label_depth = Tk.Label(frame_parameters,text="Depth [Fractional Flux]:")
label_depth.grid(row=2,column=0)
entry_depth = Tk.Entry(frame_parameters,width=7,textvariable=var_depth)
entry_depth.grid(row=2,column=1)

label_width_top = Tk.Label(frame_parameters,text="Transit Duration [days]:")
label_width_top.grid(row=0,column=2)
entry_width_top = Tk.Entry(frame_parameters,width=7,textvariable=var_width_top)
entry_width_top.grid(row=0,column=3)

label_width_bottom = Tk.Label(frame_parameters,text="Depth Duration [days]:")
label_width_bottom.grid(row=1,column=2)
entry_width_bottom = Tk.Entry(frame_parameters,width=7,textvariable=var_width_bottom)
entry_width_bottom.grid(row=1,column=3)
 
label_amplitude = Tk.Label(frame_parameters,text="RV Amplitude [m/s]:")
label_amplitude.grid(row=2,column=2)
entry_amplitude = Tk.Entry(frame_parameters,width=7,textvariable=var_amplitude)
entry_amplitude.grid(row=2,column=3)



## ----------
## Buttons/Menus
## ----------

def busy(msg="Working...",sleep=0):
    var_message.set(msg)
    root.config(cursor="watch")
    root.update()#_idletasks() #need to work through queued items
    if sleep!=0:
        time.sleep(sleep)
        notbusy()

def notbusy():
    var_message.set("")
    root.config(cursor="")


def popup_about():
    title="About"
    text=["Cornell University Department of Astronomy",
          "ASTR 1104 Lab: Exoplanets",
          "Python code by Michael Lam 2014",
          "",
          "Data obtained through Kepler HLSP",
          "http://archive.stsci.edu/prepds/kepler_hlsp/",
          "Kepler-10 data through MAST:",
          "http://archive.stsci.edu/kepler/data_search/search.php",
          "and Bathalha+ 2011",
          "",
          "Masses from exoplanets.org and references within"]
    d = window_popup(root,title,text,WIDTH=50)
    root.wait_window(d.top)

#Why does this pop up twice?
def popup_commands():
    title="Commands"
    text=["Click on a mode to select a graph",
          "",
          "Period Estimate: Folds lightcurve and RV data by this amount",
          "Redraw: Clears the figure and starts fresh",
          "Update: Redraws the plot while keeping the axes fixed",
          "",
          "All parameters are set to 0 by default."]
    d = window_popup(root,title,text,WIDTH=50)
    root.wait_window(d.top)
    
#def popup_equations():
#    title="Useful Equations"
#    text=["Distance modulus:",
#          "image_distance_modulus",
 #         "Cepheid II Period-Magnitude Relation (Matsunaga et al. 2006):"]


    d = window_popup(root,title,text,WIDTH=50)#,photo)
    root.wait_window(d.top)


class window_popup:
    def __init__(self,parent,title,txt,WIDTH=40):
        top = self.top = Tk.Toplevel(parent)
        top.title(title)
        top.geometry('+150+250')
        top.bind("<Return>",lambda event:self.ok())
        for i in range(len(txt)):
            if txt[i][:5]=="image":
                photo = eval(txt[i])
                label=Tk.Label(top,image=photo)
                label.image = photo # keep a reference!
                label.pack()
            else:
                Tk.Label(top,anchor=Tk.W,width=WIDTH,text=txt[i]).pack()
        b = Tk.Button(top,text="OK",command=self.ok)
        b.pack()
        b.focus_set()
    def ok(self):
        self.top.destroy()



def destroy(event):
    sys.exit()




## Bindings
#root.bind("<Return>",superdo)
root.bind("<Escape>", destroy)
root.bind("<Control-q>", destroy)
root.bind("<F1>",lambda event: popup_about())
root.bind("<F2>",lambda event: popup_commands())
#root.bind("<F3>",lambda event: popup_equations())
root.bind("<F10>",destroy)



menubar = Tk.Menu(root)

filemenu = Tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit",accelerator="Esc", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

selectmenu = Tk.Menu(menubar,tearoff=0)
selectmenu.add_command(label="Random",command=lambda: update_main(mode=0))
selectmenu.add_separator()
selectmenu.add_command(label="Kepler-4",command=lambda: update_main(mode=4))
selectmenu.add_command(label="Kepler-5",command=lambda: update_main(mode=5))
selectmenu.add_command(label="Kepler-6",command=lambda: update_main(mode=6))
selectmenu.add_command(label="Kepler-7",command=lambda: update_main(mode=7))
selectmenu.add_command(label="Kepler-8",command=lambda: update_main(mode=8))
selectmenu.add_separator()
selectmenu.add_command(label="Kepler-10",command=lambda: update_main(mode=10))
menubar.add_cascade(label="Select", menu=selectmenu)

helpmenu = Tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About",accelerator="F1", command=popup_about)
helpmenu.add_command(label="Commands",accelerator="F2", command=popup_commands)
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
root.config(menu=menubar)



update_main(mode=0)

#root.configure(cursor=("@/usr/X11R6/include/X11/bitmaps/star","/usr/X11R6/include/X11/bitmaps/starMask", "white", "black"))

root.mainloop()
#Tk.mainloop()
