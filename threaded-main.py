

class ThreadedMain:
    def __init__(self):
        self.var = 0


    def run(self):
        self.var += 1
        print(self.var)
