import pandas as pd 

class Candlesticks:
	def __init__(self, timeframe):
		self.timeframe = timeframe # candle timeframe to use
		self.remaining = self.timeframe # time until next bar in minutes
		self.bars = [] # (t,o,h,l,c,v)
		self.last_candle = None # the current candle

	def __getitem__(self, index):
		try:
			return self.bars[-index-1]
		except IndexError:
			print("Don't have {} candles in memory. Current length is {}".format(index, len(self.bars)))
			return None

	def __len__(self):
		return len(self.bars)

	def round_tick_time(self, mydatetime):
		# Set the reference time to 6 pm of the same day
		reference_time = mydatetime.replace(hour=18, minute=0, second=0, microsecond=0, nanosecond=0)
		if mydatetime.hour < 18: # before market open
			reference_time -= pd.Timedelta(days=1)

		# Calculate the time difference in seconds
		time_difference = (mydatetime - reference_time).total_seconds() 

		# Round down to the nearest multiple of self.timeframe minute 
		tsec = self.timeframe * 60
		rounded_time_difference = (time_difference // tsec) * tsec 

		# Add the rounded time difference to the reference time
		rounded_datetime = reference_time + pd.to_timedelta(rounded_time_difference, unit='seconds')
		return rounded_datetime


	def on_bar_update(self, candle, bartime=1):
		# work out whether to make a new bar or not
		if self.remaining <= 0:
			self.remaining += self.timeframe
			self.last_candle = None
		elif self.last_candle is not None and (candle[0] - self.last_candle[0]).seconds >= self.timeframe*60:
			self.remaining = self.timeframe
			self.last_candle = None

		# update current bar
		if self.last_candle is None:
			# need to append new candle
			self.last_candle = list(candle)
			if bartime == 0: # tick data
				self.last_candle[0] = self.round_tick_time(candle[0])
			self.bars.append(list(self.last_candle))
		else:
			self.last_candle[2] = max(self.last_candle[2], candle[2])
			self.last_candle[3] = min(self.last_candle[3], candle[3])
			self.last_candle[4] = candle[4]
			self.last_candle[5] += candle[5]
			self.bars[-1] = list(self.last_candle)

		self.remaining = self.remaining - bartime

	def on_tick_update(self, time, price, side, volume):
		self.on_bar_update([time,price,price,price,price,volume], bartime = 0)