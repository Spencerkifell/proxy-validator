from tkinter import ttk
from Pages.ProxyTab import ProxyTab
from tkinter import simpledialog
from functools import partial
import tkinter as tk

class MainView(ttk.Notebook):    
    def __init__(self, master, root: tk.Tk, verbose=False):
        super().__init__(master)
        
        self.verbose = verbose
        self.root = root
        self.pack(expand=True, fill=tk.BOTH)
        
        # Menu Options
        self._create_menu()
        
        # Proxy Tab
        self.proxy_tab = ProxyTab(self)
        self.add(self.proxy_tab, text=self.proxy_tab.TAB_NAME)
        
        # Other Tabs
        tab2 = ttk.Frame(self)
        tab3 = ttk.Frame(self)
        
        self.add(tab2, text="Configs")
        self.add(tab3, text="Tools")
        
    def _create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="Set Total Threads", command=partial(self._set_total_threads, self.verbose))
        
    def _set_total_threads(self, verbose=False):
        self.proxy_tab.total_threads.set(simpledialog.askinteger("Total Threads", "Enter the total number of threads to use:"))
        if self.proxy_tab.total_threads and verbose:
            print("Total Threads:", self.proxy_tab.total_threads.get())

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ProxyPy")
    root.minsize(750, 450)
    root.maxsize(750, 450)    
    mv = MainView(root, root, True)
    root.mainloop()
