import tkinter as tk

class Window(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.act = tk.Button(self)
        self.act['text'] = 'Hello World\n(cccc)'
        self.act['command'] = self.prtin
        self.act.pack(side='top')

        self.quit = tk.Button(
            self,
            text='QUIT',
            fg='red',
            command=self.master.destroy
        )

        self.quit.pack(side='bottom')

    def prtin(self):
        print('heeheehoohoo')

root = tk.Tk()
w = Window(master=root)
w.mainloop()
