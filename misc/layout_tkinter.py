from tkinter import font as tkFont
from tkinter.ttk import *
from tkinter import *
import tkinter.messagebox as tkm
from PIL import Image, ImageTk
from api.transfermarkt import Transfermarkt

class AppLayout:
    def __init__(self):
        self.win = Tk()
        self.win.title('Transfermarkt Scraper')
        self.win.iconbitmap('tmico.ico')
        self.win.resizable(width=False, height=False)
        # self.win.geometry('640x480')
        self.tmkt = Transfermarkt()
        self.logo = Image.open('tmlogo.png')
        self.logo = ImageTk.PhotoImage(self.logo)
        self.font = tkFont.Font(family='Segoe UI', size=12, weight='normal')
        self.pad = 5
        self.bgColor = '#002343'
        self.fgColor = '#FFFFFF'
        self.btColor = '#AC2023'

    def __app_close(self):
        if tkm.askokcancel('Transfermarkt Scraper', 'Do you want to quit?'):
            self.win.destroy()

    ### APP LAYOUT CONFIGURATION ###
    def __app_fields(self):
        self.lb_competition = Label(self.win)
        self.lb_season = Label(self.win)
        self.img_logo = Label(self.win)
        self.cb_competition = Combobox(self.win)
        self.cb_season = Combobox(self.win)
        self.bt_search = Button(self.win)
        self.bt_about = Button(self.win)

    def __app_fields_config(self):
        self.win.config(bg=self.bgColor, padx=self.pad, pady=self.pad)
        self.win.resizable(False, False)
        self.win.option_add('*TCombobox*Listbox.font', self.font)
        self.img_logo.config(image=self.logo, justify='center', bg=self.bgColor, fg=self.fgColor, font=self.font)
        self.lb_competition.config(text='Competitions', width=6, justify='left', anchor='w', bg=self.bgColor, fg=self.fgColor, font=self.font)
        self.lb_season.config(text='Seasons', width=6, justify='left', anchor='w', bg=self.bgColor, fg=self.fgColor, font=self.font)
        self.cb_competition.config(width=24, state='readonly', values='', font=self.font)
        self.cb_season.config(width=6, state='readonly', values='', font=self.font)
        self.bt_search.config(text='Search', width=12, bg=self.btColor, fg=self.fgColor, font=self.font)
        self.bt_about.config(text='About', width=12, bg=self.btColor, fg=self.fgColor, font=self.font)
 
    def __app_fields_grid(self):
        self.img_logo.grid(column=0, row=0, padx=self.pad, pady=self.pad, columnspan=2, sticky='nsew')
        self.lb_competition.grid(column=0, row=1, padx=self.pad, pady=self.pad, columnspan=1, sticky='nsew')
        self.lb_season.grid(column=0, row=2, padx=self.pad, pady=self.pad, columnspan=1, sticky='nsew')
        self.cb_competition.grid(column=1, row=1, padx=self.pad, pady=self.pad, columnspan=1, sticky='nsew')
        self.cb_season.grid(column=1, row=2, padx=self.pad, pady=self.pad, columnspan=1, sticky='nsew')
        self.bt_about.grid(column=0, row=4, padx=self.pad, pady=self.pad, columnspan=1, sticky='nsew')
        self.bt_search.grid(column=1, row=4, padx=self.pad, pady=self.pad, columnspan=1, sticky='nsew')
    
    ### POPULATE COMBO BOXES ###
    def __load_combo_competitions(self):
        self.cb_competition['values'] = self.tmkt.load_competitions()
        self.cb_competition.current(0)
    
    def __load_combo_seasons(self):
        competition = self.cb_competition.current()
        self.cb_season['values'] = self.tmkt.load_seasons(competition)
        self.cb_season.current(0)
        
    ### APP COMMANDS ###
    def __load_default_values(self):
        self.__load_combo_competitions()
        self.__load_combo_seasons()
    
    def __cmd_about_app(self):
        msg = 'Edgar Santa Rosa (C) 2022'
        msg += '\nGitHub: https://github.com/EdgarOSR'
        tkm.showinfo('Transfermarkt Scraper', msg)

    def __cmd_search(self):
        curr_comp = self.cb_competition.get()
        curr_season = self.cb_season.get()
        response = self.tmkt.scrap_tournaments(curr_comp, curr_season)
        tkm.showinfo('Transfermarkt Scraper', response)

    def __onselect_competition(self, event):
        self.__load_combo_seasons()

    def __binding_values(self):
        self.cb_competition.bind('<<ComboboxSelected>>', self.__onselect_competition)

    def __set_commands(self):
        self.bt_search.config(command=self.__cmd_search)
        self.bt_about.config(command=self.__cmd_about_app)
 
    def main(self):
        self.__app_fields()
        self.__app_fields_config()
        self.__app_fields_grid()
        self.__binding_values()
        self.__set_commands()
        self.__load_default_values()
        self.win.protocol('WM_DELETE_WINDOW', self.__app_close)
        self.win.mainloop()