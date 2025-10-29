import tkinter as tk
from tkinter import ttk, filedialog
import file_upload as fu
import classes as cl
import sys
import matplotlib.pyplot as plt
from utils import *


simulator = cl.OS_Simulator()



# Root window initial setup
root = tk.Tk()
root.title("OS simulator")
root.minsize(1206, 500)
root.config(background=GUI_MAIN_COLOR)

def add_task():
    tree.insert("",
                "end", values=(
                    task_id_textbox.get("1.0", tk.END).strip(),
                    task_color_textbox.get("1.0", tk.END).strip(),
                    task_admission_textbox.get("1.0", tk.END).strip(),
                    task_duration_textbox.get("1.0", tk.END).strip(),
                    task_priority_textbox.get("1.0", tk.END).strip(),
                    task_event_list_textbox.get("1.0", tk.END).strip()
                ))


def remove_task():
    task_to_be_removed = remove_task_textbox.get("1.0", tk.END).strip()
    for row_id in tree.get_children():
        task = tree.item(row_id, "values")
        if task[0] == task_to_be_removed:
            tree.delete(row_id)

# Called after double-clicking on a cell
def edit_cell_simulator(event):
    fu.edit_cell(event, tree_simulator)

# Called after double-clicking on a cell
def edit_cell(event):
    fu.edit_cell(event, tree)

# Function called when closing the window
def on_close():
    width = root.winfo_width()
    height = root.winfo_height()
    print(width, height)
    plt.close('all') # Closes all matplotlib windows
    root.destroy()   # Closes Tkinter window
    sys.exit()       # Ensures the Python process stops

def upload_file():
    caminho = filedialog.askopenfilename(
        title="Upload config .txt file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not caminho:
        return
    print(caminho)
    
    no_config_button.pack_forget()
    upload_button.pack_forget()
    #path_label.pack_forget()
    #path_textbox.pack_forget()
    notebook.pack(expand=True, fill="both", padx=5, pady=5)
    begin_simulation_button.pack(padx=5, pady=5)
    fu.configure_file(caminho, tree, tree_simulator)

def no_config_file():
    upload_button.pack_forget()
    no_config_button.pack_forget()
    #path_label.pack_forget()
    #ath_textbox.pack_forget()
    notebook.pack(expand=True, fill="both", padx=5, pady=5)
    begin_simulation_button.pack(padx=5, pady=5)
    fu.configure_file("", tree, tree_simulator)


def begin_simulation():
    notebook.pack_forget()
    begin_simulation_button.pack_forget()
    reset_simulation_button.pack(padx=5, pady=5)
    result = fu.begin_simulation(simulator, image_frame, update_chart_button, general_settings_var, tree, tree_simulator)
    if not result:
        reset_simulation()
def reset_simulation():
    simulator.reset()
    update_chart_button.pack_forget()
    reset_simulation_button.pack_forget()
    notebook.pack_forget()
    task_id_textbox.delete("1.0", tk.END)
    task_color_textbox.delete("1.0", tk.END)
    task_admission_textbox.delete("1.0", tk.END)
    task_duration_textbox.delete("1.0", tk.END)
    task_priority_textbox.delete("1.0", tk.END)
    task_event_list_textbox.delete("1.0", tk.END)
    #path_label.pack(padx=5)
    #path_textbox.pack(padx=10, pady=10) 
    upload_button.pack(padx=5, pady=5)
    no_config_button.pack(padx=5, pady=5)


image = tk.PhotoImage(file="images/logo.png")

# Tools frame
tools_frame = tk.Frame(root, bg=GUI_TAB_COLOR)
tools_frame.pack(padx=5, pady=5, side=tk.LEFT, fill=tk.Y) 

tk.Label(
    tools_frame,
    text="OS scheduler simulator",
    bg=GUI_TAB_COLOR,
    width=50
).pack(padx=5, pady=5)

thumbnail_image = image.subsample(5, 5)
#tk.Label(tools_frame, image=thumbnail_image).pack(padx=5, pady=5)
"""
path_label = tk.Label(tools_frame, text=".txt config file inside config_files folder:", bg=GUI_TAB_COLOR)
path_label.pack(padx=5)
path_textbox = tk.Text(tools_frame, height=1, width=30)
path_textbox.insert(tk.END, "ex1")
path_textbox.pack(padx=10, pady=10) """

upload_button = tk.Button(tools_frame, text="Upload config file", command=upload_file)
upload_button.pack(padx=5, pady=5)
no_config_button = tk.Button(tools_frame, text="Begin from scratch", command=no_config_file)
no_config_button.pack(padx=5, pady=5)
begin_simulation_button = tk.Button(tools_frame, text="Begin simulation", 
                          command=begin_simulation)
reset_simulation_button = tk.Button(tools_frame, text = "Reset simulation", command=reset_simulation)
update_chart_button = tk.Button(tools_frame, text = "Update chart", 
                                command=lambda: simulator.update_chart())

# Tools and Filters tabs
notebook = ttk.Notebook(tools_frame)

# General settings tab
general_settings_tab = tk.Frame(notebook, bg=GUI_TAB_COLOR)
general_settings_var = tk.StringVar(value=MANUAL_EXECUTION)

manual_execution_button = tk.Radiobutton(
        general_settings_tab,
        text=MANUAL_EXECUTION,
        variable=general_settings_var,
        value=MANUAL_EXECUTION,
        bg=GUI_TAB_COLOR,
    )
manual_execution_button.pack(anchor="w", padx=20, pady=5)
automatic_execution_button = tk.Radiobutton(
        general_settings_tab,  
        text=AUTOMATIC_EXECUTION,
        variable=general_settings_var,
        value=AUTOMATIC_EXECUTION,
        bg=GUI_TAB_COLOR,
    )
automatic_execution_button.pack(anchor="w", padx=20, pady=5)

table_width = 1
# table for storing algorithm and quantum
frame_table_simulator = ttk.Frame(general_settings_tab)
frame_table_simulator.pack(fill=tk.BOTH, expand=True)
tree_simulator = ttk.Treeview(frame_table_simulator)
tree_simulator.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tree_simulator.bind("<Double-1>", edit_cell_simulator)
#scroll_y = ttk.Scrollbar(frame_table_simulator, orient=tk.VERTICAL, command=tree_simulator.yview)
#scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
#tree_simulator.configure(yscrollcommand=scroll_y.set)



notebook.add(general_settings_tab, text="General Settings")

# Tasks tab
tasks_tab = tk.Frame(notebook)
tasks_var = tk.StringVar(value="None")

# table for storing task configs
frame_table = ttk.Frame(tasks_tab, width=table_width)
frame_table.pack(fill=tk.BOTH, expand=True)
tree = ttk.Treeview(frame_table)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tree.bind("<Double-1>", edit_cell)
scroll_y = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=tree.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scroll_y.set)

