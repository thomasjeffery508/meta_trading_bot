
# Simple Moving Average Crossover Strategy

import MetaTrader5 as mt5  # install using 'pip install MetaTrader5'
import pandas as pd  # install using 'pip install pandas'
from datetime import datetime
import time
from candles import Candlesticks


class BotF(Candlesticks):

    def __init__(self, symbol: str, time_frame: int, sma_period: list[int], deviation: int, isYen: bool):
        super().__init__()
        self.mt5 = mt5
        self.pd = pd
        self.symbol = symbol
        self.time_frame = time_frame
        self.sma_period = sma_period
        self.deviation = deviation
        self.isYen = isYen

        self.bull_engulfing_prices = []
        self.bear_engulfing_prices = []
        self.bull_insidebar_prices = []
        self.bear_insidebar_prices = []

        self.mt5.initialize()

    def __str__():
        return "BotF Maintained and Managed By Fortune Codebox"
    # function to send a market order

    def set_bull_engulfing_prices(self, prices):
        self.is_bull_engulfing_prices = prices

    def set_bear_engulfing_prices(self, prices):
        self.is_bear_engulfing_prices = prices

    def set_bull_insidebar_prices(self, prices):
        self.is_bull_insidebar_prices = prices

    def set_bear_insidebar_prices(self, prices):
        self.is_bear_insidebar_prices = prices

    def market_order(self, direction, **kwargs):
        tick = self.mt5.symbol_info_tick(self.symbol)
        volume = self.__risk_management()
        order_dict = {'buy': 0, 'sell': 1}
        price_dict = {'buy': tick.ask, 'sell': tick.bid}

        payload = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_dict[direction],
            "price": price_dict[direction],
            "deviation": DEVIATION,
            "magic": 100,
            "comment": "bot_i market order",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }

        order_result = self.mt5.order_send(payload)
        print(order_result)

        return order_result

    # function to close an order base don ticket id
    def close_order(self, ticket):
        positions = self.mt5.positions_get()

        for pos in positions:
            tick = self.mt5.symbol_info_tick(pos.symbol)
            # 0 represents buy, 1 represents sell - inverting order_type to close the position
            type_dict = {0: 1, 1: 0}
            price_dict = {0: tick.ask, 1: tick.bid}

            if pos.ticket == ticket:
                payload = {
                    "action": self.mt5.TRADE_ACTION_DEAL,
                    "position": pos.ticket,
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": type_dict[pos.type],
                    "price": price_dict[pos.type],
                    "deviation": self.deviation,
                    "magic": 100,
                    "comment": "bot_i close order",
                    "type_time": self.mt5.ORDER_TIME_GTC,
                    "type_filling": self.mt5.ORDER_FILLING_IOC,
                }

                order_result = self.mt5.order_send(payload)
                print(order_result)

                return order_result

        return 'Ticket does not exist'

    # private function called internally
    def __risk_management(self) -> float:
        # Risk management is very important
        # We are using 4% of the original investment for trades
        account_info = self.mt5.account_info()
        val: float = 0.00
        if account_info != None:
            balance = round(float(account_info._asdict()['balance']), 2)
            if balance > 0:
                val = 0.04 * balance / 100

                return round(float(val), 2)
            else:
                return val

        else:
            return val

    # function to get the exposure of a symbol

    def get_exposure(self):
        positions = self.mt5.positions_get(symbol=self.symbol)
        if positions:
            pos_df = self.pd.DataFrame(
                positions, columns=positions[0]._asdict().keys())
            exposure = pos_df['volume'].sum()

            return exposure

    # function to look for trading signals

    def signal(self):
        bars50 = self.mt5.copy_rates_from_pos(
            self.symbol, self.time_frame, 1, self.sma_period[0])


        bars50_df = self.pd.DataFrame(bars50)

        last_close = bars50_df.iloc[-1].close
        sma50 = bars50_df.close.mean()
        percent = self.__calc_distance_percentage(sma50, last_close)
        print(percent)
        direction = 'flat'
        if last_close > sma50 and percent <= 1.00:
            direction = 'buy'
        elif last_close < sma50 and percent <= 1.00:
            direction = 'sell'

        return last_close, sma50, direction

    def __calc_distance_percentage(self, sma50, last_close):
        """Calculate percentage from 50 sma"""

        if last_close > sma50 :
            percentage = ((last_close - sma50) / sma50) * 100
        else:
            percentage = ((sma50 - last_close) / sma50) * 100

        return round(percentage, 2)

    def tp_calc(self, entry: float, target: int, signal: int):
        """
        Calculate pip values: profit and loss
        # volume: volume for the trade
        # cxr: closing exchange rate
        # pip_after_trade: pip gained or loss

        5490.044

        """

        if self.isYen == False:
            pip = 0.0001
        else:
            pip = 0.01

        step1 = target * pip
        if signal == 0:
            tp = entry + step1
        else:
          tp = entry - step1

        return tp


if __name__ == '__main__':

    # strategy parameters
    SYMBOL = "BTCUSDm"
    TIMEFRAME = mt5.TIMEFRAME_15
    SMA_PERIODS = [50]
    DEVIATION = 20

    btc_M15 = BotF(symbol=SYMBOL, time_frame=TIMEFRAME,
                   sma_period=SMA_PERIODS, deviation=DEVIATION, isYen=False)

    val = btc_M15.pip_converter()

    # mt5.initialize()

    while True:
        # calculating account exposure
        exposure = btc_M15.get_exposure()
        # calculating last candle close and simple moving average and checking for trading signal
        last_close, sma50, direction = btc_M15.signal()

        # trading logic
        if direction == 'buy':
            # if we have a BUY signal, close all short positions
            positions = btc_M15.mt5.positions_get(symbol=SYMBOL)
            if positions:

                for pos in positions:
                    if pos.type == 1:  # pos.type == 1 represent a sell order
                        if pos.price_current >= btc_M15.tp_calc(pos.open_price, 100, pos.type):
                          btc_M15.close_order(pos.ticket)
                        else:
                          btc_M15.close_order(pos.ticket)

                # if there are no open positions, open a new long position
                # if not mt5.positions_total():
            else:
                btc_M15.market_order(direction)

        elif direction == 'sell':
            # if we have a SELL signal, close all short positions
            positions = btc_M15.mt5.positions_get(symbol=SYMBOL)
            if positions:
                for pos in positions:
                    if pos.type == 0:  # pos.type == 0 represent a buy order
                        if pos.price_current <= btc_M15.tp_calc(pos.open_price, 100, pos.type):
                          btc_M15.close_order(pos.ticket)
                        else:
                          btc_M15.close_order(pos.ticket)

            # if there are no open positions, open a new short position
            # if not mt5.positions_total():
            else:
                btc_M15.market_order(direction)

        print('time: ', datetime.now())
        print('exposure: ', exposure)
        print('last_close: ', last_close)
        print('sma10: ', sma50)
        print('signal: ', direction)
        print('-------\n')

        # update every 1 second
        time.sleep(1)
