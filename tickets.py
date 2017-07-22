"""
     Ticket Purchase Program
     Brandon Jerz
     September 1, 2014
     CSC 212 Project 1

     This program is a lookup system for a theater that allows people to purchase tickets.
     It uses a simple command-line interface.  When you get the prompt, which is TIX!
     (or it can be set to whatever you want...), type help to get a list of commands.

     Internal program notes:

     The main data structure is a dictionary of seat names  "a1", "a2", ... "a50", "b1", "b2", ... "b50", ... "t1", "t2", ... "t50"
     The dictionary's keys are strings ("a1", etc)  The values are lists, 

	 ["buyer name", cost of seat, date sole]
		 ["Mr. Dracula", 95.00, "2014-09-03"]

     If the seat is not bought the key willnot be in the dictionary.
"""

import datetime
import pickle
import os
import sys
from tkinter import *
import tkinter.messagebox as box
import tkinter.font
import tkinter.simpledialog
#import gui

#  Below are the main variables that are used globally

db = {}                       # the database of seat purchases, which is a dictionary mapping strings to 3-lists (see above)
prompt = "TIX!"          # the prompt that the user sees (and can change)
changed = False      # this is set to true whenever a change is made in the db so that when the user tries to close, it
	                 # warns him/her.  If they save (using pickle) then it is reset to False

def alert(message):
	box.showinfo("Warning", message)

def is_legal_seat(seat):
	"A seat is a letter (a through z) followed by a number (1 through 50) "

	seat = seat.lower()
	if len(seat) < 2: return False
	row = seat[0]
	if row < 'a' or  row > 't': return False
	seatnum = int(seat[1:])
	if seatnum < 1 or seatnum > 50: return False
	return True

def get_seat_cost(seat):
	""" The seat cost is based on the row and the seat within the row.
	     The base price of each row is $100 for a, $95 for b, $90 for c, etc.
	     down to t which is $5.  Rows u through z all have a base price of $5, too.
	"""

	seat = seat.lower()
	row = seat[0]
	seatnum = int(seat[1:])
	cost = 100 - (ord(row)-ord('a'))*5
	return cost

def print_db():
	"Print the database of purchases seats, primarily for debugging purposes"

	global db
	for rownum in range(ord('a'), ord('z')+1):
		row = chr(rownum)
		xprint(row,end="  ")
		for i in range(1,51):
			seat = row + str(i)
			if seat in db:
				xprint (seat,db[seat])
		xprint_newline()

def is_open(seat):
	""" Returns True/False depending on whether the indicated seat like "a17" is purchased or not.
	     If not purchased, it is open and this returns True.  Otherwise if purchased, it returns False. 
	"""

	global db
	if not is_legal_seat(seat):
		alert(seat + " is not a legal seat")
		return
	return seat not in db

def inquirex(seat):
	"""  Looks to see if the seat is sold or not.  If sold, by whom and when? """

	global db
	if (seat == ""):
		alert("You must enter a seat such as a5 or t17")
		return
	if not is_legal_seat(seat):
		alert(seat + " is not a legal seat")
		return
	if is_open(seat):
		alert(seat + " has not yet been sold")
		return
	sell_details = db[seat]
	xprint(seat,"has been sold to", sell_details[0],"on",sell_details[2],"for $%.2f." % sell_details[1])

def buy(seat):
	""" The main workhorse method that attempts to buy the indicated seat."""

	global changed
	if seat == "":
		alert("You must enter a seat such as a5 or t17")
		return
	print("seat=",seat)
	if not is_legal_seat(seat):
		alert(seat + " is not a legal seat")
		return
	else:
		alert(seat+" is legal")
	if not is_open(seat):
		alert ("This seat is already taken")
	else:
		print("About to get a string")
		response = tkinter.simpledialog.askstring("Buy a seat", "This seat is open and costs $" + str(get_seat_cost(seat)) + "\nDo you want to buy it?  (y/n)")
		if response == 'y':
			name = tkinter.simpledialog.askstring("Buy a seat", "What is the purchaser's name? ")
			discount = 0
			response = tkinter.simpledialog.askstring("Buy a seat", "Do you have a discount coupon?\nEnter the percentage...")
			if response != "0":
				if response[-1] == "%":
					response = response[0:-1]
				discount = float(response)
			seat_price = get_seat_cost(seat) - discount
			db[seat] = [name, seat_price, str(datetime.date.today())]
			gui.ta.appendtext("Congratulations!  Pay by credit card now the sum of $%.2f" % seat_price)
			changed = True
		else:
			print("OK, seat not sold")

