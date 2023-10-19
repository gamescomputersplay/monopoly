''' Class to keep a log of the game
'''

import multiprocessing

class Log:
    ''' Class to handle logging of game events
    '''

    # Lock is declare on the class level,
    # so it would be shared among processes
    lock = multiprocessing.Lock()

    # Filename to write game log to
    log_file_name = "gamelog.txt"

    # Last game that was saved into the file
    last_saved_part = 0

    # Buffer for the games that finished fast,
    # to wait for other games to catch up
    with lock:
        buffer = {}

    @classmethod
    def write_out_data(cls):
        ''' Write out logs, that are in buffer and in order
        '''
        print(cls.last_saved_part, list(cls.buffer.keys()))
        while cls.last_saved_part + 1 in cls.buffer:
            part_to_write = cls.last_saved_part + 1
            print("write", part_to_write)

            with cls.lock:
                with open(cls.log_file_name, "a", encoding="utf-8") as logfile:
                    logfile.write(cls.buffer[part_to_write])

            del cls.buffer[part_to_write]
            with cls.lock:
                cls.last_saved_part = part_to_write
            print("last", part_to_write, cls.last_saved_part)

    def __init__(self, game_number):
        self.game_number = game_number
        self.content = ""

    def add(self, data):
        ''' Add a line to a Log
        '''
        self.content += data + "\n"

    def save(self):
        ''' Add the content to the output buffer.
        Attempt to write out the buffer.
        '''
        with Log.lock:
            Log.buffer[self.game_number] = self.content
        Log.write_out_data()

    def reset(self):
        ''' Empty the log file
        '''
        with self.lock:
            with open(self.log_file_name, "w", encoding="utf-8") as _:
                pass
