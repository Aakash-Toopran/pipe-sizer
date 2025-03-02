import math
import tkinter as tk
from tkinter import ttk
import json

# Global
paraCheck = ""
pipeID = 0


# Function to load JSON data from a file
def load_json_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

json_data = load_json_data('Pipe_Size\data\data.json')

pipelIB = json_data['pipe_sizes_lib']

# Data handeling

def get_columns(data):
    return list(data[0].keys()) if data else []

def get_column_values(data, column):
    return list(dict.fromkeys(str(item[column]) for item in data if item[column]))

def find_pipe_id(data, dim_type, pipe_size, pipe_type):
    for item in data:
        if str(item[dim_type]) == pipe_size and item[pipe_type]:
            return float(item[pipe_type])
    raise ValueError("No matching pipe size")

# Math

def calculate_flow(pipe_id, velocity):
    return round(math.pi * (pipe_id/2/1000)**2 * velocity * 3600, 2)

def calculate_velocity(pipe_id, flow):
    return round(flow / (math.pi * (pipe_id/2/1000)**2 * 3600), 2)

def calculate_reynolds(velocity, diameter):
    re = math.ceil(diameter * velocity / (1000 * 8.11e-7))
    re_label.config(text=f"Re = {re}")
    return re

def calculate_headloss(velocity, diameter):
    ff = calculate_friction_factor(float(roughness_entry.get()), diameter, calculate_reynolds(velocity, diameter))
    headloss = round(ff * float(length_entry.get()) * 1000 * velocity**2 / (2 * diameter/1000) / 100000, 4)
    headloss_label.config(text=f"Pressure Drop = {headloss} bar")
    return headloss

def calculate_friction_factor(epsilon, diameter, re):
    a0 = -0.79638 * math.log(epsilon/diameter/8.208 + 7.3357/re)
    a1 = re * (epsilon/diameter) + 9.3120665 * a0
    a2 = math.log(a1/3.7099535/re)
    return ((8.128943 + a1)/(8.128943 * a0 - 0.86859209 * a1 * a2))**2

# GUI Functions

def update_pipe_options(_):
    dim = dim_type_combo.get()
    if dim in get_columns(pipelIB):
        pipe_size_combo.config(values=get_column_values(pipelIB, dim))
        pipe_size_combo.set("")
        pipe_unit_label.config(text=dim)

def update_pipe_id(_):
    global pipeID, paraCheck
    try:
        dim_type, pipe_size, pipe_type = dim_type_combo.get(), pipe_size_combo.get(), pipe_type_combo.get()
        if pipe_size and dim_type and pipe_type:
            pipeID = find_pipe_id(pipelIB, dim_type, pipe_size, pipe_type)
            pipe_id_label.config(text=f"Pipe ID = {pipeID} mm")
            if paraCheck == "flow":
                update_flow(None)
            elif paraCheck == "velocity":
                update_velocity(None)
    except Exception as e:
        print(f"Error: {e}")

def update_flow(_):
    global paraCheck
    paraCheck = "flow"
    try:
        velocity = float(velocity_entry.get())
        flow = calculate_flow(pipeID, velocity)
        flow_entry.delete(0, "end")
        flow_entry.insert(0, flow)
        calculate_headloss(velocity, pipeID)
    except ValueError:
        pass

def update_velocity(_):
    global paraCheck
    paraCheck = "velocity"
    try:
        flow = float(flow_entry.get())
        velocity = calculate_velocity(pipeID, flow)
        velocity_entry.delete(0, "end")
        velocity_entry.insert(0, velocity)
        calculate_headloss(velocity, pipeID)
    except ValueError:
        pass

# GUI Window and widgets

app = tk.Tk()
app.title("Pipe Sizing")
app.geometry("340x400")
app.resizable(False, False)

frame = tk.Frame(app)
frame.pack(padx=10, pady=10, fill="both", expand=True)

columns = get_columns(pipelIB)
dim_type_combo = ttk.Combobox(frame, values=columns[:2]); dim_type_combo.grid(row=0, column=1, padx=10, pady=5, sticky="w")
dim_type_combo.set(columns[0]); dim_type_combo.bind("<<ComboboxSelected>>", update_pipe_options)
tk.Label(frame, text="Units").grid(row=0, column=0, padx=10, pady=5, sticky="w")

pipe_type_combo = ttk.Combobox(frame, values=columns[2:]); pipe_type_combo.grid(row=1, column=1, padx=10, pady=5, sticky="w")
pipe_type_combo.set(columns[2])
tk.Label(frame, text="Pipe Standard").grid(row=1, column=0, padx=10, pady=5, sticky="w")

pipe_size_combo = ttk.Combobox(frame, values=get_column_values(pipelIB, dim_type_combo.get())); pipe_size_combo.grid(row=2, column=1, padx=10, pady=5, sticky="w")
pipe_size_combo.bind("<<ComboboxSelected>>", update_pipe_id)
tk.Label(frame, text="Pipe Size").grid(row=2, column=0, padx=10, pady=5, sticky="w")
pipe_unit_label = tk.Label(frame, text=dim_type_combo.get()); pipe_unit_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")

pipe_id_label = tk.Label(frame, text="Pipe ID = __ mm"); pipe_id_label.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="w")

velocity_entry = tk.Entry(frame); velocity_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
velocity_entry.bind("<KeyRelease>", update_flow)
tk.Label(frame, text="Velocity").grid(row=4, column=0, padx=10, pady=5, sticky="w")
tk.Label(frame, text="m/s").grid(row=4, column=2, padx=10, pady=5, sticky="w")

flow_entry = tk.Entry(frame); flow_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
flow_entry.bind("<KeyRelease>", update_velocity)
tk.Label(frame, text="Flowrate").grid(row=5, column=0, padx=10, pady=5, sticky="w")
tk.Label(frame, text="CMH").grid(row=5, column=2, padx=10, pady=5, sticky="w")

roughness_entry = tk.Entry(frame); roughness_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
roughness_entry.insert(0, "0.045")
tk.Label(frame, text="Roughness").grid(row=6, column=0, padx=10, pady=5, sticky="w")
tk.Label(frame, text="mm").grid(row=6, column=2, padx=10, pady=5, sticky="w")

length_entry = tk.Entry(frame); length_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
length_entry.insert(0, "100")
tk.Label(frame, text="Length").grid(row=7, column=0, padx=10, pady=5, sticky="w")
tk.Label(frame, text="m").grid(row=7, column=2, padx=10, pady=5, sticky="w")

re_label = tk.Label(frame, text="Re ="); re_label.grid(row=8, column=0, columnspan=3, padx=10, pady=5, sticky="w")
headloss_label = tk.Label(frame, text="Pressure Drop ="); headloss_label.grid(row=9, column=0, columnspan=3, padx=10, pady=5, sticky="w")

app.protocol("WM_DELETE_WINDOW", lambda: (app.quit(), app.destroy())) # something to do with infnite doops

if __name__ == "__main__":
    app.mainloop()