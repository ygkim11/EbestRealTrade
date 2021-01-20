from abc import ABCMeta, abstractmethod
import datetime
import queue

from ebest_event import FillEvent, OrderEvent

class ExecutionHandler(object):
    """
    The ExecutionHandler abstract class hadles the interaction between
    a set of Order objects generated by a Portfolio and ultimate set of
    Fill objects that actually occur in the market.

    The handler can be used to subclass simulated brokerages or live brokerages,
    with identical interface. This allow strategies to be backtested in very similar
    manner to the live trading engine
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        """
        Takes an Order event and executes it, producing a Fill event that
        gets placed onto the Events queue.
        :param event: Contains an Event object with order information
        :return:
        """
        raise NotImplementedError("Should implement execute_order()")


class SimulatedExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler simply converts all order objects into
    their equivalent fill objects automatically without latency, slippage or fill-ratio issues.

    This allow a straightforward "first-go" test of any strategy,
    before implementation with a more sophisticated execution handler.
    """
    def __init__(self, events):
        """
        Initialises the handler, setting the event queues up internally.
        :param events: The Queue of Event objects.
        """
        self.events = events

    def execute_order(self, event): #Naive Version 실질적으로는 Slippage 고려 필요. 호가잔량 정보 반영시켜보자.
        """
        Simply converts Order objects into Fill object naively,
        i.e. without latency, slippage or fill ratio problems.

        :param event: Contains an Event object with order information.
        :return:
        """
        if event.type == "ORDER":
            fill_event = FillEvent(datetime.datetime.utcnow(),
                                   event.symbol,
                                   'BT',
                                   event.quantity, event.direction, None, event.est_fill_cost)
            #Fill Cost as None when Backtest(Portfolio 에서 계산해줌)
            #Live Trading에서는 HTS 매입단가 넣어주면됨.
            #order type도 반영안됨. 그냥 Close로 계산.
            self.events.put(fill_event)


class KiwoomExecutionHandler(ExecutionHandler):
    """
    Key moving parts should be msg from API. We send orders and receive fill msg from API,
    thus using msgs we can implement various Execution Optimization Logic.
    """
    pass
