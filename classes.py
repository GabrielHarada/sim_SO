import queue as q
from utils import *
from tkinter import messagebox
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
        print("scheduler exec")
        if self.algorithm == "FCFS":
            self.current_task = self.step_fcfs(tasks, current_time)
        elif self.algorithm == "SRTF":
            self.current_task = self.step_srtf(tasks, current_time)
        elif self.algorithm == "PRIO":
            self.current_task = self.step_PRIO(tasks, current_time)
        self.increment_time()
        return self.current_task

        
    def increment_time(self):
        # Increment quantum timer. Reset if necessary
        self.quantum_timer = self.quantum_timer + 1
        if self.quantum == self.quantum_timer:
            print("Resetting quantum timer")
            self.quantum_timer = 0
            self.preemption_flag = True
        else:
            self.preemption_flag = False

    
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
                print("TASK FINISHED")
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
    
    def step_fcfs(self, tasks, current_time):
        print("fcfs step")
        print("Ready tasks:")
        for t in tasks:
            print(t.name)
        if not self.preemption_flag:
            print("no preemption")
            if self.current_task is not None:
                print(f"current task: {self.current_task.name}")
                if self.current_task.end != float('inf'): # if finished
                    print(f"task {self.current_task.name} finished")
                    self.quantum_timer = 0
            self.current_task = tasks[0] if tasks else None
            return self.current_task
        else:
            print("preemption")
            if len(tasks) == 0:
                return None
            if self.current_task is not None:
                print(f"current task: {self.current_task.name}")
            if self.current_task.end == float('inf'): # if not finished
                # Rotate the list to simulate FCFS with preemption
                old_task = tasks.pop(0)
                print(f"old task: {old_task.name}")
                print(f"preempting task: {old_task.name}")
                tasks.append(old_task)
                self.current_task = tasks[0]
                return self.current_task if tasks else None
            else: #task finished, such that it is no longer in the ready queue
                print(f"task {self.current_task.name} finished")
                self.quantum_timer = 0
                self.current_task = tasks[0]
                return self.current_task if tasks else None
            '''if self.current_task.end == float('inf'): # if not finished
                # Rotate the list to simulate FCFS with preemption
                old_task = tasks.pop(0)
                print(f"old task: {old_task.name}")
                print(f"preempting task: {old_task.name}")
                tasks.append(old_task)
                return tasks[0] if tasks else None
            else: #task finished, such that it is no longer in the ready queue
                print(f"task {old_task.name} finished")
                return tasks[0] if tasks else None'''

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
                print(f"Task {self.current_task.name} to finish at time {self.current_task.end + 1}")

        print(f"SRTF selected - running: {self.current_task.name if self.current_task else 'None'}")
        return self.current_task
    
    def step_srtf(self, tasks, current_time):
        print("srtf step")
        print("Ready tasks:")
        for t in tasks:
            print(t.name)
        srtf_list = tasks.copy()
        srtf_list.sort(key=lambda t: t.duration - len(t.moments_in_execution))
        return srtf_list[0] if srtf_list else None

    def step_PRIO(self, tasks, current_time):
        print("prio step")
        print("Ready tasks:")
        for t in tasks:
            print(t.name)
        prio_list = tasks.copy()
        prio_list.sort(key=lambda t: t.priority, reverse=True)
        return prio_list[0] if prio_list else None

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
        # Remove tasks which might have been suspended
        for t in ready_list:
            if t not in tasks:
                print(f"Removing suspended task from ready list: {t.name}")
                ready_list.remove(t)

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
            #self.current_task.moments_in_execution.append(current_time)
            self.current_task.remaining_time -= 1

            if self.current_task.remaining_time <= 0:
                self.current_task.end = current_time + 1
                print(f"Task {self.current_task.name} to finish at time {self.current_task.end + 1}")

        print(f"PRIORITY selected - running: {self.current_task.name if self.current_task else 'None'}")
        return self.current_task

