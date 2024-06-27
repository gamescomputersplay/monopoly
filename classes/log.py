''' Class to keep a log of the game.
Challenge here was to make it thread-safe: simulator plays several games at a time,
but the game log should be written by "whole game" chunks. This is the reason games
will not be in order, as the order games start is not the same as the order they finish.
'''

import multiprocessing

class Log:
    ''' Class to handle logging of game events
    '''

    # Lock is declare on the class level,
    # so it would be shared among processes
    lock = multiprocessing.Lock()

    def __init__(self, log_file_name="log.txt", disabled=False):
        self.log_file_name = log_file_name
        self.content = []
        self.disabled = disabled

    def add(self, data):
        ''' Add a line to a Log
        '''
        if self.disabled:
            return
        self.content.append(data)

    def save(self):
        ''' Write out the log
        '''
        if self.disabled:
            return
        with self.lock:
            with open(self.log_file_name, "a", encoding="utf-8") as logfile:
                logfile.write("\n".join(self.content))
                if self.content:
                    logfile.write("\n")

    def reset(self, first_line=""):
        ''' Empty the log file, write first_line if provided
        '''
        with self.lock:
            with open(self.log_file_name, "w", encoding="utf-8") as logfile:
                logfile.write(f"{first_line}\n")
