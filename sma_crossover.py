
# Simple Moving Average Crossover Strategy

import MetaTrader5 as mt5  # install using 'pip install MetaTrader5'
import pandas as pd  # install using 'pip install pandas'
from datetime import datetime
import time
from candles import Candlesticks


class BotF(Candlesticks):

    def __init__(self, symbol: str, time_frame: int, sma_period: list[int], deviation: int):
        super().__init__()
        self.mt5 = mt5
        self.pd = pd
        self.symbol = symbol
        self.time_frame = time_frame
        self.sma_period = sma_period
        self.deviation = deviation
        self.isYen = False

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

    def double_candle_signal(self):
        """
        Checking the signals with double candle strategy
        """

        day = self.mt5.copy_rates_from_pos(
            self.symbol, self.mt5.TIMEFRAME_D1, 1, 100)

        day_df = self.pd.DataFrame(day)

        day_df = day_df[["time", "open", "high", "low", "close"]]

        self.check_trend(day_df, 2, 3, 5)

        checks_bullish_engulfing = []
        checks_bearish_engulfing = []
        checks_bullish_insidebar = []
        checks_bearish_insidebar = []
        double_splits = []

        for i in range(len(self.frame_trends) - 1):
            ch = self.frame_trends.iloc[(-i-1):(-i-3):-1]
            double_splits.append(ch)
            # when the 5th element of this row is 1 means on a bull trend
            # We only want to check for bearish engulfing bar and bearish inside bar on a bull trend
            if self.frame_trends[i, 5] == 1:
                res_bear = self.isBearEngulfing(ch)
                res_bear_in = self.isBearInsideBar(ch)

                checks_bullish_insidebar.append((res_bull_in, i))
                checks_bearish_insidebar.append((res_bear_in, i))

            # when the 5th element of this row is -1 means on a bear trend
            # We only want to check for bullish engulfing bar and bullish inside bar on a bear trend
            elif self.frame_trends[i, 5] == -1:
                res_bull = self.isBullEngulfing(ch)
                res_bull_in = self.isBullInsideBar(ch)

                checks_bullish_engulfing.append((res_bull, i))
                checks_bearish_engulfing.append((res_bear, i))

        is_bull_engulf = [x for x in checks_bullish_engulfing if x[0] == True]
        is_bear_engulf = [x for x in checks_bearish_engulfing if x[0] == True]
        is_bull_insidebar = [
            y for y in checks_bullish_insidebar if y[0] == True]
        is_bear_insidebar = [
            y for y in checks_bearish_insidebar if y[0] == True]

        positions_bull_engulf = [double_splits[y[1]] for y in is_bull_engulf]
        positions_bear_engulf = [double_splits[y[1]] for y in is_bear_engulf]
        positions_bull_insidebar = [double_splits[y[1]]
                                    for y in is_bull_insidebar]
        positions_bear_insidebar = [double_splits[y[1]]
                                    for y in is_bear_insidebar]

        low_positions = []
        high_positions = []

        low_positions_insidebar = []
        high_positions_insidebar = []

        if len(positions_bull_engulf) > 1:
            for i in range(len(positions_bull_engulf)):
                low_positions.append(
                    {'high': positions_bull_engulf[i].iloc[1].high, 'low': positions_bull_engulf[i].iloc[1].low, 'index': is_bull_engulf[i][1]})
        elif len(positions_bull_engulf) == 1:
            low_positions.append(
                {'high': positions_bull_engulf[0].iloc[1].high, 'low': positions_bull_engulf[0].iloc[1].low, 'index': is_bull_engulf[0][1]})

        if len(positions_bear_engulf) > 1:

            for i in range(len(positions_bear_engulf)):
                high_positions.append(
                    {'high': positions_bear_engulf[i].iloc[1].high, 'low': positions_bear_engulf[i].iloc[1].low, 'index': is_bear_engulf[i][1]})

        elif len(positions_bear_engulf) == 1:
            high_positions.append(
                {'high': positions_bear_engulf[0].iloc[1].high, 'low': positions_bear_engulf[0].iloc[1].low, 'index': is_bear_engulf[0][1]})

        if len(positions_bull_insidebar) > 1:
            for i in range(len(positions_bull_insidebar)):
                low_positions_insidebar.append(
                    {'high': positions_bull_insidebar[i].iloc[0].high, 'low': positions_bull_insidebar[i].iloc[1].low, 'index': is_bull_insidebar[i][1]})

        elif len(positions_bull_insidebar) == 1:
            low_positions_insidebar.append(
                {'high': positions_bull_insidebar[0].iloc[0].high, 'low': positions_bull_insidebar[0].iloc[0].low, 'index': is_bull_insidebar[0][1]})

        if len(positions_bear_insidebar) > 1:
            for i in range(len(positions_bear_insidebar)):
                high_positions_insidebar.append(
                    {'high': positions_bear_insidebar[i].iloc[0].high, 'low': positions_bear_insidebar[i].iloc[1].low, 'index': is_bear_insidebar[i][1]})

        elif len(positions_bear_insidebar) == 1:
            high_positions_insidebar.append(
                {'high': positions_bear_insidebar[0].iloc[0].high, 'low': positions_bear_insidebar[0].iloc[0].low, 'index': is_bear_insidebar[0][1]})

        self.set_bull_engulfing_prices(low_positions)
        self.set_bear_engulfing_prices(high_positions)
        self.set_bull_insidebar_prices(low_positions_insidebar)
        self.set_bear_insidebar_prices(high_positions_insidebar)

    def signal(self):
        bars10 = self.mt5.copy_rates_from_pos(
            self.symbol, self.time_frame, 1, self.sma_period[0])
        bars21 = self.mt5.copy_rates_from_pos(
            self.symbol, self.time_frame, 1, self.sma_period[1])

        day = self.mt5.copy_rates_from_pos(
            self.symbol, self.mt5.TIMEFRAME_D1, 1, 14)

        day_df = self.pd.DataFrame(day)

        yesterday = self.isDragonFlyDoji(day_df.iloc[-1])

        print("is yesterday's candle a gravestone doji?: ", yesterday)

        self.double_candle_signal()
        print('bullish engulfing high and low within 100 days: ',
              self.bull_engulfing_prices)
        print('bearish engulfing high and low within 100 days: ',
              self.bear_engulfing_prices)

        print('bullish insidebar high and low within 100 days: ',
              self.bull_insidebar_prices)

        print('bearish insidebar high and low within 100 days: ',
              self.bear_insidebar_prices)

        bars10_df = self.pd.DataFrame(bars10)
        bars21_df = self.pd.DataFrame(bars21)

        last_close = bars10_df.iloc[-1].close
        sma10 = bars10_df.close.mean()
        sma21 = bars21_df.close.mean()

        direction = 'flat'
        if sma10 > sma21:
            direction = 'buy'
        elif sma10 < sma21:
            direction = 'sell'

        return last_close, sma10, sma21, direction

    def signal50(self):
        """Signal for 50 ema"""
    def calc_distance_percentage(self, sma50, last_close):
        """Calculate percentage from 50 sma"""

        if last_close > sma50 :
            percentage = ((last_close - sma50) / sma50) * 100
        else:
            percentage = ((sma50 - last_close) / sma50) * 100

        return percentage


    # cxr means closing exchange rate
    def calc_supply_demand_zones(self):
        """
        Calculating supply & demand zones
        """

        rates = self.mt5.copy_rates_from_pos(
            self.symbol, self.time_frame, 0, 240)

        rates_df = self.pd.DataFrame(rates)

        highest_high = rates_df['high'].max()
        lowest_low = rates_df['low'].min()

        fair_price = (highest_high + lowest_low) / 2

        supply_zones = rates_df[rates_df['high'] >=
                                fair_price + (highest_high - fair_price) * 0.7]['high']
        demand_zones = rates_df[rates_df['low'] <=
                                fair_price - (fair_price - lowest_low) * 0.7]['low']

        return supply_zones, demand_zones

    def calc_candle_type(self, frame):
        '''
         Checking different candle types
        '''
        if self.isDoji(frame):
            return "Doji"
        elif self.isDragonFlyDoji(frame):
            return "DragonFly Doji"
        elif self.isGravestoneDoji(frame):
            return "Gravestone Doji"
        elif self.isHammer(frame):
            return "Hammer"
        elif self.isShootingstar(frame):
            return "Shooting Star"
        elif self.isSpinningTop(frame):
            return "Spinning Top"
        elif self.isSpinningBottom(frame):
            return "Spinning Bottom"
        elif self.isBullMaburuzu(frame):
            return "Bullish Maburuzu"
        elif self.isBearMaburuzu(frame):
            return "Bearish Maburuzu"
        else:
            return "Normal"

    def pip_converter(self, volume: float, cxr: float, pip_after_trade: int) -> str:
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

        step1 = volume * pip
        step2 = step1 / cxr
        step3 = round(pip_after_trade * step2, 2)
        if pip_after_trade > 0:
            res = f"Total Profit: {step3} {self.symbol}"

        else:
            res = f"Total Loss: {step3} {self.symbol}"

        return res


