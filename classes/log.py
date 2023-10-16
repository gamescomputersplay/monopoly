''' Class to keep a log of the game
'''

class Log:

    def __init__(self, log_file_name="gamelog.txt"):
        self.log_file_name = log_file_name
        self.content = ""

    def add(self, data):
        ''' Add a line to a Log
        '''
        self.content += data + "\n"

    def save(self):
        ''' Write out the log
        '''
        with open(self.log_file_name, "a", encoding="utf-8") as logfile:
            logfile.write(self.content)

    def reset(self):
        ''' Empty the log file
        '''
        with open(self.log_file_name, "w", encoding="utf-8") as logfile:
            pass
