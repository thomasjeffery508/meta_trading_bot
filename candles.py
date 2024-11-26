"""Candle Sticks Class & Properties"""
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, find_peaks


class Candlesticks:

    def __init__(self) -> None:
        self.frame_trends: pd.DataFrame

    def isDoji(self, frame) -> bool:
        body = abs(frame.open - frame.close)
        candle = abs(frame.high - frame.low)
        average_price = frame.high + frame.low / 2

        percentage = round(float((body/candle) * 1), 2)

        h = average_price + (frame.high - average_price) * 0.025
        l = average_price - (average_price - frame.low) * 0.025

        if frame.close > frame.open:
            if percentage <= 0.05 and h >= frame.close and l <= frame.open:
                return True

            else:
                return False

        elif frame.open > frame.close:
            if percentage <= 0.05 and h >= frame.open and l <= frame.close:
                return True

            else:
                return False

        elif frame.open == frame.close:
            if percentage <= 0.05:
                return True

            else:
                return False
        else:
            return False

    def isDragonFlyDoji(self, frame):
        body = abs(frame.open - frame.close)
        candle = abs(frame.high - frame.low)

        percentage = round(float((body/candle) * 1), 2)

        mid = (frame.high + frame.low) / 2
        h = mid + ((frame.high - mid) * 0.05)
        if percentage <= 0.05 and frame.open >= h and frame.close >= h:
            return True
        else:
            return False

    def isGravestoneDoji(self, frame):
        body = abs(frame.open - frame.open)
        candle = abs(frame.high - frame.low)

        percentage = round(float((body/candle) * 1), 2)

        mid = (frame.high + frame.low) / 2
        h = mid - ((frame.high - mid) * 0.05)
        if percentage <= 0.05 and frame.open <= h and frame.close <= h:
            return True
        else:
            return False

    def isHammer(self, frame):
        body = abs(frame.open - frame.close)
        candle = abs(frame.high - frame.low)

        percentage = round(float((body/candle) * 1), 2)

        mid = (frame.high + frame.low) / 2

        h = mid + ((frame.high - mid) * 0.05)
        if percentage > 0.05 and percentage <= 0.25 and frame.open >= h and frame.close >= h:
            return True
        else:
            return False

    def isShootingstar(self, frame):
        body = abs(frame.open - frame.close)
        candle = abs(frame.high - frame.low)

        percentage = round(float((body/candle) * 1), 2)

        mid = (frame.high + frame.low) / 2

        h = mid - ((frame.high - mid) * 0.05)
        if percentage > 0.05 and percentage <= 0.25 and frame.open <= h and frame.close <= h:
            return True
        else:
            return False

    def isSpinningTop(self, frame):

        body = abs(frame.open - frame.close)
        candle = abs(frame.high - frame.low)
        average_price = (frame.high + frame.low) / 2

        percentage = round(float((body/candle) * 1), 2)

        h = average_price + ((frame.high - average_price) * 0.125)
        l = average_price - ((average_price - frame.low) * 0.125)

        if frame.close > frame.open:
            if percentage > 0.05 and percentage <= 0.25 and h >= frame.close and l <= frame.open:
                return True

            else:
                return False
        else:
            return False

    def isSpinningBottom(self, frame):
        body = abs(frame.open - frame.close)
        candle = abs(frame.high - frame.low)
        average_price = (frame.high + frame.low) / 2

        percentage = round(float((body/candle) * 1), 2)

        h = average_price + ((frame.high - average_price) * 0.125)
        l = average_price - ((average_price - frame.low) * 0.125)

        if frame.open > frame.close:
            if percentage > 0.05 and percentage <= 0.25 and h >= frame.open and l <= frame.close:
                return True

            else:
                return False
        else:
            return False

    def isBullMaburuzu(self, frame):
        if frame.close > frame.open:
            body = abs(frame.close - frame.open)
            candle = abs(frame.high - frame.low)

            percentage = round(float((body/candle) * 1), 2)

            if percentage >= 0.65:
                return True
            else:
                return False

        else:
            return False

    def isBearMaburuzu(self, frame):
        if frame.open > frame.close:
            body = abs(frame.open - frame.close)
            candle = abs(frame.high - frame.low)

            percentage = round(float((body/candle) * 1), 2)
            if percentage >= 0.65:
                return True
            else:
                return False

        else:
            return False

    def isBullEngulfing(self, frame):
        # Engulfing candle comprises of two candle sticks and the first candle is entirely engulfed by the
        # second candle
        # The second real body is the opposite of the first real body
        first = frame.iloc[-2]
        second = frame.iloc[-1]

        if second.close > first.close and second.close > first.open and first.close < first.open and second.close > second.open and self.isBullMaburuzu(second):
            return True
        else:
            return False

    def isBearEngulfing(self, frame):
        first = frame.iloc[-2]
        second = frame.iloc[-1]

        if second.close < first.close and second.close < first.open and first.close > first.open and second.close < second.open and self.isBearMaburuzu(second):
            return True
        else:
            return False

    def isBullInsideBar(self, frame):
        first = frame.iloc[-2]
        second = frame.iloc[-1]

        if first.open > second.open and first.open > second.close and second.close > first.close and self.isBearMaburuzu(first):
            return True

        else:
            return False

    def isBearInsideBar(self, frame):

        first = frame.iloc[-2]
        second = frame.iloc[-1]

        if first.open < second.open and first.open < second.close and second.close < first.close and self.isBullMaburuzu(first):
            return True

        else:
            return False

    def isMorningStar(self, frame):
        if frame.shape[0] < 3:
            pass
        else:
            first = frame.iloc[-3]
            second = frame.iloc[-2]
            third = frame.iloc[-1]
            checksecond = self.isDoji(second) or self.isDragonFlyDoji(
                second) or self.isHammer(second)
            if self.isBullMaburuzu(first) and checksecond and self.isBearMaburuzu(third):
                return True

            else:
                return False

    def isEveningStar(self, frame):
        if frame.shape[0] < 3:
            pass
        else:
            first = frame.iloc[-3]
            second = frame.iloc[-2]
            third = frame.iloc[-1]
            checksecond = self.isDoji(second) or self.isGravestoneDoji(
                second) or self.isShootingstar(second)
            if self.isBearMaburuzu(first) and checksecond and self.isBullMaburuzu(third):
                return True

            else:
                return False

    def isTweezerBottom(self):
        pass

    def isTweezersTop(self):
        pass

    def calc_fibonacci_levels(self, frame):
        """
         Fibonacci levels are 0.236, 0.382, 0.500, 0.618
        """
        max_price = frame['close'].max()
        min_price = frame['close'].min()

        difference = max_price - min_price

        first_level = max_price - difference * 0.236
        second_level = max_price - difference * 0.382
        third_level = max_price - difference * 0.5
        fourth_level = max_price - difference * 0.618

        return max_price, first_level, second_level, third_level, fourth_level, min_price

    def __adder(self, frame: pd.DataFrame, times):
        self.frame_trends = frame
        for i in range(1, times+1):
            # new_col = np.zeros((len(self.frame_trends), 1), dtype=float)
            # frame = np.append(self.frame_trends, new_col, axis=1)
            self.frame_trends['trends'] = 0

        # print('inside Adder: ', self.frame_trends.head(3))

    def __deleter(self, frame, index, times):
        for i in range(1, times + 1):
            frame = np.delete(frame, index, axis=1)

        return frame

    def __jump(self, frame, jump):
        frame = frame[jump:]
        return frame

    def check_trend(self, framed: pd.DataFrame, high, low, index):

        self.__adder(framed, 1)

        for i in range(len(self.frame_trends) - 1, -1, -1):
            if self.frame_trends.iloc[i].high > self.frame_trends.iloc[i-2].low and self.frame_trends.iloc[i].high > self.frame_trends.iloc[i-3].low and self.frame_trends.iloc[i].high > self.frame_trends.iloc[i-5].low and self.frame_trends.iloc[i].high > self.frame_trends.iloc[i-8].low and self.frame_trends.iloc[i].high > self.frame_trends.iloc[i-13].low:
                self.frame_trends[i, index] = 1

            elif self.frame_trends.iloc[i].high < self.frame_trends.iloc[i-2, low] and self.frame_trends.iloc[i, high] < self.frame_trends.iloc[i-3, low] and self.frame_trends.iloc[i, high] < self.frame_trends.iloc[i-5, low] and self.frame_trends.iloc[i, high] < self.frame_trends.iloc[i-8, low] and self.frame_trends.iloc[i, high] < self.frame_trends.iloc[i-13, low]:
                self.frame_trends[i, index] = -1
