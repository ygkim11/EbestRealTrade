import datetime
import pprint
import queue
import time
import matplotlib.pyplot as plt
from multiprocessing import Process, Manager, Queue, JoinableQueue

class Backtest(object):
    """
    Encapsulates the setting and components for carrying out
    an event-driven backtest
    """
    def __init__(
         self, csv_dir, symbol_list, initial_cap, heartbeat, start_date,
         data_handler, execution_handler, portfolio, strategy
    ):
        """
        Initialises backtest
        :param csv_dir: Hard root of CSV
        :param symbol_list: The list of symbol strings
        :param initial_cap: The starting capital of portfolio
        :param heartbeat: Backtest "Heartbeat" in seconds(??)
        :param start_date: The start datetime of strategy
        :param data_handler: (Class) Handles market data feed
        :param execution_handler: (Class) Handles the Order/Fill for trade
        :param portfolio: (Class) Keeps track of portfolio current and prior positions + Risk Management can be added
        :param strategy: (Class) Generates signal based on market data
        """

        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_cap = initial_cap
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.events = Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1


        self._generate_trading_instances()

    def _generate_trading_instances(self):
         """
         Generates the trading instance object from their class types.
         :return:
         """
         print("Creating DataHandler, Strategy, Portfolio and ExecutionHandler")
         self.data_handler = self.data_handler_cls(self.events, self.csv_dir, self.symbol_list)
         self.strategy = self.strategy_cls(self.data_handler, self.events)
         self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date,
                                             self.initial_cap)
         self.execution_handler = self.execution_handler_cls(self.events)


    def _run_real_trade(self):
        """
        Executes backtest
        :return:
        """
        while True:
            #Update the market bars
            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars(i)
            else:
                break
            #Handles the events
            while True:
                try:
                    event = self.events.get(False) # queue에 뭐가있으면 다처리하고 while문 밖으로 나감!
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            print(event)
                            self.strategy.calc_signals(event)
                            self.portfolio.update_timeindex(event)
                            # p1 = Process(target=self.strategy.calc_signals, args=(event,))
                            # p2 = Process(target=self.portfolio.update_timeindex, args=(event,))
                            # p1.start()
                            # p2.start()
                        elif event.type == 'SIGNAL':
                            print(event)
                            self.signals += 1
                            self.portfolio.update_signal(event)
                        elif event.type == 'ORDER':
                            print(event)
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.type == 'FILL':
                            print(event)
                            self.fills += 1
                            self.portfolio.update_fill(event)

        time.sleep(self.heartbeat) #Live Trading시 실제로 시간을 맞춰주려는 code인가? Backtest에서는 0.0으로 설정해버림.

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        :return:
        """
        self.portfolio.create_equity_curve_dataframe()

        print("Creating Summary Stats....")
        stats = self.portfolio.output_summary_stats()

        print("Creating Equity Curve...")
        pprint.pprint(stats)

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)
        print(self.portfolio.equity_curve.tail(10))  # 추후 보완 ㄱㄱ

        #plot equity curve
        self.portfolio.equity_curve['equity_curve'].plot()
        plt.show()

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        :return:
        """
        self._run_backtest()
        self._output_performance()