def refund(seat):
	""" This method allows you to unpurchase a seat.  It must have already been purchased and you must give
	     the name of the current owner of the seat in order to get a refund.  Afterwards the seat is open and may
	     be repurchased (by anyone.)
	"""

	global changed
	if (seat == ""):
		print("You must enter a seat such as a5 or t17")
		return
	if not is_legal_seat(seat):
		print(seat," is not a legal seat")
		return
	if is_open(seat):
		print ("This seat has not been sold")
		return
	the_seat = db[seat]
	response = input("What is your name? ")
	if response != the_seat[0]:
		print ("You did not buy the seat ",seat)
		return
	print ("The cost of seat ",seat,"was ", "%.2f." % the_seat[1])
	print ("It was bought on ",the_seat[2])
	response = input("Are you sure you want to refund it? (y/n) ")
	if response != "y":
		return
	del db[seat]
	print ("Refunded!")
	changed = True

def total():
	" Find all seats that are purchased and total up the amounts they were purchased for. "

	count = len(list(db.keys()))
	actual_total = 0      # the amount that the people really paid for the seats
	face_total = 0        # the amount they would have paid if there were no discounts.
	for key in db.keys():
		actual_total += db[key][1]
		face_total += get_seat_cost(key)
	print ("There are ",count," seats that have been sold already")
	print ("The face total is $%.2f" % actual_total)
	print ("The actual (discounted) total is $%.2f" % face_total)
	diff = face_total - actual_total
	print ("The amount given away in discounts amounts to $%.2f" % diff)

def find(command):
	""" Find a purchaser and which seats s/he has bought.
	  This requires that we look through all items in the seat dictionary and match the name.
	  This function was not part of the final requirements for the project. 
	"""
	name = command[5:]
	count = 0
	for key,value in db.items():
		if value[0] == name:
			count+= 1
			print ("Seat ", key)
	if count == 0:
		print(name," has not yet bought any seats")
	else:
		print(name," has bought ",count," seats.")
		
def load():
	""" Load the database from a disk file named ticketsystem.db.  That is saved using pickle. """

	global db, changed
	filename = "ticketsystem.dat"
	file = open(filename, "rb")
	db = pickle.load(file)
	print("There were ",len(db)," seats bought already")
	file.close()
	changed = False

def save():
	""" Save the database to a disk file named ticketsystem.db.  That is saved using pickle. """

	global changed
	filename = "ticketsystem.dat"
	file = open(filename, "wb")
	if file == None:
		print("There was an error creating your file")
		return
	pickle.dump(db, file)
	file.close()
	print("Saved words to ",filename)
	changed = False

def help():
	""" Print out all the commands possible in this system. 
	     Note that the find user command did not make it into the final specs. 
	"""

	xprint ("help   -- print help")
	xprint ("buy a5 -- try to buy seat a5")
	xprint ("inq a5 -- (inquire) what is the status of seat a5?")
	xprint ("refund a5 -- ask for a refund on a seat")
	xprint ("total -- how many seats are sold, how much money total")
	xprint ("view -- see the list of seats that are sold")
	xprint ("save -- save the database for later use")
	xprint ("load -- load the database that was saved")
	xprint ("    The name of the database file is ticketsystem.dat")
	xprint ("prompt >> -- change the prompt to whatever you want")
	xprint ("clear     -- clear the screen")
	xprint ("@any command   -- execute any Python system; just type @ first.")
	xprint ("*a system command -- execute an operating system command such as dir")
	xprint ("quit")


#def main():
	""" The main command engine, called from the main module code at the end.
	     It uses a command line interface and the dispatch code is very minimal.
	     A try/except block surrounds the main dispatch code so that a bug or
	    crash does not freeze the system, which would force the program to be
	    killed, thereby losing the databse in memory.  We could have used "shelve"
	    to do a kind of direct database to disk.
	"""
'''
	global db, prompt, changed
	print ("Welcome to the ticket reservation system!")
	print ("Enter a command or \"help\" to get help")
'''

def dispatch(command):
	try:
		#command = input(prompt + " ")
		print("Command=/"+command+"/")
		if command == "help":
			help()
		elif command.startswith("buy"):
			buy(command[4:])
		elif command.startswith("inq"):
			print("made it to inquire, seat="+command[4:])
			inquirex(command[4:])
		elif command.startswith("refund"):
			refund(command[7:])
		elif command.startswith("total"):
			total()
		elif command.startswith("view"):
			print_db()
		elif command.startswith("save"):
			save()
		elif command.startswith("load"):
			load()
		elif command.startswith("prompt"):
			prompt = command[7:]
		elif command.startswith("clear"):
			print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
		elif command.startswith("@"):
			debug_command = command[1:]
			print("GOT/" + debug_command + "/")
			exec(debug_command)
		elif command.startswith("*"):
			system_command = command[1:]
			os.system(system_command)
		elif command.startswith("#"):            # this is a comment that they can put into their scripts
			pass
		elif command == "quit":
			if changed:
				print("This loses all info.")
				response = input("Are you sure you want to quit now? (y/n)")
				if response == "y": os.exit()
			else:
				os.exit()
		else:
			print("Illegal command.  Try \"help\" if you are unsure.")
	except:
		print("Illegal command or bug in the system!")


if __name__ == "__main__":
	if "pickle" not in sys.modules:
		print("WARNING!!\nPickle is not activated.\n\n");
	main()

	
