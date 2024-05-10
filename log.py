import os
class Log:
    def __init__(self):
        self.message = ""
    
    def init():
        directory = os.getcwd()
        Log.logger = Log()

    def final():
        directory = os.listdir()
        
        filterLogs = lambda filename: filename[0:3] == "log" and filename[-4:] == ".txt" and len(filename) >= 8
        
        files = list(filter(filterLogs, directory))
        currentNumber = 0
        numberFound = False
        while not numberFound:
            if currentNumber >= len(files):
                numberFound = True
                break
            file = files[currentNumber]
            numberRangeStart = 3
            numberRangeEnd = file.find(".txt")
            if int(file[numberRangeStart:numberRangeEnd]) != currentNumber:
                numberFound = True
                break
            currentNumber += 1
        
        logFile = f"log{currentNumber}.txt"
        
        with open(logFile, "w") as log:
            log.write(Log.logger.message)
    
    def addMessage(self, strings, prints, logs):
        message = ""
        for string in strings:
            message += string.__str__() + " "
        if prints:
            print(message)
        message += "\n"
        if logs:
            self.message += message

def log(*strings, prints = True, logs = True):
    logger = Log.logger
    logger.addMessage(strings, prints, logs)
    
Log.init()

