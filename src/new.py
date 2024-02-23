import multiprocessing
from manage_crawl import Update 
import asyncio
from task_manage import TaskManager

class ProcessManager:
    def __init__(self):
        self.processes = []

    def add_process(self, target, args=()):
        process = multiprocessing.Process(target=target, args=args)
        self.processes.append(process)

    def start_all_processes(self):
        for process in self.processes:
            process.start()

    def join_all_processes(self):
        for process in self.processes:
            process.join()

    def clear_processes(self):
        self.processes = []

def auto_update():
    crawl_update = Update()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl_update.run())
    loop.close()
    

def crawl():
    task_manager = TaskManager()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task_manager.start())
    loop.close()
    asyncio.run()

if __name__ == '__main__':

    manager = ProcessManager()
    manager.add_process(auto_update)
    manager.add_process(crawl)

    manager.start_all_processes()
    manager.join_all_processes()

    print("All processes completed")