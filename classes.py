import queue as q
from utils import *
import os


class Scheduler:
    def __init__(self, algorithm, quantum):
        self.algorithm = algorithm
        self.current_task = None
        self.quantum = quantum
        self.quantum_timer = 0
        self.preemption_flag = False

        # Variables for FCFS algorithm
        self.execution_queue = q.Queue()
    
    def reset(self):
        print("Resetting scheduler")
        self.algorithm = None
        self.current_task = None
        self.quantum = None
        self.quantum_timer = 0
        self.preemption_flag = False

        self.execution_queue = q.Queue()

    # Execute 1 step of the simulation
    def exec(self, tasks, current_time):
        if self.algorithm == "FCFS":
            self.current_task = self.step_FCFS(tasks, current_time)
        elif self.algorithm == "SRTF":
            self.current_task = self.step_SRTF(tasks, current_time)
        elif self.algorithm == "PRIO":
            self.current_task = self.step_Priority(tasks, current_time)

        self.quantum_timer = self.quantum_timer + 1
        if self.quantum_timer == self.quantum:
            self.quantum_timer = 0
            self.preemption_flag = True
        else:
            self.preemption_flag = False

        return self.current_task
    
    # Step functions should return the task to be executed
    def step_FCFS(self, tasks, current_time):
        # Enqueue tasks starting at current_time

        # List to store tasks starting at current_time
        new_tasks = []
        for task in tasks:
            if task.start == current_time:
                new_tasks.append(task)
        # Enqueue tasks in ascending order of their indexes
        while len(new_tasks) > 0:
            earliest = None
            for task in new_tasks:
                if earliest is None:
                    earliest = task
                else:
                    if int(task.name[1:]) < int(earliest.name[1:]):
                        earliest = task
            new_tasks.remove(earliest)
            print("enqueuing task: " + earliest.name)
            self.execution_queue.put(earliest)
        
        # If the queue is not empty but there is no current task.
        if not self.execution_queue.empty():
            if self.current_task is None:
                self.current_task = self.execution_queue.get()
        else:
            print("empty queue")
        
        if self.current_task is not None:
            # Verificar se a tarefa ja acabou
            if self.current_task.end != float('inf'):
                # Reset quantum timer
                self.quantum_timer = 0
                # Se ha tarefas para serem executadas na fila
                if not self.execution_queue.empty():
                    self.current_task = self.execution_queue.get()
                else:
                    self.current_task = None
            elif self.preemption_flag:
                print("PREEMPTION")
                self.execution_queue.put(self.current_task)
                self.current_task = self.execution_queue.get()

                
        print("FCFS selected")

        print('returning: ' + self.current_task.name if self.current_task else "returning None")
        return self.current_task

    def step_SRTF(self, tasks, current_time):
        # Initialize remaining_time for new tasks if not already done
        for t in tasks:
            if t.start == current_time and not hasattr(t, "remaining_time"):
                t.remaining_time = t.duration

        # Add any newly arrived tasks to ready queue
        new_tasks = [t for t in tasks if t.start == current_time]
        for t in new_tasks:
            print(f"enqueuing new task: {t.name}")
            self.execution_queue.put(t)

        # Rebuild the ready queue as a list to allow sorting
        ready_list = []
        while not self.execution_queue.empty():
            ready_list.append(self.execution_queue.get())

        # If current task exists and has remaining time > 0, put it back in the list
        if self.current_task is not None and self.current_task.remaining_time > 0:
            ready_list.append(self.current_task)

        # Remove finished tasks
        ready_list = [t for t in ready_list if t.remaining_time > 0]

        # Sort by shortest remaining time
        ready_list.sort(key=lambda x: x.remaining_time)

        # Pick the next task
        if len(ready_list) > 0:
            next_task = ready_list[0]
        else:
            next_task = None

        # Save back to queue
        for t in ready_list:
            self.execution_queue.put(t)

        if next_task != self.current_task:
            if self.current_task is not None and next_task is not None:
                print(f"Preempting {self.current_task.name} for {next_task.name}")
            elif self.current_task is not None and next_task is None:
                print(f"Task {self.current_task.name} completed, no next task.")
            self.current_task = next_task

        # Decrease remaining time of the current task
        if self.current_task is not None:
            self.current_task.remaining_time -= 1
            if self.current_task.remaining_time == 0:
                self.current_task.end = current_time + 1
                print(f"Task {self.current_task.name} finished at time {self.current_task.end}")

        print(f"SRTF selected - running: {self.current_task.name if self.current_task else 'None'}")
        return self.current_task
    
    def step_Priority(self, tasks, current_time):
        # Add newly arrived tasks
        for t in tasks:
            if t.start == current_time:
                print(f"Enqueuing task: {t.name} (priority {t.priority})")
                if not hasattr(t, "remaining_time"):
                    t.remaining_time = t.duration
                self.execution_queue.put(t)

        # Build a list from the queue
        ready_list = []
        while not self.execution_queue.empty():
            ready_list.append(self.execution_queue.get())

        # Reinsert current task if still running and not finished
        if self.current_task is not None and self.current_task.end == float('inf') and self.current_task not in ready_list:
            ready_list.append(self.current_task)

        # Remove finished tasks
        ready_list = [t for t in ready_list if t.end == float('inf')]

        # Sort by priority (higher = more important)
        ready_list.sort(key=lambda t: t.priority, reverse=True)

        # Select next task
        next_task = ready_list[0] if ready_list else None

        # Restore the ready queue
        for t in ready_list:
            self.execution_queue.put(t)

        # Handle preemption
        if next_task != self.current_task:
            if self.current_task is not None and next_task is not None:
                print(f"Preempting {self.current_task.name} for {next_task.name}")
            elif self.current_task is not None and next_task is None:
                print(f"Task {self.current_task.name} completed, no next task.")
            self.current_task = next_task

        # Execute 1 time unit
        if self.current_task is not None:
            self.current_task.moments_in_execution.append(current_time)
            self.current_task.remaining_time -= 1

            if self.current_task.remaining_time <= 0:
                self.current_task.end = current_time + 1
                print(f"Task {self.current_task.name} finished at time {self.current_task.end}")

        print(f"PRIORITY selected - running: {self.current_task.name if self.current_task else 'None'}")
        return self.current_task

