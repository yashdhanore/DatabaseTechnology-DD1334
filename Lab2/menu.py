#!/usr/bin/python
import sqlite3
from sys import argv
import matplotlib.pyplot as plt

# for Python 2.x users
try:
    input = raw_input
except NameError:
    pass


class Program:
    def __init__(self):  # PG-connection setup
        # establish database connection
        self.conn = sqlite3.connect('mondial.db')
        self.cur = self.conn.cursor()  # create a database query cursor

        # specify the command line menu here
        self.actions = [self.task_a,
                        self.task_b, self.task_c, self.task_d, self.task_e, self.task_f,
                        self.task_g, self.exit]
        # menu text for each of the actions above
        self.menu = ["Task a", "Task b", "Task c",
                     "Task d", "Task e", "Task f", "Task g", "Exit"]
        self.cur = self.conn.cursor()

    def print_menu(self):
        """Prints a menu of all functions this program offers.  Returns the numerical correspondant of the choice made."""
        for i, x in enumerate(self.menu):
            print("%i. %s" % (i+1, x))
        return self.get_int()

    def get_int(self):
        """Retrieves an integer from the user.
        If the user fails to submit an integer, it will reprompt until an integer is submitted."""
        while True:
            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(self.menu):
                    return choice
                print("Invalid choice.")
            except (NameError, ValueError, TypeError, SyntaxError):
                print("That was not a number, genious.... :(")

    def task_a(self):
        xy = "SELECT Year, Population FROM PopData"

        print("U1: (start) " + xy)
        try:
            self.cur.execute(xy)
            data = self.cur.fetchall()
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error message:", e.args[0])
            self.conn.rollback()
            exit()

        xs = []
        ys = []
        for r in data:
            # you access ith component of row r with r[i], indexing starts with 0
            # check for null values represented as "None" in python before conversion and drop
            # row whenever NULL occurs
            if (r[0] != None and r[0] != None):
                xs.append(float(r[0]))
                ys.append(float(r[1]))
            else:
                print("Dropped tuple ", r)

        plt.scatter(xs, ys)
        plt.savefig("figure_a.png")
        plt.show()

    def task_b(self):
        xy = "SELECT Year, SUM(Population) FROM PopData GROUP BY Year"

        print("U1: (start) " + xy)
        try:
            self.cur.execute(xy)
            data = self.cur.fetchall()
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error message:", e.args[0])
            self.conn.rollback()
            exit()

        xs = []
        ys = []
        for r in data:
            if (r[0] != None and r[0] != None):
                xs.append(float(r[0]))
                ys.append(float(r[1]))
            else:
                print("Dropped tuple ", r)

        plt.title("Total city population by year in database")
        plt.scatter(xs, ys)
        plt.savefig("figure_b.png")
        plt.show()

    def task_c(self):
        print("task c")

    def task_d(self):
        print("task d")

    def task_e(self):
        print("task e")

    def task_f(self):
        print("task f")

    def task_g(self):
        print("task g")

    def exit(self):
        self.cur.close()
        self.conn.close()
        exit()

    def print_answer(self, result):
        print("-----------------------------------")
        for r in result:
            print(r)
        print("-----------------------------------")

    def run(self):
        while True:
            try:
                self.actions[self.print_menu()-1]()
            except IndexError:
                print("Bad choice")
                continue


if __name__ == "__main__":
    db = Program()
    db.run()
