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
    last_saved_game = 0

    # Buffer for the games that finished fast,
    # to wait for other games to catch up 
    buffer = {}

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
        print("save", self.game_number)
        Log.buffer[self.game_number] = self.content
        Log.write_out_data()

    @classmethod
    def write_out_data(cls):
        ''' Write out logs, that are in buffer and in order
        '''
        print(Log.last_saved_game)
        Log.last_saved_game += 1

        # while Log.last_saved_game + 1 in Log.buffer:
        #     game_to_write = Log.last_saved_game + 1
        #     print("write", game_to_write)
        #     with Log.lock:
        #         with open(Log.log_file_name, "a", encoding="utf-8") as logfile:
        #             logfile.write(Log.buffer[game_to_write])
        #     del Log.buffer[game_to_write]
        #     Log.last_saved_game += 1
        #     print("last", game_to_write, Log.last_saved_game)


    def reset(self):
        ''' Empty the log file
        '''
        with self.lock:
            with open(self.log_file_name, "w", encoding="utf-8") as _:
                pass
