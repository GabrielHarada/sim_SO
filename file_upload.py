import classes as cl
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import *
import re
import importlib.util
import importlib.machinery
import os

def edit_cell(event, tree):
    # Check if a cell was clicked
    item = tree.identify_row(event.y)
    coluna = tree.identify_column(event.x)
    if not item or not coluna:
        return

    # Column index
    col_index = int(coluna.replace('#', '')) - 1
    valor_atual = tree.item(item, "values")[col_index]

    # cell coordinates
    x, y, width, height = tree.bbox(item, coluna)
    
    # Entry field over the cell
    entry = tk.Entry(tree)
    entry.place(x=x, y=y, width=width, height=height)
    entry.insert(0, valor_atual)
    entry.focus()

    def save(event=None):
        novo_valor = entry.get()
        valores = list(tree.item(item, "values"))
        valores[col_index] = novo_valor
        tree.item(item, values=valores)
        entry.destroy()

    def cancel_writing(event=None):
        entry.destroy()

    entry.bind("<Return>", save)
    entry.bind("<Escape>", cancel_writing)
    entry.bind("<FocusOut>", save)

def configure_file(filename, tree, selected_dropdown, os_quantum_entry):

    # Clear existing data
    for item in tree.get_children():
            tree.delete(item)

    colunas = ["id", "cor", "ingresso", "duracao", "prioridade", "lista_eventos"]
    tree["columns"] = colunas
    tree["show"] = "headings"

    # Configure columns
    for col in colunas:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=50, anchor="center")

    # Check if data format is valid
    if filename != "":
        if validate_file(filename):
            with open(filename, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                values_simulator = lines[0].split(";")
                for line in lines[1:]:
                    valores = line.split(";")
                    if len(valores) == len(colunas):
                        tree.insert("", "end", values=valores)
                selected_dropdown.set(values_simulator[0])
                os_quantum_entry.delete(0, tk.END)
                os_quantum_entry.insert(0, values_simulator[1])
    else:
        # Add default values
        selected_dropdown.set("FCFS")
        os_quantum_entry.delete(0, tk.END)
        os_quantum_entry.insert(0, "2")
        tree.insert("", "end", values=["t01", "#ff0000", "0", "5", "1", "-"])

def validate_table(tree, quantum):
    # Validate quantum
    if not quantum.isdigit() or int(quantum) <= 0:
        messagebox.showerror("Error", f"Invalid quantum '{quantum}'. Must be a positive integer.")
        print(f"Error: Invalid quantum '{quantum}'. Must be a positive integer.")
        return False

    # Validate tasks
    task_rows = tree.get_children()
    if len(task_rows) == 0:
        messagebox.showerror("Error", "Task table is empty.")
        print("Error: Task table is empty.")
        return False

    color_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")

    task_ids = []
    for i, row_id in enumerate(task_rows, start=1):
        values = tree.item(row_id, "values")
        if len(values) != 6:
            messagebox.showerror("Error", f"Row {i} has incorrect number of columns ({len(values)}). Expected 6.")
            print(f"Error: Row {i} has incorrect number of columns ({len(values)}). Expected 6.")
            return False

        id_, color, arrival, duration, priority, events = values
    
        if not id_:
            messagebox.showerror("Error", f"Row {i}: ID is empty.")
            print(f"Error: Row {i}: ID is empty.")
            return False
        else:
            task_ids.append(id_)
            if id_[0] != 't' or not id_[1:].isdigit() or len(id_[1:]) != 2:
                messagebox.showerror("Error", f"Row {i}: Invalid ID '{id_}'. Must be in format 'tXX' where XX are two digits.")
                print(f"Error: Row {i}: Invalid ID '{id_}'. Must be in format 'tXX' where XX are two digits.")
                return False
        if not color_pattern.match(color):
            messagebox.showerror("Error", f"Row {i}: Invalid color '{color}'. Must be in #RRGGBB format.")
            print(f"Error: Row {i}: Invalid color '{color}'. Must be in #RRGGBB format.")
            return False

        for val, name in [(arrival, "arrival"), (duration, "duration"), (priority, "priority")]:
            if not val.isdigit() or int(val) < 0:
                messagebox.showerror("Error", f"Row {i}: Invalid '{name}' value '{val}'. Must be a non-negative integer.")
                print(f"Error: Row {i}: Invalid '{name}' value '{val}'. Must be a non-negative integer.")
                return False

        if events != "-" and not all(e.strip() for e in events.split(",")):
            messagebox.showerror("Error", f"Row {i}: Invalid event list '{events}'.")
            print(f"Error: Row {i}: Invalid event list '{events}'.")
            return False
    # Check for duplicate IDs
    if len(task_ids) != len(set(task_ids)): # set function removes duplicates
        messagebox.showerror("Error", "Duplicate task IDs found in the table.")
        print("Error: Duplicate task IDs found in the table.")
        return False
    print("Validation successful: all tables are valid.")
    return True

def validate_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found.")
        print("File not found.")
        return False

    if len(lines) < 2:
        messagebox.showerror("Error", "File too short. Make sure the file contains at least 2 lines.")
        print("File too short. Make sure the file contains at least 2 lines.")
        return False

    # First line (OS settings)
    primeira = lines[0].split(";")
    if len(primeira) != 2:
        messagebox.showerror("Error", "First line should contain 2 fields: algorithm and quantum.")
        print("First line should contain 2 fields: algorithm and quantum.")
        return False

    algoritmo, quantum = primeira
    if not algoritmo.isalpha():
        messagebox.showerror("Error", "Algorithm should only consist of letters.")
        print("Algorithm should only consist of letters.")
        return False
    if not quantum.isdigit() or int(quantum) <= 0:
        messagebox.showerror("Error", "Quantum must be a positive integer.")
        print("Quantum must be a positive integer.")
        return False
    task_ids = []
    # Other lines (tasks)
    padrao_cor = re.compile(r"^#[0-9a-fA-F]{6}$")
    for i, line in enumerate(lines[1:], start=2):
        partes = line.split(";")
        if len(partes) != 6:
            messagebox.showerror("Error", f"Line {i} should contain 6 fields: id, color, ingresso, duracao, prioridade, lista_eventos.")
            print(f"line {i}: not enough fields ({len(partes)}).")
            return False

        id_, cor, ingresso, duracao, prioridade, eventos = partes

        if not id_:
            messagebox.showerror("Error", f"Line {i}: ID is empty.")
            print(f"line {i}: ID empty.")
            return False
        else:
            task_ids.append(id_)
            if id_[0] != 't' or not id_[1:].isdigit() or len(id_[1:]) != 2:
                messagebox.showerror("Error", f"Line {i}: Invalid ID '{id_}'. Must be in format 'tXX' where XX are two digits.")
                print(f"Error: Row {i}: Invalid ID '{id_}'. Must be in format 'tXX' where XX are two digits.")
                return False
        if not padrao_cor.match(cor):
            messagebox.showerror("Error", f"Line {i}: Invalid color '{cor}'. Must be in #RRGGBB format.")
            print(f"line {i}: invalid color ({cor}).")
            return False
        for campo, nome in [(ingresso, "ingresso"), (duracao, "duracao"), (prioridade, "prioridade")]:
            if not campo.isdigit() or int(campo) < 0:
                messagebox.showerror("Error", f"Line {i}: Invalid '{nome}' value '{campo}'. Must be a non-negative integer.")
                print(f"line {i}: field '{nome}' invalid ({campo}).")
                return False
        # lista_eventos pode ser '-' ou lista separada por vírgulas
        if eventos != "-" and not all(e.strip() for e in eventos.split(",")):
            messagebox.showerror("Error", f"Line {i}: Invalid event list '{eventos}'.")
            print(f"line {i}: invalid event list ({eventos}).")
            return False
    # Check for duplicate IDs
    if len(task_ids) != len(set(task_ids)): # set function removes duplicates
        messagebox.showerror("Error", "Duplicate task IDs found in the table.")
        print("Error: Duplicate task IDs found in the table.")
        return False
    print("Valid file")
    return True

def load_external_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

def begin_simulation(os_simulator, window, chart_button, step_back_button, simulation_mode, tree, algorithm, quantum):
    print("Beginning simulation.")

    # Make sure data in tables is valid (user might have added invalid data through the GUI)
    if validate_table(tree, quantum):
        simulation_lines = []

        # Retrieve tasks
        for row_id in tree.get_children():
            simulation_lines.append(tree.item(row_id, "values"))

        # Retrieve algorithm and quantum and store into os_simulator
        os_simulator.algorithm = algorithm
        os_simulator.quantum = int(quantum)
        os_simulator.simulation_mode = simulation_mode.get()


        # Create task objects
        for line in simulation_lines:
            print('creating new task')
            mutexes = []
            if line[5] != "-":
                # parse event list
                event_list = [e.strip() for e in line[5].split(",")]
                for event in event_list:
                    print(f"event: {event}")
                    # mutex event format ex: ML00:01,MU00:03
                    if event.startswith("ML"):
                        match = re.match(r"ML(\d{2}):(\d+)", event)
                        if match:
                            mutex_id = int(match.group(1))
                            requisition_time = int(match.group(2))
                            mutex_event = cl.TaskMutexEvent(mutex_id, requisition_time, None)
                            mutexes.append(mutex_event)

                            if mutex_id not in [m.mutex_id for m in os_simulator.mutexes]:
                                os_simulator.mutexes.append(cl.Mutex(mutex_id))
                    elif event.startswith("MU"):
                        match = re.match(r"MU(\d{2}):(\d+)", event)
                        if match:
                            mutex_id = int(match.group(1))
                            duration = int(match.group(2))
                            for m in mutexes:
                                if m.mutex_id == mutex_id and m.duration is None:
                                    m.duration = duration  

            task = cl.Task(line[0], line[1], int(line[2]), int(line[3]), int(line[4]), mutexes)
            task.print_task()
            os_simulator.tasks.append(task)
            #os_simulator.ready_tasks.append(task)
            os_simulator.total_simulation_time += int(line[3])
        
        # sort tasks by name
        # lambda is a nameless function. t is the input. t.name[1:] is the output.
        os_simulator.tasks.sort(key=lambda t: t.name[1:])

        # Account for gaps between tasks
        earliest_start = None
        for task in os_simulator.tasks:
            if earliest_start is None or task.start < earliest_start.start:
                earliest_start = task
        os_simulator.total_simulation_time += earliest_start.start
        '''
        modules = {}
        for filename in os.listdir("./"):
            if filename.startswith("Scheduler_") and filename.endswith(".py"):
                name_module = filename[:-3]  # remove ".py"
                module = importlib.import_module(name_module)
                modules.update({name_module: module})
        print(modules)'''
            
        # create scheduler object
        if os_simulator.algorithm == "FCFS":
            os_simulator.scheduler = cl.Scheduler("FCFS", os_simulator.quantum)
        elif os_simulator.algorithm == "SRTF":
            os_simulator.scheduler = cl.Scheduler("SRTF", os_simulator.quantum)
        elif os_simulator.algorithm == "PRIO":
            os_simulator.scheduler = cl.Scheduler("PRIO", os_simulator.quantum)
        else:
            filename = os_simulator.algorithm + ".py"     # e.g. "Scheduler_FCFSNEW.py"
            fullpath = os.path.join(".", filename)

            module = load_external_module(os_simulator.algorithm, fullpath)
            print("External scheduler init")
            print(module)
            os_simulator.scheduler = module.Scheduler_ext(os_simulator.algorithm,  os_simulator.quantum)
            print(os_simulator.scheduler)

        #plot initial chart
        os_simulator.fig, os_simulator.ax = plt.subplots(figsize=(PLOT_INITIAL_WIDTH,PLOT_INITIAL_HEIGHT))
        os_simulator.ax.set_xlim(0, X_AXIS_MIN_LENGTH)
        os_simulator.ax.set_xticks(range(int(os_simulator.ax.get_xlim()[0]), int(os_simulator.ax.get_xlim()[1]) + 1))
        for x in range(int(os_simulator.ax.get_xlim()[0]), int(os_simulator.ax.get_xlim()[1]) + 1):
            os_simulator.ax.axvline(x=x, color="gray", linestyle=":", linewidth=0.8)
        for task in os_simulator.tasks:
            os_simulator.ax.barh(task.name, 0, left=0)
        os_simulator.canvas = FigureCanvasTkAgg(os_simulator.fig, master=window)
        os_simulator.widget = os_simulator.canvas.get_tk_widget()
        os_simulator.widget.pack(padx=10, pady=10)


        # Different behavior based on execution mode
        if simulation_mode.get() == MANUAL_EXECUTION:
            chart_button.pack(padx = 5, pady = 5)
            step_back_button.pack(padx = 5, pady = 5)
        elif simulation_mode.get() == AUTOMATIC_EXECUTION:
            while os_simulator.simulation_finished == False:
                os_simulator.step_forward(chart_button, step_back_button)

        return True

    else:
        return False