if __name__ == '__main__':

    # strategy parameters
    SYMBOL = "GBPJPYm"
    TIMEFRAME = mt5.TIMEFRAME_H1
    SMA_PERIODS = [10, 21]
    DEVIATION = 20

    gbp_HR1 = BotF(symbol=SYMBOL, time_frame=TIMEFRAME,
                   sma_period=SMA_PERIODS, deviation=DEVIATION)

    val = gbp_HR1.pip_converter()

    # mt5.initialize()

    while True:
        # calculating account exposure
        exposure = gbp_HR1.get_exposure()
        # calculating last candle close and simple moving average and checking for trading signal
        last_close, sma10, sma21, direction = gbp_HR1.signal()

        # trading logic
        if direction == 'buy':
            # if we have a BUY signal, close all short positions
            positions = gbp_HR1.mt5.positions_get(symbol=SYMBOL)
            if positions:

                for pos in positions:
                    if pos.type == 1:  # pos.type == 1 represent a sell order
                        gbp_HR1.close_order(pos.ticket)

                # if there are no open positions, open a new long position
                # if not mt5.positions_total():
            else:
                gbp_HR1.market_order(direction)

        elif direction == 'sell':
            # if we have a SELL signal, close all short positions
            positions = gbp_HR1.mt5.positions_get(symbol=SYMBOL)
            if positions:
                for pos in positions:
                    if pos.type == 0:  # pos.type == 0 represent a buy order
                        gbp_HR1.close_order(pos.ticket)

            # if there are no open positions, open a new short position
            # if not mt5.positions_total():
            else:
                gbp_HR1.market_order(direction)

        print('time: ', datetime.now())
        print('exposure: ', exposure)
        print('last_close: ', last_close)
        print('sma10: ', sma10)
        print('sma10: ', sma21)
        print('signal: ', direction)
        print('-------\n')

        # update every 1 second
        time.sleep(1)
