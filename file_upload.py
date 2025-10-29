import classes as cl
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import *
import re

def edit_cell(event, tree):
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

def configure_file(filename, tree, tree_simulator):
    for item in tree.get_children():
            tree.delete(item)
    for item in tree_simulator.get_children():
        tree_simulator.delete(item)

    colunas_simulator = ["algorithm", "quantum"]
    tree_simulator["columns"] = colunas_simulator
    tree_simulator["show"] = "headings"

    colunas = ["id", "cor", "ingresso", "duracao", "prioridade", "lista_eventos"]
    tree["columns"] = colunas
    tree["show"] = "headings"

    for col in colunas:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=50, anchor="center")
    for col in colunas_simulator:
        tree_simulator.heading(col, text=col.capitalize())
        tree_simulator.column(col, width=100, anchor="center")
    # Check if data format is valid
    
    if filename != "":
        if validate_file(filename):
            with open(filename, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if filename != "":
                    for line in lines[1:]:
                        valores = line.split(";")
                        if len(valores) == len(colunas):
                            tree.insert("", "end", values=valores)
                    values_simulator = lines[0].split(";")
                    tree_simulator.insert("", "end", values=values_simulator)
    else:
        tree_simulator.insert("", "end", values=["-", "-"])

def validate_table(tree, tree_simulator):
    # ====== Validate simulator info ======
    sim_rows = tree_simulator.get_children()
    if len(sim_rows) == 0:
        print("Error: Simulator table is empty.")
        return False

    # Expect exactly one row (algorithm, quantum)
    sim_values = tree_simulator.item(sim_rows[0], "values")
    if len(sim_values) != 2:
        print("Error: Simulator table must contain two columns: algorithm and quantum.")
        return False

    algorithm, quantum = sim_values
    if not algorithm.isalpha():
        print(f"Error: Invalid algorithm '{algorithm}'. Must contain only letters.")
        return False
    if not quantum.isdigit() or int(quantum) <= 0:
        print(f"Error: Invalid quantum '{quantum}'. Must be a positive integer.")
        return False

    # ====== Validate tasks ======
    task_rows = tree.get_children()
    if len(task_rows) == 0:
        print("Error: Task table is empty.")
        return False

    color_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")

    for i, row_id in enumerate(task_rows, start=1):
        values = tree.item(row_id, "values")
        if len(values) != 6:
            print(f"Error: Row {i} has incorrect number of columns ({len(values)}). Expected 6.")
            return False

        id_, color, arrival, duration, priority, events = values

        if not id_:
            print(f"Error: Row {i}: ID is empty.")
            return False

        if not color_pattern.match(color):
            print(f"Error: Row {i}: Invalid color '{color}'. Must be in #RRGGBB format.")
            return False

        for val, name in [(arrival, "arrival"), (duration, "duration"), (priority, "priority")]:
            if not val.isdigit() or int(val) < 0:
                print(f"Error: Row {i}: Invalid '{name}' value '{val}'. Must be a non-negative integer.")
                return False

        if events != "-" and not all(e.strip() for e in events.split(",")):
            print(f"Error: Row {i}: Invalid event list '{events}'.")
            return False

    print("Validation successful: all tables are valid.")
    return True

def validate_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("File not found.")
        return False

    if len(lines) < 2:
        print("File too short. Make sure the file contains at least 2 lines.")
        return False

    # First line (OS settings)
    primeira = lines[0].split(";")
    if len(primeira) != 2:
        print("First line should contain 2 fields: algorithm and quantum.")
        return False

    algoritmo, quantum = primeira
    if not algoritmo.isalpha():
        print("Algorithm should only consist of letters.")
        return False
    if not quantum.isdigit() or int(quantum) <= 0:
        print("Quantum must be a positive integer.")
        return False

    # Other lines (tasks)
    padrao_cor = re.compile(r"^#[0-9a-fA-F]{6}$")
    for i, line in enumerate(lines[1:], start=2):
        partes = line.split(";")
        if len(partes) != 6:
            print(f"line {i}: not enough fields ({len(partes)}).")
            return False

        id_, cor, ingresso, duracao, prioridade, eventos = partes

        if not id_:
            print(f"line {i}: ID empty.")
            return False
        if not padrao_cor.match(cor):
            print(f"line {i}: invalid color ({cor}).")
            return False
        for campo, nome in [(ingresso, "ingresso"), (duracao, "duracao"), (prioridade, "prioridade")]:
            if not campo.isdigit() or int(campo) < 0:
                print(f"line {i}: field '{nome}' invalid ({campo}).")
                return False
        # lista_eventos pode ser '-' ou lista separada por vírgulas
        if eventos != "-" and not all(e.strip() for e in eventos.split(",")):
            print(f"line {i}: invalid event list ({eventos}).")
            return False

    print("Valid file")
    return True

def begin_simulation(os_simulator, window, chart_button, simulation_mode, tree, tree_simulator):
    print("Beginning simulation.")
    # Make sure data in tables is valid (user might have added invalid data through the GUI)
    if validate_table(tree, tree_simulator):
        simulation_lines = []

        # Retrieve tasks
        for row_id in tree.get_children():
            simulation_lines.append(tree.item(row_id, "values"))

        # Retrieve algorithm and quantum and store into os_simulator
        os_data = []
        os_data = tree_simulator.item(tree_simulator.get_children()[0], "values")
        print(os_data)
        os_simulator.algorithm = os_data[0]
        os_simulator.quantum = int(os_data[1])
        os_simulator.simulation_mode = simulation_mode.get()


        # Create task objects
        for line in simulation_lines:
            print('creating new task')
            task = cl.Task(line[0], line[1], int(line[2]), int(line[3]), int(line[4]), line[5])
            print(task.name)
            os_simulator.tasks.append(task)
            os_simulator.total_simulation_time += int(line[3])
        
        # Account for gaps between tasks
        earliest_start = None
        for task in os_simulator.tasks:
            if earliest_start is None or task.start < earliest_start.start:
                earliest_start = task
        os_simulator.total_simulation_time += earliest_start.start
        
        # create scheduler object
        if os_simulator.algorithm == "FCFS":
            os_simulator.scheduler = cl.Scheduler("FCFS", os_simulator.quantum)
        elif os_simulator.algorithm == "SRTF":
            os_simulator.scheduler = cl.Scheduler("SRTF", os_simulator.quantum)
        elif os_simulator.algorithm == "PRIO":
            os_simulator.scheduler = cl.Scheduler("PRIO", os_simulator.quantum)

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
            print("im here")
            chart_button.pack(padx = 5, pady = 5)
        elif simulation_mode.get() == AUTOMATIC_EXECUTION:
            while os_simulator.simulation_finished == False:
                os_simulator.update_chart()

        return True

    else:
        messagebox.showerror("Error", "Please make sure the table contains only valid data")
        return False