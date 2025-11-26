from abc import ABC, abstractmethod
from enum import Enum

class ApplicationStatus(Enum):
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    PENDING = "pending"


class ApplicationState(ABC):
    """
    Abstract base class for application states in the state pattern.
    Defines the interface for state transitions: shortlist, reject, and accept.
    Each concrete state should implement these transitions according to its rules.
    """
    current_status: ApplicationStatus

    @abstractmethod
    def shortlist(self):
        """
        Transition the application to the shortlisted state.
        Returns a new ApplicationState instance representing the new state.
        """
        raise NotImplementedError

    @abstractmethod
    def reject(self):
        """
        Transition the application to the rejected state.
        Returns a new ApplicationState instance representing the new state.
        """
        raise NotImplementedError

    @abstractmethod
    def accept(self):
        """
        Transition the application to the accepted state.
        Returns a new ApplicationState instance representing the new state.
        """
        raise NotImplementedError



class ShortlistedState(ApplicationState):
    """
    Represents the 'shortlisted' state of an application.
    Allows transitions to 'rejected' or 'accepted', but not to 'shortlisted' again.
    """

    def __init__(self):
        self.current_status = ApplicationStatus.SHORTLISTED

    def shortlist(self) -> ApplicationState:
        """
        Attempting to shortlist an already shortlisted application returns the same state.
        """
        return self  # Already shortlisted

    def reject(self) -> ApplicationState:
        """
        Transition from shortlisted to rejected state.
        """
        return RejectedState()

    def accept(self) -> ApplicationState:
        """
        Transition from shortlisted to accepted state.
        """
        return AcceptedState()



class RejectedState(ApplicationState):
    """
    Represents the 'rejected' state of an application.
    Allows transition back to 'shortlisted', but cannot be accepted.
    """

    def __init__(self):
        self.current_status = ApplicationStatus.REJECTED

    def shortlist(self) -> ApplicationState:
        """
        Transition from rejected to shortlisted state.
        """
        return ShortlistedState()

    def reject(self) -> ApplicationState:
        """
        Attempting to reject an already rejected application returns the same state.
        """
        return self  # Already rejected

    def accept(self) -> ApplicationState:
        """
        Cannot accept a rejected application; returns the same state.
        """
        return self  # Cannot accept a rejected application



class AcceptedState(ApplicationState):
    """
    Represents the 'accepted' state of an application.
    Allows transition to 'rejected', but cannot be shortlisted or accepted again.
    """

    def __init__(self):
        self.current_status = ApplicationStatus.ACCEPTED

    def shortlist(self) -> ApplicationState:
        """
        Cannot shortlist an accepted application; returns the same state.
        """
        return self  # Cannot shortlist an accepted application

    def reject(self) -> ApplicationState:
        """
        Transition from accepted to rejected state.
        """
        return RejectedState()

    def accept(self) -> ApplicationState:
        """
        Attempting to accept an already accepted application returns the same state.
        """
        return self  # Already accepted



class PendingState(ApplicationState):
    """
    Represents the 'pending' state of an application.
    Allows transitions to 'shortlisted', 'rejected', or 'accepted'.
    """

    def __init__(self):
        self.current_status = ApplicationStatus.PENDING

    def shortlist(self) -> ApplicationState:
        """
        Transition from pending to shortlisted state.
        """
        return ShortlistedState()

    def reject(self) -> ApplicationState:
        """
        Transition from pending to rejected state.
        """
        return RejectedState()

    def accept(self) -> ApplicationState:
        """
        Transition from pending to accepted state.
        """
        return AcceptedState()

