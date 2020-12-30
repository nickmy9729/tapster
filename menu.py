import numpy
import pprint
import math
import time
try:
    from tkinter import *
except ImportError:
    from tkinter import *
from tkinter import ttk

from bartender import Bartender
from belfrywidgets import Wizard

bartender = Bartender()

class Application():
    def __init__(self, master, bartender):
        self.master = master
        self.bartender = bartender
        self.drinks = self.bartender.filterDrinks("drink")
        self.availDrinks = []

        master.title("Bartender")
        master.resizable(0, 0)

        self.buttons = []
        self.numOfButton = 0

        availDrinksLBL = Label(master, text="Available Drinks:", fg="black")
        drinkInfoLBL = Label(master, text="Drink Information:", fg="black")
        availDrinksLBL.grid(row=0, column=0, sticky=W)
        drinkInfoLBL.grid(row=0, column=1, sticky=W)

        self.frm = Frame(master)
        self.frm.grid(row=1, column=0, sticky=N+S, padx=10)
        master.rowconfigure(1, weight=1)
        master.columnconfigure(1, weight=1)
        
        scrollbar = Scrollbar(self.frm, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        drinkList = Listbox(self.frm, width=20, yscrollcommand=scrollbar.set, font=("Helvetica", 20))
        drinkList.bind('<<ListboxSelect>>',self.onselect)
        drinkList.pack(expand=True, fill=Y)

        self.drinkSelection = Listbox(master, height=15, font=("Helvetica", 15))
        self.drinkSelection.grid(row=1, column=1, sticky=E+W+N, padx=10)

        for d in self.drinks:
            if d.visible == True:
                self.availDrinks.append(d)
                drinkList.insert(END, d.name)

        self.pourButton = Button(master, text='Make Drink', command=lambda: self.quit(self.master), font=("Helvetica", 15))
        self.pourButton.grid(row=2, column=1, sticky=E+W+N)
    
    def pour_drink(self, wiz, bttn, lblvar, recipe):
        bttn.config(state=DISABLED)
        step_num = wiz.pane_names.index(wiz.selected_pane)
        num_steps = len(wiz.pane_names)
        lblvar.set("Pouring Drink\n\nAdding Ingredients:\n" + "\n".join(recipe.attributes['steps'][step_num - 1]))
        var = IntVar()
        self.master.after(10000, var.set, 1)
        print("waiting...")
        self.master.wait_variable(var)
        #time.sleep(10)
        if step_num + 1 == num_steps:
            wiz.set_finish_enabled(True)
            lblvar.set("Pour complete, please click finish")
        else:
            wiz.set_next_enabled(True)
            lblvar.set("Pour complete, please click next")

    def launchWizard(self, recipe):
        wiz = Wizard(
            width=640,
            height=480,
            cancelcommand=lambda: print("Cancel"),
            finishcommand=lambda: print("Finish"),
        )

        wiz.geometry("1372x722")
        wiz.attributes('-fullscreen', True)

        def disable_finish():
            wiz.set_finish_enabled(False)

        def enable_finish():
            wiz.set_finish_enabled(True)

        def disable_next():
            wiz.set_next_enabled(False)

        def handle_entry():
            idx = wiz.pane_names.index(wiz.selected_pane) + 1
            num_steps = len(wiz.pane_names)
            print("Step " + str(idx) + " of " + str(num_steps))
            wiz.set_prev_enabled(False)
            wiz.set_next_enabled(True)
            wiz.set_finish_enabled(False)
            if idx == num_steps:
                wiz.set_next_enabled(False)
                wiz.set_finish_enabled(True)

        def pour_start():
            wiz.set_finish_enabled(False)
            wiz.set_next_enabled(False)
            wiz.set_prev_enabled(False)

        pane = wiz.add_pane("Introduction", "Introduction", entrycommand=lambda: handle_entry())
        lbl = Label(pane, text="Making Drink " + recipe.name, font=("Helvetica", 15))
        lbl.pack(side=TOP, fill=BOTH, expand=1)
        print(recipe.attributes)
        if 'steps' in recipe.attributes:
            step_idx = 1
            num_steps = len(recipe.attributes['steps'])
            print("Num Steps " + str(num_steps))
            for step in recipe.attributes['steps']:
                pane = None
                if isinstance(step, str):
                    pane = wiz.add_pane("step " + str(step_idx), "step " + str(step_idx), entrycommand=lambda: handle_entry())
                    lbl = Label(pane, text=step)
                    lbl.pack(side=TOP, fill=BOTH, expand=1)
                if isinstance(step, list):
                    pane = wiz.add_pane("step " + str(step_idx), "step " + str(step_idx), entrycommand=pour_start)
                    text_var = StringVar(pane)
                    text_var.set("Ready to pour ingredients:\n" + "\n".join(recipe.attributes['steps'][step_idx - 1]) + "\n\nPlace glass under dispenser and press 'Pour' when ready.")
                    lbl  = Label(pane, textvariable=text_var, font=("Helvetica", 15))
                    lbl.pack(side=TOP, fill=BOTH, expand=1)
                    bttn = Button(pane, text="Pour", font=("Helvetica", 15))
                    bttn.config(command=lambda: self.pour_drink(wiz, bttn, text_var, recipe))
                    bttn.pack(side=BOTTOM, fill=BOTH)
                step_idx = step_idx + 1
        self.master.wait_window(wiz)

    def onselect(self, event):
        widget = event.widget
        selection=widget.curselection()
        picked = widget.get(selection[0])
        index = int(widget.curselection()[0])

        self.pourButton.configure(command= lambda recipe=self.availDrinks[index]: self.launchWizard(recipe))

        #value = w.get(index)
        self.drinkSelection.delete(0, END)
        self.drinkSelection.insert(END, "Drink Name: " + self.availDrinks[index].name)
        self.drinkSelection.insert(END, "Ingredients: ")
        for i in self.availDrinks[index].attributes['ingredients']:
            self.drinkSelection.insert(END, "    " + i + ": " + str(self.availDrinks[index].attributes['ingredients'][i]) + " ml")
        
    def adminMenu(self):
        pass

    def quit(self, master):
        self.bartender.quit()
        master.quit()

def launchPumpConfigUI():
    win = Toplevel()
    win.geometry("1372x722")
    win.attributes('-fullscreen', True)
    win.wm_title("Pump Config")

    columns = {
        'Pump': 'name',
        'Flow Rate': 'flowrate',
        'Pin': 'pin',
        'Ingredient': '',
        'Empty1': '',
        'Empty2': '',
        'Empty3': '',
        'Prime': '',
        'Test': '',
        'Clean': ''
    }

    #height = len(list(bartender.pump_configuration.keys()))
    #width = columns.keys()
    cells = {}
    row = 0
    for p in bartender.pump_configuration:
        c = 0
        for k in columns.keys():
            if k == "Prime" or k == "Clean" or k == "Test":
                but = Button(win, text=k, font=("Helvetica", 15))
                but.grid(row=row, column=c)
                cells[(row,c)] = but
            else:
                if k == 'Ingredient':
                    tkvar = StringVar(win)
                    choices = sorted(list(map(lambda x: bartender.slugify(x['name']), bartender.getIngredientsList())))
                    b = ttk.Combobox(win)
                    b['values'] = choices
                    try:
                        current_ing = choices.index(bartender.pump_configuration[p]['value'])
                        b.current(current_ing)
                    except ValueError:
                        pass
                    b.config(font=('Helvetica', 20))
                elif k == 'Pin':
                    b = ttk.Combobox(win)
                    pin_options = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
                    b['values'] = pin_options
                    try:
                        curr_pin = pin_options.index(int(bartender.pump_configuration[p]['pin']))
                        b.current(curr_pin)
                    except ValueError:
                        b.current(0)
                    b.config(font=('Helvetica', 20), width=5)
                elif k == 'Flow Rate':
                    b = ttk.Combobox(win)
                    flow_options = (100, 400)
                    b['values'] = flow_options
                    try:
                        curr_flow = flow_options.index(int(bartender.pump_configuration[p]['flowrate']))
                        b.current(curr_flow)
                    except ValueError:
                        b.current(0)
                    b.config(font=('Helvetica', 20), width=10)
                elif k == "Empty1":
                    b = Label(win, text='          ', font=("Helvetica", 15))
                elif k == "Empty2":
                    b = Label(win, text='          ', font=("Helvetica", 15))
                elif k == "Empty3":
                    b = Label(win, text='          ', font=("Helvetica", 15))
                else:
                    b = Label(win, text=bartender.pump_configuration[p][columns[k]], font=("Helvetica", 15))
                #b = Entry(win, text=bartender.pump_configuration[p][columns[k]])
                b.grid(row=row, column=c)
                cells[(row,c)] = b
            c = c + 1
        row = row + 1
    #writeBut = Button(win, text="Ok", command=win.destroy, font=("Helvetica", 15))
    writeBut = Button(win, text="Ok", command= lambda: getPumpConfig(win), font=("Helvetica", 15))
    writeBut.grid(row=row, column=6)
    cleanAllBut = Button(win, text="Clean All Pumps", font=("Helvetica", 15))
    cleanAllBut.grid(row=row, column=5)

def getPumpConfig(win):
    columns = {
        'Pump': 'name',
        'Flow Rate': 'flowrate',
        'Pin': 'pin',
        'Ingredient': '',
        'Prime': '',
        'Test': '',
        'Clean': ''
    }

    pump_cfg = {}
    for r_idx, pump in enumerate(bartender.pump_configuration):
        pump = {
            "flowrate": '',
            "name": "Pump " + str(r_idx + 1),
            "pin": '', 
            "value": ""
        }
        for c_idx, col in enumerate(columns):
            if col == 'Flow Rate':
                option = win.grid_slaves(row=r_idx, column=c_idx)
                pump['flowrate'] = option[0].get()
            elif col == 'Pin':
                option = win.grid_slaves(row=r_idx, column=c_idx)
                pump['pin'] = option[0].get()
            elif col == 'Ingredient':
                option = win.grid_slaves(row=r_idx, column=c_idx)
                #pump['value'] = dict(option[0])['text']
                pump['value'] = option[0]['values'][option[0].current()]

            pump_cfg["pump_" + str(r_idx + 1)] = pump
    bartender.writePumpConfiguration(pump_cfg)
    win.destroy()


def launchCleanUI():
    win = Toplevel()
    win.wm_title("Window")

    l = Label(win, text="Input")
    l.grid(row=0, column=0)

    b = Button(win, text="Okay", command=win.destroy)
    b.grid(row=1, column=0)


def launchPrimeUI():
    win = Toplevel()
    win.wm_title("Window")

    l = Label(win, text="Input")
    l.grid(row=0, column=0)

    b = Button(win, text="Okay", command=win.destroy)
    b.grid(row=1, column=0)

def launchPumpAdmin():
    wiz = Wizard(
        width=640,
        height=480,
        cancelcommand=lambda: print("Cancel"),
        finishcommand=lambda: print("Finish"),
    )

root = Tk()
root.overrideredirect(True)
root.overrideredirect(False)
root.attributes('-fullscreen',True)
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("1372x722")
#root.geometry("%dx%d+0+0" % (w, h))
menubar = Menu(root)
adminbar = Menu(menubar, tearoff=0)
adminbar.add_command(label="Pump Config", command=launchPumpConfigUI, font=("Helvetica", 20))
menubar.add_cascade(label="Admin", menu=adminbar, font=("Helvetica", 20))
root.config(menu=menubar)
menu = Application(root, bartender)


root.mainloop()
