from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import re
import ast
import requests
import threading

regex_pattern: str = r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b"

class ProxyTab(ttk.Frame):
    TAB_NAME = "Proxies"
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create widgets for the proxies tab
        self.file_label = ttk.Label(self, text="Selected File: None")
        self.file_label.pack(pady=10)

        self.upload_button = ttk.Button(self, text="Upload File", command=self.read_proxy_file)
        self.upload_button.pack(pady=10)

        # Frame to contain the verified and non-verified proxies
        listbox_frame = ttk.Frame(self)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        self.proxies_var = tk.StringVar()
        self.listbox1 = tk.Listbox(
            listbox_frame, 
            listvariable=self.proxies_var
        )
        self.listbox1.grid(row=0, column=0, sticky=tk.NSEW, padx=10)

        self.updated_proxies_var = tk.StringVar()
        self.listbox2 = tk.Listbox(
            listbox_frame, 
            listvariable=self.updated_proxies_var
        )
        self.listbox2.grid(row=0, column=1, sticky=tk.NSEW, padx=10)
        
        # Set the row and column weights to allow the listboxes to expand
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(1, weight=1)

        # Set the column weights to allow the listboxes to expand horizontally
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Frame to contain the controls
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        verify_button = ttk.Button(
            buttons_frame, 
            text="Verify Proxies", 
            command=self.verify_proxies
        )
        verify_button.grid(row=0, column=0, padx=10)

        use_button = ttk.Button(
            buttons_frame, 
            text="Save Proxies", 
            command=self.write_proxy_file
        )
        use_button.grid(row=0, column=1, padx=10)
        
        self.total_threads = tk.IntVar(value=1)
        
        # self.total_threads_str = tk.StringVar()
        # thread_label = ttk.Label(buttons_frame, textvariable=self.total_threads_str)
        # thread_label.config(text=f"Total Threads: {self.total_threads.get()}")
        # thread_label.grid(row=1, column=1, sticky=tk.NSEW, padx=10, pady=10)
        # self.total_threads_str = tk.StringVar()
        # thread_label = ttk.Label(buttons_frame, textvariable=self.total_threads_str, justify=tk.CENTER)
        # thread_label.grid(row=0, column=3, sticky=tk.NSEW)
        # self.total_threads_str.set(f"{self.total_threads.get()}")
        
        buttons_frame.grid_rowconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        # buttons_frame.grid_columnconfigure(2, weight=1)
        # buttons_frame.grid_columnconfigure(3, weight=1)
        # buttons_frame.grid_columnconfigure(4, weight=1)

    def read_proxy_file(self):
        with filedialog.askopenfile(filetypes=[("Text Files", "*.txt")]) as file:
            if not file.readable:
                messagebox.showerror("Error", f"Unable to open file: {file.name}")
                return
            self.file_label.config(text="Selected File: " + file.name.split('/')[-1])
            raw_data = file.read()
            values = re.findall(regex_pattern, raw_data)
        if len(values) > 0:
            self.proxies_var.set(values)

    def write_proxy_file(self):
        if not isinstance(self.updated_proxies_var, tk.StringVar) or len(self.updated_proxies_var.get()) == 0:
            messagebox.showerror("Error", "No proxies to write.")
            return
        with filedialog.asksaveasfile(filetypes=[("Text Files", "*.txt")]) as file:
            if not file.writable:
                messagebox.showerror("Error", f"Unable to write to file: {file.name}")
                return
            file.write(str(self.updated_proxies_var.get()))

    def clear_proxies(self):
        if not messagebox.askyesno("Clear Proxies", "Are you sure you want to clear the proxies?"):
            return
        self.proxies_var.set([])
        self.updated_proxies_var.set([])
        
    def update_thread_count(self, value):
        value = int(float(value))
        self.total_threads.set(value)
        # self.total_threads_str.set(f"{value}")
        
    def verify_proxy(self, proxy: str, url: str) -> bool:
        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        try:
            requests.get(url, proxies=proxies, timeout=1.5)
            return True
        except Exception:
            return False

    def verify_proxies(self, url: str = "https://www.google.com"):    
        if not isinstance(self.proxies_var, tk.StringVar) or len(self.proxies_var.get()) == 0:
            messagebox.showerror("Error", "No proxies to verify.")
            return
        
        proxies = list(ast.literal_eval(self.proxies_var.get()))
            
        thread_count = len(proxies) if len(proxies) < self.total_threads.get() else self.total_threads.get()
        
        values_per_thread = int(len(proxies) / thread_count)

        divided_proxies = {}
        for index in range(thread_count):
            values = list(ProxyTab.take(proxies, values_per_thread))
            divided_proxies[index] = values
            proxies = proxies[(len(values)):]

        while len(proxies) > 0:
            for index in range(thread_count):
                if len(proxies) == 0:
                    break
                divided_proxies[index].append(proxies.pop(0))
        
        threads = []
        for index in range(thread_count):
            print("starting thread: " + str(index))
            current_thread = threading.Thread(target=self.verify_proxy_obj, args=(divided_proxies[index], url))
            threads.append(current_thread)
            current_thread.start()
            
        for thread in threads:
            print("killing thread: " + str(thread))
            thread.join()
            
        print("all threads killed")
            
        # join the lists
        verified_proxies = [item for sublist in divided_proxies.values() for item in sublist]
        self.updated_proxies_var.set(verified_proxies)        
    
    def verify_proxy_obj(self, proxies: list, url: str = "https://www.google.com") -> list:
        for proxy in proxies:
            if not self.verify_proxy(proxy, url):
                proxies.remove(proxy)
        return proxies
    
    @staticmethod
    def take(iterable: iter, amount: int) -> iter:
        for index, item in enumerate(iterable):
            if index == amount:
                break
            yield item
