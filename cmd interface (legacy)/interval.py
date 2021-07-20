# from threading import Event, Thread

# class Interval(Thread):
#     def __init__(self, interval, func, *args, **kwargs):
#         Thread.__init__(self)

#         self.interval = interval
#         self.func = func
#         self.args = args
#         self.kwargs = kwargs
#         self.running = Event()

#     def start(self):
#         if not self.running.is_set():
#             self.running.set()
#             self.__run()

#     def __run(self):
#         while self.running.wait(1):
#             self.func(*self.args, **self.kwargs)

#     def stop(self):
#         self.running.clear()


from threading import Timer

class Interval(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

