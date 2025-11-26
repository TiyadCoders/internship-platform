from abc import ABC, abstractmethod
from enum import Enum

class ApplicationStatus(Enum):
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    PENDING = "pending"


class ApplicationState(ABC):
    current_status: ApplicationStatus

    @abstractmethod
    def shortlist(self):
        raise NotImplementedError

    @abstractmethod
    def reject(self):
        raise NotImplementedError

    @abstractmethod
    def accept(self):
        raise NotImplementedError



class ShortlistedState(ApplicationState):

    def __init__(self):
        self.current_status = ApplicationStatus.SHORTLISTED

    def shortlist(self) -> ApplicationState:
        return self  # Already shortlisted

    def reject(self) -> ApplicationState:
        return RejectedState()

    def accept(self) -> ApplicationState:
        return AcceptedState()



class RejectedState(ApplicationState):

    def __init__(self):
        self.current_status = ApplicationStatus.REJECTED

    def shortlist(self) -> ApplicationState:
        return ShortlistedState()

    def reject(self) -> ApplicationState:
        return self  # Already rejected

    def accept(self) -> ApplicationState:
        return self  # Cannot accept a rejected application



class AcceptedState(ApplicationState):

    def __init__(self):
        self.current_status = ApplicationStatus.ACCEPTED

    def shortlist(self) -> ApplicationState:
        return self  # Cannot shortlist an accepted application

    def reject(self) -> ApplicationState:
        return RejectedState()

    def accept(self) -> ApplicationState:
        return self  # Already accepted



class PendingState(ApplicationState):

    def __init__(self):
        self.current_status = ApplicationStatus.PENDING

    def shortlist(self) -> ApplicationState:
        return ShortlistedState()

    def reject(self) -> ApplicationState:
        return RejectedState()

    def accept(self) -> ApplicationState:
        return AcceptedState()

