class Log:
    def __init__(self):
        for n in ["log.txt", "data.txt"]:
            with open(n, "w") as f:
                f.write("")
        self.data = []
        self.fs = open("log.txt", "ab", 0)

    def close(self):
        pass

    def write(self, text, level=0, data=False):
        if data:
            self.data.append(text)
            return

        if level < 2:
            self.fs.write(bytes("\n" * (2 - level), "utf-8"))
        self.fs.write(bytes("\t" * level + text + "\n", "utf-8"))

    def get_data(self):
        return self.data
