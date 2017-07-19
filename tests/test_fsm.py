import unittest

import traders.fsm


# Create some fake states to test the Transition class.
class EndState(traders.fsm.State):

    def __init__(self):
        super().__init__('Ending')

    @property
    def events(self):
        return ('ended',)

    def run(self):
        return 'ended'


class StartState(traders.fsm.State):

    def __init__(self):
        super().__init__('Starting')

    @property
    def events(self):
        return ('started',)

    def run(self):
        return 'started'


class CountingState(traders.fsm.State):

    def __init__(self):
        super().__init__('Counting')
        self.value = 0

    @property
    def events(self):
        return ('counted',)

    def run(self):
        self.value += 1
        return 'counted'


class LimitingState(traders.fsm.State):

    def __init__(self, value, limit):
        super().__init__('Limiting')
        self.value = value
        self.limit = limit

    @property
    def events(self):
        return ('over', 'under')

    def run(self):
        if self.value > self.limit:
            return 'over'
        else:
            return 'under'


class Transition(unittest.TestCase):
    """Test the traders.fsm.Transition class"""

    def test_init(self):
        """Test the __init__ method"""

        # Create a simple transition.
        start_state = StartState()
        end_state = EndState()
        transition = traders.fsm.Transition(start_state, 'started', end_state)
        self.assertTrue(isinstance(transition, traders.fsm.Transition))

        # The first parameter must be a state.
        self.assertRaises(TypeError, traders.fsm.Transition,
                          None, 'started', end_state)

        # The third parameter must be a state.
        self.assertRaises(TypeError, traders.fsm.Transition,
                          start_state, 'started', None)

        # The fourth parameter must be callable or None.
        self.assertRaises(TypeError, traders.fsm.Transition,
                          start_state, 'started', end_state, 2)

    def test_match(self):
        """Test the match method"""

        # Create a simple transition.
        start_state = StartState()
        end_state = EndState()
        transition = traders.fsm.Transition(start_state, 'started', end_state)

        # Should only match if both the state and the event match.
        self.assertTrue(transition.match(start_state, 'started'))
        self.assertFalse(transition.match(end_state, 'started'))
        self.assertFalse(transition.match(start_state, 'ended'))
        self.assertFalse(transition.match(end_state, 'ended'))


class FiniteStateMachine(unittest.TestCase):
    """Test the traders.fsm.FiniteStateMachine class"""

    def test_events(self):
        """Test the events property"""

        # Create a simple state machine.
        start_state = StartState()
        machine = traders.fsm.FiniteStateMachine('Start machine', start_state)

        # Because the machine has no transitions, its events should
        # be exactly those of its inital state.
        self.assertEqual(machine.events, start_state.events)


class SimpleFSM(unittest.TestCase):
    """Test the traders.fsm.FiniteStateMachine by building simple ones"""

    def test_counting_fsm(self):

        counting = CountingState()
        limiting = LimitingState(counting.value, 10)

        def update(counting, event, limiting):
            limiting.value = counting.value

        counting_fsm = traders.fsm.FiniteStateMachine('Counting to 10',
                                                      counting)
        counting_fsm.add(traders.fsm.Transition(counting, 'counted',
                                                limiting, update))
        counting_fsm.add(traders.fsm.Transition(limiting, 'under',
                                                counting))

        # The only event of the state machine is 'over'.
        self.assertEqual(counting_fsm.events, ('over',))

        # After running the machine, the counter should be 1 over
        # the limit.
        counting_fsm.run()
        self.assertEqual(counting.value, 11)
