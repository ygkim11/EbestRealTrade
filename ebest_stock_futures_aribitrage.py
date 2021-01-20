import datetime
import numpy as np
import pandas as pd

from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from execution import SimulatedExecutionHandler

class StockFuturesArbitrage(Strategy):

    """
    Carries out Arbitrage trading on korean stock futures
    """
    def __init__(self, bars, events, short_window=100, long_window=400):
        """
        Initialses the Moving Avg. Cross Strategy.
        :param bars: The DataHandler object that provides bar information
        :param events: The Event Queue object
        :param short_window: The short moving average lookback
        :param long_window: The long moving average lookback
        """
        self.bars = bars  # bars를 어떻게 DataHandler로 정의해서 들고 오는건지 확인하기
        self.symbol_list = self.bars.symbol_list # pair_list의 unpacked list
        self.pair_list = [("068270", "1CPR2000")] #셀트리온 // 전날 universe를 정해줘야함
        self.events = events
        self.bought = self._initial_bought_dict()

        self.expiration_datetime = "매주 둘째주 목요일 3시?"

    def _initial_bought_dict(self):
        """
        Adds keys to the bought dict for all symbols and initially set them to "OUT"
        :return:
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = "OUT"
        return bought

    def calc_expiration_dateime(self):
        if self.bars.get_latest_bar_datetime(sf_code)


    def calc_signal_for_pairs(self):
        """
        generates signal based on pct_basis of stock futures
        :return:
        """
        for p in self.pair_list:
            s_code = p[0]
            sf_code = p[1]
            bar_date = self.bars.get_latest_bar_datetime(sf_code)

            if self.bought[s_code] == "OUT" and self.bought[sf_code] == "OUT":
                s_ask = self.bars.get_latest_bar_value(s_code, "sell_hoga1") # 주식
                sf_bid = self.bars.get_latest_bar_value(sf_code, "buy_hoga1") # 주식선물
                entry_spread = (sf_bid/s_ask)-1

                dt = datetime.datetime.utcnow()
                if entry_spread >= 0.00:
                    print("ENTRY LONG: %s and SHORT: %s at %2f at %s" % (s_code, sf_code, entry_spread, bar_date))
                    s_signal = SignalEvent(2, s_code, dt, "LONG", 1.0, s_ask)
                    sf_signal = SignalEvent(2, sf_code, dt, "SHORT", 1.0, sf_bid)
                    self.events.put(s_signal)
                    self.events.put(sf_signal)
                    self.bought[s_code] = "LONG"
                    self.bought[sf_code] = "SHORT"
                else:
                    pass

            elif self.bought[s_code] != "OUT" and self.bought[sf_code] != "OUT":
                s_bid = self.bars.get_latest_bar_value(p[0], "buy_hoga1")  # 주식
                sf_ask = self.bars.get_latest_bar_value(p[1], "sell_hoga1")  # 주식선물
                exit_spread = (sf_ask / s_bid) - 1
                dt = datetime.datetime.utcnow()

                if bar_date == self.expiration_datetime: #만기일 3시까지 Backwardation 미발생시 강제청산/ 실제 트레이딩시에는 그냥 놔두면 현금정산 될듯.
                    print("FORCE EXIT SHORT: %s and LONG: %s at %2f at %s" % (s_code, sf_code, exit_spread, bar_date))
                    s_signal = SignalEvent(2, s_code, dt, "EXIT", 1.0, s_bid)
                    sf_signal = SignalEvent(2, sf_code, dt, "EXIT", 1.0, sf_ask)
                    self.events.put(s_signal)
                    self.events.put(sf_signal)
                    self.bought[s_code] = "OUT"
                    self.bought[sf_code] = "OUT"

                else:
                    if exit_spread <= -0.01:
                        print("EXIT SHORT: %s and LONG: %s at %2f at %s" % (s_code, sf_code, exit_spread, bar_date))
                        s_signal = SignalEvent(2, s_code, dt, "EXIT", 1.0, s_bid)
                        sf_signal = SignalEvent(2, sf_code, dt, "EXIT", 1.0, sf_ask)
                        self.events.put(s_signal)
                        self.events.put(sf_signal)
                        self.bought[s_code] = "OUT"
                        self.bought[sf_code] = "OUT"

            else:
                print("Bought dict LONG/SHORT status error: Both pairs should have same position")




    def calc_signals(self, event):
        """
        generates signal based on pct_basis of stock futures
        """
        if event.type == "MARKET":
            self.calc_signal_for_pairs()
