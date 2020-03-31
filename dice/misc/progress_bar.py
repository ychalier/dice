import threading
import queue
import time

class ProgressThread(threading.Thread):

    """
    Basic utility to show progress over an iterative task.
    """

    def __init__(self, q, total):
        super().__init__()
        self.q = q
        self.total = total
        self.current = 0

    def run(self):
        start = time.time()
        while True:
            try:
                while True:
                    self.current = self.q.get(block=False)
            except queue.Empty:
                pass
            elapsed = time.time() - start
            if self.current == self.total or self.current is None:
                break
            remaining = (float(self.total) * elapsed / (self.current + 1))\
                      - elapsed
            if self.current == 0:
                print("\rProgress: {} ({}%) | Elapsed: {} | Remaining: {}"
                      .format(self.current,
                              int(100 * float(self.current) / self.total),
                              time.strftime("%H:%M:%S", time.gmtime(elapsed)),
                              "--:--:--"),
                      end="")
            else:
                print("\rProgress: {} ({}%) | Elapsed: {} | Remaining: {}"
                      .format(self.current,
                              int(100 * float(self.current) / self.total),
                              time.strftime("%H:%M:%S", time.gmtime(elapsed)),
                              time.strftime("%H:%M:%S", time.gmtime(remaining))),
                      end="")
        print("\rProgress: {} (100%) | Elapsed: {} | Remaining: 00:00:00"
              .format(
                      self.total,
                      time.strftime("%H:%M:%S", time.gmtime(elapsed))))

class ProgressBar():

    def __init__(self, total):
        self.current = 0
        self.q = queue.Queue()
        self.thread = ProgressThread(self.q, total)

    def start(self):
        return self.thread.start()

    def increment(self):
        self.update(self.current + 1)

    def update(self, current):
        self.current = current
        self.q.put(current)

    def stop(self):
        self.q.put(None)
        self.thread.join()

    def iterate(iterable, callback, msg=None, length=None):
        if length is None:
            length = len(iterable)
        bar = ProgressBar(length)
        if msg is not None:
            print(msg)
        bar.start()
        for item in iterable:
            callback(item)
            bar.increment()
        bar.stop()
