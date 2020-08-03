from enum import Enum


class TimerStatus(Enum):
    STOPPED = -1
    PAUSED = 0
    RUNNING = 1


class Timer:
    def __init__(self):
        self.status = TimerStatus.STOPPED

    def start(self):
        if self.status != TimerStatus.RUNNING:
            self.status = TimerStatus.RUNNING
            return True
        return False

    def pause(self):
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED
            return True
        return False

    def resume(self):
        if self.status == TimerStatus.PAUSED:
            self.status = TimerStatus.RUNNING
            return True
        return False

    def stop(self):
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.STOPPED
            return True
        return False

    def get_status(self):
        return self.status


