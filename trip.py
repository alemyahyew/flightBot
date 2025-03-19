import typing
class trip:
    tripName: str
    fromLocation: str
    toLocation: str
    leaveDate: str
    returnDate: str

    def __init__(self,depID, ariID, outD, retD):

        self.tripName = ( depID + " -> " + ariID)
        self.departure_id = depID
        self.arrival_id = ariID
        self.outbound_date = outD
        self.return_date = retD

