# -*- coding: utf-8 -*-
from numpy import sqrt as npsqrt
from pandas import DataFrame
from .atr import atr
from .true_range import true_range
from pandas_ta.overlap import ema, hlc3, sma
from pandas_ta.utils import get_offset, high_low_range, non_zero_range, verify_series


def kc(high, low, close, length=None, scalar=None, mamode=None, offset=None, **kwargs):
    """Indicator: Keltner Channels (KC)"""
    # Validate arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    length = int(length) if length and length > 0 else 20
    min_periods = int(kwargs["min_periods"]) if "min_periods" in kwargs and kwargs["min_periods"] is not None else length
    scalar = float(scalar) if scalar and scalar > 0 else 2
    use_tr = kwargs.pop("tr", True)
    mamode = mamode.lower() if mamode else None
    offset = get_offset(offset)

    # Calculate Result
    if use_tr:
        range_ = true_range(high, low, close)
    else:
        range_ = high_low_range(high, low)

    _mode = ""
    if mamode == "sma":
        basis = sma(close, length)
        band = sma(range_, length=length)
        _mode += "s"
    elif mamode is None or mamode == "ema":
        basis = ema(close, length=length)
        band = ema(range_, length=length)

    lower = basis - scalar * band
    upper = basis + scalar * band

    # Offset
    if offset != 0:
        lower = lower.shift(offset)
        basis = basis.shift(offset)
        upper = upper.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        lower.fillna(kwargs["fillna"], inplace=True)
        basis.fillna(kwargs["fillna"], inplace=True)
        upper.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        lower.fillna(method=kwargs["fill_method"], inplace=True)
        basis.fillna(method=kwargs["fill_method"], inplace=True)
        upper.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    _props = f"{_mode if len(_mode) else ''}_{length}_{scalar}"
    lower.name = f"KCL{_props}"
    basis.name = f"KCB{_props}"
    upper.name = f"KCU{_props}"
    basis.category = upper.category = lower.category = "volatility"

    # Prepare DataFrame to return
    data = {lower.name: lower, basis.name: basis, upper.name: upper}
    kcdf = DataFrame(data)
    kcdf.name = f"KC{_props}"
    kcdf.category = basis.category

    return kcdf



kc.__doc__ = \
"""Keltner Channels (KC)

A popular volatility indicator similar to Bollinger Bands and
Donchian Channels.

Sources:
    https://www.tradingview.com/wiki/Keltner_Channels_(KC)

Calculation:
    Default Inputs:
        length=20, scalar=2, mamode=None
    ATR = Average True Range
    EMA = Exponential Moving Average
    SMA = Simple Moving Average

    BAND = ATR(high, low, close)
    if mamode == "ema":
        BASIS = EMA(close, length)
    elif mamode == "sma":
        BASIS = SMA(close, length)
    else: # Typical Price
        hl_range = high - low
        tp = typical_price = hlc3(high, low, close)
        BASIS = SMA(tp, length)
        BAND = SMA(hl_range, length)
    
    LOWER = BASIS - scalar * BAND
    UPPER = BASIS + scalar * BAND

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    length (int): The short period.  Default: 20
    scalar (float): A positive float to scale the bands.   Default: 2
    mamode (str): Two options: None or "ema".  Default: "ema"
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: lower, basis, upper columns.
"""