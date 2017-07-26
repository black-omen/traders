from abc import ABC, abstractproperty, abstractmethod
from itertools import chain


class State(ABC):

    def __init__(self, name):
        """Abstract base class for states of a finite state machine

        When a FSM is in a specific state, that state is run. The outcome of
        running the state is an event. The list of events that can be
        returned by a state is given by its `event` property.

        """
        self.name = name

    def __str__(self):
        """Converts state to readable string representation"""
        return self.name

    @abstractproperty
    def events(self):
        """Returns a tuple of events that can be returned by the run method"""
        pass

    @abstractmethod
    def run(self):
        """Runs the state code"""
        pass


class Transition(object):

    def __init__(self, current_state, event, next_state, update=None):
        """A transition between two states following and event

        The transition class represents the specific change from one state
        to another following an event. It also provides a mechanism to
        pass information from the initial state to the new state via the
        update function.

        The update function must receive the current state, the event, and
        the new state as parameters. It updates the new state and returns
        None.

        """

        if not isinstance(current_state, State):
            raise TypeError(
                '\'current_state\' must be an instance of {}, not {}.'
                .format(State, current_state.__class__))

        if not isinstance(next_state, State):
            raise TypeError(
                '\'next_state\' must be an instance of {}, not {}.'
                .format(State, next_state.__class__))

        if update is not None and not callable(update):
            raise TypeError('\'update\' must be callable or None, not {}.'
                            .format(update.__class__))

        self._current_state = current_state
        self._event = event
        self._next_state = next_state
        self._update = update

    def __str__(self):
        return '({}, {}) -> {}'.format(str(self.current_state.name),
                                       str(self.event),
                                       str(self.next_state.name))

    @property
    def event(self):
        return self._event

    @property
    def current_state(self):
        return self._current_state

    @property
    def next_state(self):
        """Returns the next state without updating it"""
        return self._next_state

    def apply(self):
        """Applies the update function and returns the new state"""
        if self._update is not None:
            self._update(self.current_state, self.event, self._next_state)
        return self._next_state

    def match(self, current_state, event):
        """Verifies if the transition matches the state and event"""
        if self.current_state == current_state and self.event == event:
            return True

        return False


class FiniteStateMachine(State):

    def __init__(self, name, start_state):
        """A finite state machine

        The finite state machine encapsulates a list of states and the
        transition between them. Because a FSM is itself a state, it can be
        run and yield events. The events of a FSM are all the events of its
        state which are not associated with a transition.

        """

        super().__init__(name)
        self.start_state = start_state
        self._transitions = []

    @property
    def events(self):
        """Returns the list of events that can be thrown by the  FSM"""

        # The events that the FSM can throw are all the events that
        # do not have a transition.
        events = []
        states = set(chain((self.start_state,),
                           (t.current_state for t in self._transitions),
                           (t.next_state for t in self._transitions)))
        for state in states:
            for event in state.events:
                if self.transition(state, event) is None:
                    events.append(event)

        return tuple(events)

    def __str__(self):
        """String representation of a FSM"""

        out = 'FSM: {}\n'.format(self.name)
        out += '\n  Start state: {}\n'.format(str(self.start_state))
        out += '\n  Transitions:\n'
        for transition in self._transitions:
            out += '    {}\n'.format(str(transition))

        out += '\n  Events:\n'
        for event in self.events:
            out += '    {}\n'.format(event)

        print(out)

    def add(self, transition):
        """Adds a transition to a FiniteStateMachine"""

        if not isinstance(transition, Transition):
            raise TypeError(
                '\'transition\' must be an instance of {}, not {}.'
                .format(Transition, transition.__class__))
        self._transitions.append(transition)

    def run(self):
        """Runs the finite state machine"""

        current_state = self.start_state

        while True:
            event = current_state.run()
            transition = self.transition(current_state, event)
            if transition is None:
                break
            current_state = transition.apply()

        return event

    def transition(self, state, event):
        """Returns the transition for a state and event or None"""
        matches = (t for t in self._transitions if t.match(state, event))
        return next(matches, None)
