from tkinter import ttk, filedialog, messagebox
from functools import partial
import tkinter as tk
import re
import requests
import ast
import platform
import pdb

regex_pattern: str = r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b"

# Create a StringVar to represent the dataset
global proxies_var
global updated_proxies_var
global file_name_var

def read_proxy_file(text_label: ttk.Label, display_path: bool = False):
    with filedialog.askopenfile(filetypes=[("Text Files", "*.txt")]) as file:
        if not file.readable:
            messagebox.showerror("Error", f"Unable to open file: {file.name}")
            return
        file_name = file.name if display_path else file.name.split('/')[-1]
        text_label.config(text="Selected File: " + file_name)
        raw_data = file.read()
        values = re.findall(regex_pattern, raw_data)
    if len(values) > 0:
        proxies_var.set(values)
        
def write_proxy_file():
    if not isinstance(updated_proxies_var, tk.StringVar) or len(updated_proxies_var.get()) == 0:
            messagebox.showerror("Error", "No proxies to write.")
            return
    with filedialog.asksaveasfile(filetypes=[("Text Files", "*.txt")]) as file:
        if not file.writable:
            messagebox.showerror("Error", f"Unable to write to file: {file.name}")
            return
        file.write(str(updated_proxies_var.get()))

def clear_proxies():
    if not messagebox.askyesno("Clear Proxies", "Are you sure you want to clear the proxies?"):
        return
    proxies_var.set([])
    updated_proxies_var.set([])
        
def verify_proxy(proxy: str, url: str) -> bool:
    proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
    try:
        requests.get(url, proxies=proxies, timeout=1.5)
        return True
    except Exception:
        return False
    
def verify_proxies(url: str = "https://www.google.com"):    
    if not isinstance(proxies_var, tk.StringVar) or len(proxies_var.get()) == 0:
        messagebox.showerror("Error", "No proxies to verify.")
        return
    proxies = list(ast.literal_eval(proxies_var.get()))
    for index, proxy in enumerate(proxies):
        if not verify_proxy(proxy, url):
            proxies.remove(proxy)
    updated_proxies_var.set(proxies)
    
# region Root Setup

root = tk.Tk()
root.title("ProxyPy")
root.minsize(650, 400)
root.maxsize(650, 400)

menu = tk.Menu(root)

file_menu = tk.Menu(menu, tearoff=False)
file_menu.add_command(label="Upload Proxy File", command=read_proxy_file, accelerator="Command+O" if platform.system() == "Darwin" else "Control+O")
file_menu.add_command(label="Save Verified Proxies", command=write_proxy_file, accelerator="Command+S" if platform.system() == "Darwin" else "Control+S")
file_menu.add_command(label="Clear Proxies", command=clear_proxies, accelerator="Command+D" if platform.system() == "Darwin" else "Control+D")
menu.add_cascade(label="File", menu=file_menu)

tools_menu = tk.Menu(menu, tearoff=False)
tools_menu.add_command(label="Show File Path")
tools_menu.add_command(label="Verify Raw Proxies")
tools_menu.add_command(label="Use Proxies")
menu.add_cascade(label="Tools", menu=tools_menu)

tab_parent = ttk.Notebook(root)

tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab3 = ttk.Frame(tab_parent)

tab_parent.add(tab1, text="Proxies")
tab_parent.add(tab2, text="Configs")
tab_parent.add(tab3, text="Tools")

tab_parent.pack(expand=True, fill=tk.BOTH)

# Dynamic Variables

proxies_var = tk.StringVar()
updated_proxies_var = tk.StringVar()
file_name = tk.StringVar()

# Key Bindings

if platform.system() == "Darwin":
    root.bind("<Command-o>", lambda e: read_proxy_file(file_label))
    root.bind("<Command-d>", lambda e: clear_proxies())
    root.bind("<Command-s>", lambda e: write_proxy_file())
else:
    root.bind("<Control-o>", lambda e: read_proxy_file(file_label))
    root.bind("<Control-d>", lambda e: clear_proxies())
    root.bind("<Control-s>", lambda e: write_proxy_file())

# endregion

#region Tab 1

file_label = ttk.Label(tab1, text=f"Selected File: {file_name.get() if file_name.get() else 'None'}")
file_label.pack(pady=10)

upload_button = ttk.Button(tab1, text="Upload File", command=partial(read_proxy_file, file_label))
upload_button.pack(pady=10)

#region Listboxes

# Create a Frame inside tab1 for listboxes
listbox_frame = ttk.Frame(tab1)
listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

# Create the first listbox in listbox_frame
listbox1 = tk.Listbox(listbox_frame, listvariable=proxies_var)
listbox1.grid(row=0, column=0, sticky=tk.NSEW, padx=10)

# Create the second listbox in listbox_frame
listbox2 = tk.Listbox(listbox_frame, listvariable=updated_proxies_var)
listbox2.grid(row=0, column=1, sticky=tk.NSEW, padx=10)

# Set the row and column weights to allow the listboxes to expand
listbox_frame.grid_rowconfigure(0, weight=1)
listbox_frame.grid_columnconfigure(0, weight=1)
listbox_frame.grid_columnconfigure(1, weight=1)

# Set the column weights to allow the listboxes to expand horizontally
tab1.grid_columnconfigure(0, weight=1)
tab1.grid_columnconfigure(1, weight=1)

#endregion

#region Controls

buttons_frame = ttk.Frame(tab1)
buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

verify_button = ttk.Button(buttons_frame, text="Verify Proxies", command=verify_proxies)
verify_button.grid(row=0, column=0, padx=10)

use_button = ttk.Button(buttons_frame, text="Use Proxies")
use_button.grid(row=0, column=1, padx=10)

# save_button = ttk.Button(buttons_frame, text="Save Proxies", command=write_proxy_file)
# save_button.grid(row=0, column=2, padx=10)

# clear_button = ttk.Button(buttons_frame, text="Clear Proxies", command=clear_proxies)
# clear_button.grid(row=0, column=3, padx=10)

buttons_frame.grid_rowconfigure(0, weight=1)
buttons_frame.grid_columnconfigure(0, weight=1)
buttons_frame.grid_columnconfigure(1, weight=1)

#endregion

#endregion

#region Tab 2

#endregion

#region Tab 3

#endregion

root.config(menu=menu)
root.mainloop()