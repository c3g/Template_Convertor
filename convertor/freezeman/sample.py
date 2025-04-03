# A record container the sample data to be exported to the freezeman template
class FreezemanSample:
    def __init__(self):
        self.kind = ""
        self.name = ""
        self.project = ""
        self.cohort = ""
        self.experimentalGroup = ""
        self.taxon = ""
        self.sampleCoord = ""
        self.containerKind = ""
        self.containerName = ""
        self.containerBarcode = ""
        self.containerCoord = ""
        self.individualName = ""
        self.sex = ""
        self.volume = ""
        self.concentration = ""
        self.collectionSite = ""
        self.tissueSource = ""
        self.receptionDate = ""
        self.comment = ""
        self.alias = ""

    def __str__(self):
        return f"{self.name} ({self.kind}) vol: {self.volume}"
