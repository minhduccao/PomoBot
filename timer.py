from enum import Enum


class TimerStatus(Enum):
    STOPPED = -1
    PAUSED = 0
    RUNNING = 1


class Timer:
    def __init__(self):
        self.status = TimerStatus.STOPPED
        self.time_left = 0

    def start(self, duration: int):
        if self.status != TimerStatus.RUNNING:
            self.time_left = duration
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
            self.time_left = 0
            self.status = TimerStatus.STOPPED
            return True
        return False

    def tick(self, tick_duration=1):
        self.time_left -= tick_duration
        print('Time left: ', self.time_left)
        if self.time_left <= 0:
            self.status = TimerStatus.STOPPED
            print('Timer stopped')

    def get_status(self):
        return self.status

    def get_time(self):
        return self.time_left


