# ---------------------------------------------------------------------------------------------
#  Copyright (c) Akash Nag. All rights reserved.
#  Licensed under the MIT License. See LICENSE.md in the project root for license information.
# ---------------------------------------------------------------------------------------------

# ---------------- IMPORTS -------------------
import curses
import time
import sys
import market
from formatting import *

# ---------------- GLOBALS ------------------
REFRESH_DELAY = 5
ROWS = 0
COLS = 0
scrip = None
qty = None
rate = None
brokerage = 0

def get_portfolio_info(qty, buy_rate, brok, current_rate):
	investment = qty * buy_rate
	revenue = qty * current_rate
	brokAmt = 0 
	if brok > 0:
		brokAmt = qty * 2 * buy_rate * brok * 0.01
		#brokAmt = qty * 2 * max([ buy_rate * brok * 0.01, brok ])
	change = revenue - investment - brokAmt
	pChange = (change * 100) / investment
	
	return {
		"investment" : round(investment, 2),
		"revenue" : round(revenue, 2),
		"change" : round(change, 2),
		"pChange" : round(pChange, 2),
		"brokerage": round(brokAmt, 2)		
	}

def sfloat(data):
	if(data == None):
		return 0
	else:
		return float(str(data))

def display_data(stdscr, data, updated, qty, rate, brok):
	stdscr.clear()
	for i in range(ROWS):
		stdscr.addstr(i, 0, " " * (COLS-1), gc(COLOR_WHITE_ON_BLACK))
	
	sym = " " + data.get("symbol") + " "

	stdscr.addstr(1, len(sym)+2, data.get("companyName"), curses.A_BOLD | gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(1, 1, sym, gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(2, 1, "Volume: " + pretty(int(data.get("totalTradedVolume")), False), gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(3, 1, " " + pretty(data.get("lastPrice")) + " ", get_color_bg(data.get("open"), data.get("lastPrice")))
	stdscr.addstr(4, 1, symbol(sfloat(data.get("change"))) + " " + pretty(sfloat(data.get("change"))) + " (" + pretty(sfloat(data.get("pChange"))) + "%)", get_color_fg(sfloat(data.get("change"))))
	
	if(is_market_closed()):
		stdscr.addstr(5, 1, "Market Closed", gc(COLOR_YELLOW_ON_BLACK))
	else:
		stdscr.addstr(5, 1, " LIVE ", curses.A_BLINK | gc(COLOR_WHITE_ON_RED))
		stdscr.addstr(5, 8, "Updated: " + get_current_time(), gc(COLOR_WHITE_ON_BLACK))

	if(qty > 0 and rate > 0):
		pinfo = get_portfolio_info(qty, rate, brok, data.get("lastPrice"))	
		stdscr.addstr(2, 30, "Holding: " + str(qty) + " shares @ " + str(rate) + "/share", gc(COLOR_WHITE_ON_BLACK))
		stdscr.addstr(3, 30, " " + pretty(pinfo.get("revenue")) + " ", get_color_bg(pinfo.get("investment"), pinfo.get("revenue")))
		stdscr.addstr(4, 30, symbol(pinfo.get("change")) + " " + pretty(pinfo.get("change")) + " (" + pretty(pinfo.get("pChange")) + "%)", get_color_fg(pinfo.get("change")))
		stdscr.addstr(5, 30, "Investment: " + pretty(pinfo.get("investment")) + "    Brokerage: " + pretty(pinfo.get("brokerage")), gc(COLOR_WHITE_ON_BLACK))

	stdscr.addstr(7, 1,  "    CLOSE ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(7, 12, "     OPEN ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(7, 23, "   DAYLOW ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(7, 34, "  DAYHIGH ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(7, 45, " 52WEEKLO ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(7, 56, " 52WEEKHI ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(7, 67, "  DELVRY% ", gc(COLOR_BLACK_ON_YELLOW))

	stdscr.addstr(8, 1,  pad_left_str(data.get("previousClose"),9), gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(8, 12,  pad_left_str(data.get("open"),9), gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(8, 23,  pad_left_str(data.get("dayLow"),9), gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(8, 34,  pad_left_str(data.get("dayHigh"),9), gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(8, 45,  pad_left_str(data.get("low52"),9), gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(8, 56,  pad_left_str(data.get("high52"),9), gc(COLOR_WHITE_ON_BLACK))
	stdscr.addstr(8, 67,  pad_left_str(data.get("deliveryToTradedQuantity"),8) + "%", gc(COLOR_WHITE_ON_BLACK))
	
	stdscr.addstr(10, 1,  "     BID QTY ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(10, 15, "   BID PRICE ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(10, 29, "   OFFER QTY ", gc(COLOR_BLACK_ON_YELLOW))
	stdscr.addstr(10, 43, " OFFER PRICE ", gc(COLOR_BLACK_ON_YELLOW))
	if(qty > 0 and rate > 0): stdscr.addstr(10, 57, "   P/L @ BID PRICE ", gc(COLOR_BLACK_ON_YELLOW))
	
	for i in range(1,6):
		if(data.get("buyQuantity" + str(i)) == None):
			stdscr.addstr(10+i, 1,  pad_left_str("-", 12), gc(COLOR_WHITE_ON_BLACK))
		else:
			stdscr.addstr(10+i, 1,  pad_left_str(pretty(int(data.get("buyQuantity" + str(i))), False), 12), gc(COLOR_WHITE_ON_BLACK))
		stdscr.addstr(10+i, 15,  pad_left_str(pretty(data.get("buyPrice" + str(i)), False), 12), gc(COLOR_WHITE_ON_BLACK))
		if(data.get("sellQuantity" + str(i)) == None):
			stdscr.addstr(10+i, 29,  pad_left_str("-", 12), gc(COLOR_WHITE_ON_BLACK))
		else:
			stdscr.addstr(10+i, 29,  pad_left_str(pretty(int(data.get("sellQuantity" + str(i))), False), 12), gc(COLOR_WHITE_ON_BLACK))
		stdscr.addstr(10+i, 43,  pad_left_str(pretty(data.get("sellPrice" + str(i)), False), 12), gc(COLOR_WHITE_ON_BLACK))

		if(qty > 0 and rate > 0):
			#offerPrice = data.get("sellPrice" + str(i))	# to get P/L on offer price
			offerPrice = data.get("buyPrice" + str(i))		# to get P/L on bid price
			if(offerPrice == None):
				stdscr.addstr(10+i, 57,  pad_left_str("-", 18), gc(COLOR_WHITE_ON_BLACK))
			else:
				pinfo = get_portfolio_info(qty, rate, brok, sfloat(offerPrice))
				stdscr.addstr(10+i, 57,  pad_left_str(pretty(pinfo.get("change"), False), 18), get_color_fg(pinfo.get("change")))
	
	# print total bid and offer quantities
	if(data.get("totalBuyQuantity") == None):
		stdscr.addstr(16, 1,  pad_left_str("-", 12), gc(COLOR_WHITE_ON_BLUE))
	else:
		stdscr.addstr(16, 1,  pad_left_str(pretty(int(data.get("totalBuyQuantity")), False), 12) + " ", gc(COLOR_WHITE_ON_BLUE))
	if(data.get("totalSellQuantity") == None):
		stdscr.addstr(16, 29,  pad_left_str("-", 12), gc(COLOR_WHITE_ON_BLUE))
	else:
		stdscr.addstr(16, 29, pad_left_str(pretty(int(data.get("totalSellQuantity")), False), 12) + " ", gc(COLOR_WHITE_ON_BLUE))
	
	stdscr.refresh()

def initialize(stdscr):
	global ROWS, COLS

	curses.start_color()
	curses.use_default_colors()
	curses.noecho()
	curses.cbreak()	
	curses.curs_set(False)
	init_colors()
	ROWS, COLS = stdscr.getmaxyx()
	stdscr.clear()
	stdscr.refresh()

def parseArgs(args):
	if(len(sys.argv) == 1):
		return (None, None, None, None)
	else:
		scrip = sys.argv[1].upper()
		if(not market.isValid(scrip)): scrip = None

		qty = 0
		rate = 0
		brokerage = 0

		if(len(sys.argv) >= 3):
			temp = sys.argv[2]
			pos = temp.find("@")
			if(pos > -1):
				qty = int(temp[0:pos])
				rate = sfloat(temp[pos+1:])
		
		if(len(sys.argv) >= 4):
			temp = sys.argv[3]
			brokerage = sfloat(temp)

		return (scrip, qty, rate, brokerage)
	
def printUsage():
	print("ERROR: Invalid parameters or incorrect NSE code")
	print("\n\t\t  NSE Scrip Watch v1.0")
	print("\t\tCopyright 2020, Akash Nag. Licensed under the MIT License.")
	print("\nUsage:")
	print("\tpython3 scripwatch.py <scripcode> [<qty>@<rate> [<brok>]]")
	print("\n<scripcode>\tThe NSE scrip code for the stock")
	print("<qty>\t\tOptional. Number of shares of this stock in portfolio")
	print("<rate>\t\tOptional. Price of each share of this stock in portfolio")
	print("<brok>\t\tOptional. Brokerage as a percentage of share price,")
	print("      \t\tand also as minimum brokerage amount.")
	print("      \t\tTotal brokerage = 2 * qty * MAX(brok * rate * 0.01, brok)")
	print()

def printScreenError(stdscr):
	stdscr.clear()
	stdscr.addstr(0, 0, "ERROR:", curses.color_pair(COLOR_RED_ON_BLACK))
	stdscr.addstr(1, 0, "Window size insufficient!", curses.color_pair(COLOR_WHITE_ON_BLACK))
	stdscr.refresh()

def printError(stdscr, e):
	stdscr.clear()
	stdscr.addstr(0, 0, "ERROR:", curses.color_pair(COLOR_RED_ON_BLACK))
	stdscr.addstr(1, 0, pad_str_max(str(e), COLS-1), curses.color_pair(COLOR_WHITE_ON_BLACK))
	stdscr.refresh()


def app_main(stdscr):
	global scrip, qty, rate, brokerage

	initialize(stdscr)
	while(True):
		(stockData, updated) = market.fetch_data(scrip)
		if(stockData != None): 
			try:
				display_data(stdscr, stockData, updated, qty, rate, brokerage)
			except Exception as e:
				printError(stdscr, e)
				#printScreenError(stdscr)
		time.sleep(REFRESH_DELAY)

def main():
	global scrip, qty, rate, brokerage
	market.init_NSE()
	scrip, qty, rate, brokerage = parseArgs(sys.argv)
	if(scrip == None):
		printUsage()
		exit(1)
	else:
		curses.wrapper(app_main)
		
# ------------ MAIN CODE -----------------
main()