import tkinter as tk
from tkinter import ttk, messagebox
import json
from managerLSNMP import Manager  # Certifique-se de que a classe Manager está no mesmo diretório ou ajuste o import
import time  # Para timestamp nos logs

class DeviceWindow:
    def __init__(self, root, manager, dispositivo_id, device_type, on_close_callback):
        self.manager = manager
        self.dispositivo_id = dispositivo_id
        self.device_type = device_type
        self.root = root
        self.root.title(f"{device_type.capitalize()} - ID {dispositivo_id}")
        self.on_close_callback = on_close_callback

        # Vincula o evento de fechamento da janela ao callback
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Resultados
        self.result_text = tk.Text(self.root, wrap="word", height=15)
        self.result_text.pack(expand=True, fill="both")

    def on_close(self):
        self.on_close_callback(self.dispositivo_id)
        self.root.destroy()

    def update_device_status(self):
        relevant_ids = self.get_relevant_ids()
        response = self.manager.get(ids=relevant_ids, dispositivo_id=self.dispositivo_id)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, json.dumps(response, indent=4))

    def get_relevant_ids(self):
        if self.device_type == "ar_condicionado":
            return ['estado', 'modo', 'intensidade', 'temperatura']
        elif self.device_type == "iluminacao":
            return ['estado', 'intensidade']
        return []

class SNMPManagerApp:
    def __init__(self, root):
        self.manager = Manager('localhost', 54321)
        self.device_windows = {}

        self.root = root
        self.root.title("SNMP Manager")

        # Criação dos frames
        self.frame_top = ttk.Frame(root, padding="10")
        self.frame_top.grid(row=0, column=0, sticky="ew")

        self.frame_bottom = ttk.Frame(root, padding="10")
        self.frame_bottom.grid(row=1, column=0, sticky="nsew")

        # Comando GET/SET
        self.command_label = ttk.Label(self.frame_top, text="Command:")
        self.command_label.grid(row=0, column=0, sticky="w")

        self.command_var = tk.StringVar()
        self.command_combo = ttk.Combobox(self.frame_top, textvariable=self.command_var, state="readonly")
        self.command_combo["values"] = ("GET", "SET")
        self.command_combo.grid(row=0, column=1, sticky="ew")

        # Dispositivo ID
        self.device_id_label = ttk.Label(self.frame_top, text="Device ID:")
        self.device_id_label.grid(row=1, column=0, sticky="w")

        self.device_id_entry = ttk.Entry(self.frame_top)
        self.device_id_entry.grid(row=1, column=1, sticky="ew")

        # Atributos
        self.attributes_label = ttk.Label(self.frame_top, text="Attributes (comma separated):")
        self.attributes_label.grid(row=2, column=0, sticky="w")

        self.attributes_entry = ttk.Entry(self.frame_top)
        self.attributes_entry.grid(row=2, column=1, sticky="ew")

        # Valores (apenas para SET)
        self.values_label = ttk.Label(self.frame_top, text="Values (comma separated, for SET only):")
        self.values_label.grid(row=3, column=0, sticky="w")

        self.values_entry = ttk.Entry(self.frame_top)
        self.values_entry.grid(row=3, column=1, sticky="ew")

        # Botão de enviar
        self.send_button = ttk.Button(self.frame_top, text="Send", command=self.send_command)
        self.send_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Resultados
        self.result_text = tk.Text(self.frame_bottom, wrap="word", height=15)
        self.result_text.grid(row=0, column=0, sticky="nsew")

        # Botões para abrir janelas de dispositivos
        self.device_button_frame = ttk.Frame(root, padding="10")
        self.device_button_frame.grid(row=2, column=0, sticky="ew")
        
        self.ar_condicionado_button = ttk.Button(self.device_button_frame, text="Ar Condicionado 1.1", command=lambda: self.open_device_window("1.1", "ar_condicionado"))
        self.ar_condicionado_button.grid(row=0, column=0, padx=5, pady=5)

        self.iluminacao_button = ttk.Button(self.device_button_frame, text="Iluminação 2.2", command=lambda: self.open_device_window("2.2", "iluminacao"))
        self.iluminacao_button.grid(row=0, column=1, padx=5, pady=5)

        self.ar_condicionado_1_3_button = ttk.Button(self.device_button_frame, text="Ar Condicionado 1.3", command=lambda: self.open_device_window("1.3", "ar_condicionado"))
        self.ar_condicionado_1_3_button.grid(row=0, column=2, padx=5, pady=5)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_bottom.grid_rowconfigure(0, weight=1)
        self.frame_bottom.grid_columnconfigure(0, weight=1)

    def log_response(self, response):
        with open("snmp_responses.log", "a") as log_file:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            log_file.write(f"[{timestamp}] {json.dumps(response, indent=4)}\n")

    def send_command(self):
        command = self.command_var.get()
        dispositivo_id = self.device_id_entry.get().strip()
        attributes = self.attributes_entry.get().strip().split(',')
        attributes = [attr.strip() for attr in attributes]

        if not dispositivo_id or not attributes:
            messagebox.showwarning("Input Error", "Device ID and Attributes are required.")
            return

        try:
            if command == "GET":
                response = self.manager.get(ids=attributes, dispositivo_id=dispositivo_id)
            elif command == "SET":
                values = self.values_entry.get().strip().split(',')
                values = [int(value.strip()) if value.strip().isdigit() else value.strip() for value in values]
                if len(values) != len(attributes):
                    messagebox.showwarning("Input Error", "Number of values must match number of attributes.")
                    return
                response = self.manager.set(ids=attributes, dispositivo_id=dispositivo_id, valores=values)
            else:
                messagebox.showerror("Command Error", "Invalid command selected.")
                return

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, json.dumps(response, indent=4))
            self.log_response(response)  # Log the response to the file

            # Atualize as janelas de dispositivos após o comando
            self.update_device_windows()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_device_window(self, dispositivo_id, device_type):
        if dispositivo_id not in self.device_windows:
            new_window = tk.Toplevel(self.root)
            device_window = DeviceWindow(new_window, self.manager, dispositivo_id, device_type, self.on_device_window_close)
            self.device_windows[dispositivo_id] = device_window
            device_window.update_device_status()  # Atualizar status do dispositivo ao abrir a janela
        else:
            self.device_windows[dispositivo_id].root.lift()

    def on_device_window_close(self, dispositivo_id):
        if dispositivo_id in self.device_windows:
            del self.device_windows[dispositivo_id]

    def update_device_windows(self):
        for device_window in self.device_windows.values():
            device_window.update_device_status()

if __name__ == "__main__":
    with open("snmp_responses.log", "w") as log_file:
        log_file.write("")
    root = tk.Tk()
    app = SNMPManagerApp(root)
    root.mainloop()