class OS_Simulator:
    def __init__(self):
        self.algorithm = ""
        self.quantum = 0
        self.tasks = []
        self.ready_tasks = []
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
        self.simulation_moment = 0

        # Events
        self.mutexes = []


    # show messagebox with task data
    def show_task_data(self, task_id):
        for task in self.tasks:
            if task.name == task_id:
                task.show_info()
                return
        messagebox.showerror("Error", f"Task {task_id} not found.")

    def reset(self):
        print("Resetting OS simulator")
        self.algorithm = ""
        self.quantum = 0
        self.tasks = []
        self.ready_tasks = []
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
        self.simulation_moment = 0
        self.current_task = None
        self.total_simulation_time = 0
        self.finished_tasks = []
        self.simulation_finished = False
        self.simulation_mode = ""

        self.mutexes = []

        for t in self.tasks:
            if hasattr(t, "remaining_time"):
                delattr(t, "remaining_time")
        
    # print OS_Simulator data
    def print_self(self):
        print(f"Algorithm: {self.algorithm}, Quantum: {self.quantum}")
        for task in self.tasks:
            print(f"Task: {task.name}, Color: {task.color}, Start: {task.start}, Duration: {task.duration}, Priority: {task.priority}, Events: {task.event_list}")


    def plot_chart(self):
        if self.simulation_mode == MANUAL_EXECUTION or len(self.finished_tasks) == len(self.tasks):
            self.ax.clear()
            self.ax.set_xlim(0, max(X_AXIS_MIN_LENGTH, self.simulation_moment + 1))
            self.ax.set_xticks(range(int(self.ax.get_xlim()[0]), int(self.ax.get_xlim()[1]) + 1))
            # grid lines
            for x in range(int(self.ax.get_xlim()[0]), int(self.ax.get_xlim()[1]) + 1):
                self.ax.axvline(x=x, color="gray", linestyle=":", linewidth=0.8)
            for task in self.tasks:
                self.ax.barh(task.name, 0, left=0)
                for i in range(self.simulation_moment):
                    # if task was executing at time i
                    if i in task.moments_in_execution:
                        self.ax.barh(task.name, 1, left=i, color=task.color, edgecolor="black")
                    # if task was not executing at time i but has started
                    elif i >= task.start and i < task.end:
                        self.ax.barh(task.name, 1, left=i, color="white", edgecolor="black")
            self.canvas.draw()

    def step_forward(self, step_forward_button, step_back_button):
        print("Stepping forward.")
        print("current time: " + str(self.current_time))
        print("simulation moment: " + str(self.simulation_moment))
        if self.current_time == self.simulation_moment:
            print("At current time. Executing one step.")
            self.update_chart(step_forward_button, step_back_button)
        elif self.simulation_moment < self.current_time:
            print("In the past. Moving forward one step.")
            self.simulation_moment += 1
            self.plot_chart()
        print()

    def step_back(self):
        print("Stepping back.")
        print("current time: " + str(self.current_time))
        print("simulation moment: " + str(self.simulation_moment))
        if self.simulation_moment == 0:
            print("Already at time 0, cannot step back.")
        else:    
            self.simulation_moment -= 1
        
        self.plot_chart()
        print()
    
    def update_chart(self, update_chart_button, step_back_button):
        for t in self.tasks:
            if t.start == self.current_time and t not in self.ready_tasks and t not in self.finished_tasks:
                print(f"Adding task {t.name} to ready tasks")
                self.ready_tasks.append(t)
        print("Ready tasks at time " + str(self.current_time) + ":")
        for t in self.ready_tasks:
            print(t.name)
        next_task = self.scheduler.exec(self.ready_tasks, self.current_time)
        if next_task is not None:    
            print("Executing task: ")
            for event in next_task.event_list:
                if isinstance(event, TaskMutexEvent):
                    if event.mutex_id in [m.mutex_id for m in self.mutexes]:
                        mutex = None
                        for mu in self.mutexes:
                            if mu.mutex_id == event.mutex_id:
                                mutex = mu
                        # Check if the task is requesting the mutex at this time
                        if event.requisition_time == len(next_task.moments_in_execution):
                            if mutex.locked_by is None or mutex.locked_by == next_task:
                                print(f"Task {next_task.name} acquiring mutex {mutex.mutex_id}")
                                mutex.locked_by = next_task
                                mutex.lock_time_remaining = event.duration
                                mutex.lock_time_remaining -= 1
                                print(f"mutex time remaining: {mutex.lock_time_remaining}")
                            else:
                                print(f"Task {next_task.name} waiting for mutex {mutex.mutex_id} (currently locked by {mutex.locked_by.name})")
                                self.ready_tasks.remove(next_task)
                                self.scheduler.quantum_timer = 0
                                mutex.waiting_tasks_queue.put(next_task)
                                self.update_chart(update_chart_button, step_back_button)
                                return
                        # Check if the task is done with the mutex
                        elif mutex.locked_by == next_task:
                            if mutex.lock_time_remaining > 0:
                                mutex.lock_time_remaining -= 1
                                print(f"Task {next_task.name} holding mutex {mutex.mutex_id}, time remaining: {mutex.lock_time_remaining}")
                            if mutex.lock_time_remaining == 0:
                                print(f"Task {next_task.name} releasing mutex {mutex.mutex_id}")
                                mutex.locked_by = None
                                # place one suspended task back in ready list
                                if not mutex.waiting_tasks_queue.empty():
                                    waiting_task = mutex.waiting_tasks_queue.get()
                                    print(f"Task {waiting_task.name} acquiring mutex {mutex.mutex_id} from waiting queue")
                                    mutex.locked_by = waiting_task
                                    # Find the corresponding event to set lock_time_remaining
                                    for ev in waiting_task.event_list:
                                        if isinstance(ev, TaskMutexEvent) and ev.mutex_id == mutex.mutex_id:
                                            mutex.lock_time_remaining = ev.duration
                                    self.ready_tasks.append(waiting_task)
            next_task.moments_in_execution.append(self.current_time)
            next_task.print_task()
        # increment time
        if len(self.finished_tasks) < len(self.tasks):
            self.current_time += 1
            self.simulation_moment += 1
        if next_task is not None:
            # Check if the task just finished
            if hasattr(next_task, "remaining_time"):  # For SRTF or similar algorithms
                if next_task.remaining_time == 0 and next_task not in self.finished_tasks:
                    next_task.end = self.current_time
                    self.finished_tasks.append(next_task)
                    self.ready_tasks.remove(next_task)
            else:  # For FCFS or non-preemptive algorithms
                if len(next_task.moments_in_execution) == next_task.duration:
                    print("TASK" + next_task.name + "FINISHED")
                    next_task.end = self.current_time
                    self.finished_tasks.append(next_task)
                    self.ready_tasks.remove(next_task)
    
        self.plot_chart()

        # Check if simulation is finished
        if len(self.finished_tasks) == len(self.tasks):
            update_chart_button.pack_forget()
            step_back_button.pack_forget()
            print("Simulation finished")
            if self.simulation_finished == False:
                if not os.path.isdir("./image_output"):
                    os.makedirs("./image_output")
                    print("creating dir")
                self.fig.savefig("image_output/output.png")
                print("Saving image")
                messagebox.showinfo("Simulation finished!", "Simulation finished! The output image has been saved as ./image_output/output.png")

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
    
    def print_task(self):
        print(f"Task: {self.name}, Color: {self.color}, Start: {self.start}, Duration: {self.duration}, Priority: {self.priority}")
        print(f"Event list: ", end="")
        for event in self.event_list:
            event.print_event()
        print(f"Moments in execution: {self.moments_in_execution}, End: {self.end}")
    
    def show_info(self):
        unique_moments = list(set(self.moments_in_execution))
        unique_moments.sort(key=int)
        info = f"Task Name: {self.name}\n"
        info += f"Color: {self.color}\n"
        info += f"Start Time: {self.start}\n"
        info += f"Duration: {self.duration}\n"
        info += f"Priority: {self.priority}\n"
        info += f"Event List: {self.event_list}\n"
        info += f"Moments in Execution: {unique_moments}\n"
        info += f"End Time: {self.end}\n"
        messagebox.showinfo("Task Information", info)

class TaskMutexEvent:
    def __init__(self, mutex_id, requisition_time, duration):
        self.mutex_id = mutex_id
        self.requisition_time = requisition_time
        self.duration = duration
        self.lock_time_remaining = duration  # Time remaining for the lock to be released
    def print_event(self):
        print(f"Mutex ID: {self.mutex_id}, Requisition Time: {self.requisition_time}, Duration: {self.duration}")
    
class Mutex:
    def __init__(self, mutex_id):
        self.mutex_id = mutex_id
        self.locked_by = None  # Task that currently holds the mutex
        self.waiting_tasks_queue = q.Queue()