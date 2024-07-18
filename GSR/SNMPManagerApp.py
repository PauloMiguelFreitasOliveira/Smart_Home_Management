import tkinter as tk
from tkinter import messagebox
from managerLSNMP import Manager

class DeviceWindow:
    def __init__(self, master, device_id, manager):
        self.master = master
        self.device_id = device_id
        self.manager = manager
        self.master.title(f"Device {device_id} Interface")
        
        # Get device attributes
        self.attributes = self.get_device_attributes()

        print(f"Attributes for device {device_id}: {self.attributes}")  # Debug: print attributes

        self.create_widgets()

    def get_device_attributes(self):
        response = self.manager.get(ids=[], dispositivo_id=self.device_id)
        print(f"Response from manager for device {self.device_id}: {response}")  # Debug: print response

        if "valores" in response and response["valores"]:
            return response["valores"]
        return []

    def create_widgets(self):
        row = 0
        self.entries = {}
        
        for attribute in self.attributes:
            for key, value in attribute.items():
                label = tk.Label(self.master, text=key)
                label.grid(row=row, column=0, sticky='e')
                
                entry = tk.Entry(self.master)
                entry.grid(row=row, column=1, sticky='w')
                entry.insert(0, value)  # Insere o valor do atributo na entrada
                entry.config(state='readonly')  # Define a entrada como somente leitura
                self.entries[key] = entry
                
                row += 1

        self.update_button = tk.Button(self.master, text="Update", command=self.update_device)
        self.update_button.grid(row=row, columnspan=2)

    def update_device(self):
        updated_values = {key: entry.get() for key, entry in self.entries.items()}
        response = self.manager.set(ids=list(updated_values.keys()), dispositivo_id=self.device_id, valores=list(updated_values.values()))
        messagebox.showinfo("Update", f"Device {self.device_id} updated with response: {response}")

class ManagerApp:
    def __init__(self, root, manager):
        self.manager = manager
        self.root = root
        self.root.title("Manager Interface")
        
        self.device_list_frame = tk.Frame(self.root)
        self.device_list_frame.pack(padx=10, pady=10)

        self.devices = self.load_devices()
        
        self.device_windows = {}  # Dicionário para armazenar as janelas dos dispositivos

        for device_id in self.devices:
            button = tk.Button(self.device_list_frame, text=f"Device {device_id}", command=lambda id=device_id: self.open_device_window(id))
            button.pack()

        self.refresh_button = tk.Button(self.device_list_frame, text="Refresh", command=self.refresh_devices)
        self.refresh_button.pack()

        self.open_all_device_windows()

    def load_devices(self):
        with open('dispositivos.txt', 'r') as file:
            lines = file.readlines()
            devices = [line.split('|')[0].strip() for line in lines if line.strip()]
        return devices

    def open_device_window(self, device_id):
        device_window = tk.Toplevel(self.root)
        self.device_windows[device_id] = DeviceWindow(device_window, device_id, self.manager)

    def open_all_device_windows(self):
        for device_id in self.devices:
            self.open_device_window(device_id)

    def refresh_devices(self):
        self.devices = self.load_devices()
        
        # Destroi as janelas existentes que não estão mais na lista de dispositivos
        for device_id in list(self.device_windows.keys()):
            if device_id not in self.devices:
                self.device_windows[device_id].master.destroy()
                del self.device_windows[device_id]

        # Abre novas janelas para dispositivos que foram adicionados
        for device_id in self.devices:
            if device_id not in self.device_windows:
                self.open_device_window(device_id)

if __name__ == "__main__":
    root = tk.Tk()
    manager = Manager('localhost', 54321)
    app = ManagerApp(root, manager)
    root.mainloop()

