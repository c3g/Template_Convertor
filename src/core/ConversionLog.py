
class ConversionLog:

    def __init__(self):
        pass

    def sampleSkipped(reason, rowNumber):
        # report a sample that was skipped, with the reason why
        print(f"{rowNumber} skipped: {reason}")