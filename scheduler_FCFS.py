import classes as cl

class Scheduler_ext(cl.Scheduler):
    def exec(self, tasks, current_time):
        print("Scheduler FCFS executing")
        self.current_task = self.step_FCFS(tasks, current_time)
        self.increment_time()
        return self.current_task