add_task_frame = tk.Frame(tasks_tab)
add_task_frame.pack()
add_task_label = tk.Label(
    add_task_frame,
    text="Add task:"
)
add_task_label.pack(padx=5, pady=5)

task_id_color_frame = tk.Frame(add_task_frame)
task_id_color_frame.pack(anchor='w')
task_id_label = tk.Label(
    task_id_color_frame,
    text="Task ID: "
)
task_id_label.pack(padx=5, side="left")
task_id_textbox = tk.Text(task_id_color_frame, height=1, width=5)
task_id_textbox.pack(padx=5, side="left") 

task_color_label = tk.Label(
    task_id_color_frame,
    text="Task color: "
)
task_color_label.pack(padx=5, side="left")
task_color_textbox = tk.Text(task_id_color_frame, height=1, width=10)
task_color_textbox.pack(padx=5, side="left")

task_admission_duration_priority_frame = tk.Frame(add_task_frame)
task_admission_duration_priority_frame.pack(anchor='w')
task_admission_label = tk.Label(
    task_admission_duration_priority_frame,
    text="Task admission time: "
)
task_admission_label.pack(padx=5, pady=5, side="left")
task_admission_textbox = tk.Text(task_admission_duration_priority_frame, height=1, width=5)
task_admission_textbox.pack(padx=5, side="left")

task_duration_label = tk.Label(
    task_admission_duration_priority_frame,
    text="Task duration: "
)
task_duration_label.pack(padx=5, pady=5, side="left")
task_duration_textbox = tk.Text(task_admission_duration_priority_frame, height=1, width=5)
task_duration_textbox.pack(padx=5, side="left")

task_priority_label = tk.Label(
    task_admission_duration_priority_frame,
    text="Task priority: "
)
task_priority_label.pack(padx=5, pady=5, side="left")
task_priority_textbox = tk.Text(task_admission_duration_priority_frame, height=1, width=5)
task_priority_textbox.pack(padx=5, side="left")

task_event_list_frame = tk.Frame(add_task_frame)
task_event_list_frame.pack(anchor='w')
task_event_list_label = tk.Label(
    task_event_list_frame,
    text="Task event_list: "
)
task_event_list_label.pack(padx=5, pady=5, side="left")
task_event_list_textbox = tk.Text(task_event_list_frame, height=3, width=40)
task_event_list_textbox.pack(padx=10, side="right")

add_task_button = tk.Button(add_task_frame, text="Add task", command=add_task)
add_task_button.pack(padx=5, pady=5)

remove_task_frame = tk.Frame(tasks_tab)
remove_task_frame.pack()
remove_task_label = tk.Label(
    remove_task_frame,
    text="Remove task (enter task ID):"
)
remove_task_label.pack(padx=5, pady=5, side="left")
remove_task_textbox = tk.Text(remove_task_frame, height=1, width=5)
remove_task_textbox.pack(padx=10, pady=10, side="left") 
remove_task_button = tk.Button(remove_task_frame, text="Remove task", command=remove_task)
remove_task_button.pack(padx=5, pady=5)

'''for filter in ["Blurring", "Sharpening"]:
    tk.Radiobutton(
        tasks_tab,
        text=filter,
        variable=tasks_var,
        value=filter,
        bg="lightgreen",
    ).pack(anchor="w", padx=20, pady=5)'''
notebook.add(tasks_tab, text="Tasks")



# Image frame
image_frame = tk.Frame(root, bg=GUI_MAIN_COLOR)
image_frame.pack(padx=5, pady=5, side=tk.RIGHT, fill=tk.BOTH, expand=True)

display_image = image.subsample(2, 2)
'''
tk.Label(
    image_frame,
    text="Image",
    bg="grey",
    fg="white",
).pack(padx=5, pady=5)

tk.Label(image_frame, image=display_image).pack(padx=5, pady=5)
'''

# Make sure the program is terminated after closing the window
root.protocol("WM_DELETE_WINDOW", on_close)

# Initialize GUI
root.mainloop()

print("Terminating program")