class OS_Simulator:
    def __init__(self):
        self.algorithm = ""
        self.quantum = 0
        self.tasks = []
        self.scheduler = None

        # Variables used for plotting the chart
        self.fig = None
        self.ax = None
        self.canvas = None
        self.widget = None
        self.df = None

        # Variables used for the simulation
        self.current_time = 0
        self.current_task = None
        self.total_simulation_time = 0
        self.finished_tasks = []
        self.simulation_finished = False
        self.simulation_mode = ""


    def reset(self):
        print("Resetting OS simulator")
        self.algorithm = ""
        self.quantum = 0
        self.tasks = []
        if self.scheduler is not None:
            self.scheduler.reset()
        self.fig = None
        self.ax = None
        self.canvas = None
        if self.widget is not None:
            self.widget.pack_forget()
            self.widget = None
        self.df = None

        self.current_time = 0
        self.current_task = None
        self.total_simulation_time = 0
        self.finished_tasks = []
        self.simulation_finished = False
        self.simulation_mode = ""

        for t in self.tasks:
            if hasattr(t, "remaining_time"):
                delattr(t, "remaining_time")
        
    def print_self(self):
        print(f"Algorithm: {self.algorithm}, Quantum: {self.quantum}")
        for task in self.tasks:
            print(f"Task: {task.name}, Color: {task.color}, Start: {task.start}, Duration: {task.duration}, Priority: {task.priority}, Events: {task.event_list}")


    def update_chart(self):
        print("current time: " + str(self.current_time))
        next_task = self.scheduler.exec(self.tasks, self.current_time)
        if next_task is not None:    
            print("Executing task")
            next_task.moments_in_execution.append(self.current_time)
        # increment time
        if len(self.finished_tasks) < len(self.tasks):
            self.current_time += 1
        if next_task is not None:
            # Check if the task just finished
            if hasattr(next_task, "remaining_time"):  # For SRTF or similar algorithms
                if next_task.remaining_time == 0 and next_task not in self.finished_tasks:
                    next_task.end = self.current_time
                    self.finished_tasks.append(next_task)
            else:  # For FCFS or non-preemptive algorithms
                if len(next_task.moments_in_execution) == next_task.duration:
                    next_task.end = self.current_time
                    self.finished_tasks.append(next_task)
    
        # plot chart
        if self.simulation_mode == MANUAL_EXECUTION or len(self.finished_tasks) == len(self.tasks):
            print("simulation mode")
            self.ax.clear()
            self.ax.set_xlim(0, max(X_AXIS_MIN_LENGTH, self.current_time + 1))
            self.ax.set_xticks(range(int(self.ax.get_xlim()[0]), int(self.ax.get_xlim()[1]) + 1))
            for x in range(int(self.ax.get_xlim()[0]), int(self.ax.get_xlim()[1]) + 1):
                self.ax.axvline(x=x, color="gray", linestyle=":", linewidth=0.8)
            for task in self.tasks:
                self.ax.barh(task.name, 0, left=0)
                for i in range(self.current_time):
                    if i in task.moments_in_execution:
                        self.ax.barh(task.name, 1, left=i, color=task.color, edgecolor="black")
                    elif i >= task.start and i < task.end:
                        self.ax.barh(task.name, 1, left=i, color="white", edgecolor="black")
            self.canvas.draw()

        if len(self.finished_tasks) == len(self.tasks):
            print("Simulation finished")
            if self.simulation_finished == False:
                if not os.path.isdir("./image_output"):
                    os.makedirs("./image_output")
                    print("creating dir")
                self.fig.savefig("image_output/output.png")
                print("Saving image")
            self.simulation_finished = True
        
        print()

class Task:
    def __init__(self, name, color, start, duration, priority, event_list):
        self.name = name
        self.color = color
        self.start = start
        self.duration = duration
        self.priority = priority
        self.event_list = event_list

        self.moments_in_execution = []
        self.end = float('inf')