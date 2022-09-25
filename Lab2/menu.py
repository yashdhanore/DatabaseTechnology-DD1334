#!/usr/bin/python
from re import S
import sqlite3
from sys import argv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

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
        City = input("City: ")
        Country = input("Country: ")
        values = (City, Country)

        xy = "SELECT Year, SUM(Population) FROM PopData WHERE Name = (?) AND Country = (?) GROUP BY Year"

        print("U1: (start) " + xy)
        try:
            self.cur.execute(xy, values)
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

        regr = LinearRegression().fit(np.array(xs).reshape(
            [-1, 1]), np.array(ys).reshape([-1, 1]))

        score = regr.score(np.array(xs).reshape(
            [-1, 1]), np.array(ys).reshape([-1, 1]))
        a = regr.coef_[0][0]
        b = regr.intercept_[0]

        plt.title("City population and prediction for " +
                  City + ", " + Country)
        plt.scatter(xs, ys)
        plt.plot(xs, a*np.array(xs) + b, color='red')
        plt.savefig("figure_c.png")
        plt.show()

    def task_d(self):
        query = "DROP TABLE IF EXISTS linearprediction"
        self.cur.execute(query)
        self.conn.commit()

        create_table = "CREATE TABLE linearprediction" + \
            "(Name TEXT NOT NULL, Country TEXT NOT NULL, a REAL NOT NULL," + \
            "b REAL NOT NULL, Score REAL NOT NULL, PRIMARY KEY(Name,Country) ,CHECK (Score >= 0 AND Score <= 1))"

        self.cur.execute(create_table)
        self.conn.commit()

        cc = "SELECT Name, Country FROM PopData GROUP BY Name, Country;"
        cur2 = self.conn.cursor()  # returns an iterator, can directly iterate over it
        cur2.execute(cc)

        while True:
            row = cur2.fetchone()
            if row == None:
                break

            xy = "SELECT Year, SUM(Population) FROM PopData WHERE Name = (?) AND Country = (?) GROUP BY Year"

            try:
                self.cur.execute(xy, row)
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

            if len(xs) > 1 and len(ys) > 1:
                regr = LinearRegression().fit(np.array(xs).reshape(
                    [-1, 1]), np.array(ys).reshape([-1, 1]))

                score = regr.score(np.array(xs).reshape(
                    [-1, 1]), np.array(ys).reshape([-1, 1]))
                a = regr.coef_[0][0]
                b = regr.intercept_[0]

                values = (row[0], row[1], a, b, score)
                query = "INSERT INTO linearprediction VALUES(?,?,?,?,?)"
                self.cur.execute(query, values)

            self.conn.commit()

    def task_e(self):
        query = "DROP TABLE IF EXISTS prediction"
        self.cur.execute(query)
        self.conn.commit()

        create_table = "CREATE TABLE prediction" + \
            "(Name TEXT NOT NULL, Country TEXT NOT NULL, Population INTEGER NOT NULL," + \
            "Year INTEGER NOT NULL, PRIMARY KEY(Name,Country,Year))"

        self.cur.execute(create_table)
        self.conn.commit()

        for i in range(1950, 2051):
            insert = "INSERT INTO prediction (Name, Country, Population, Year) SELECT Name, Country, a*" + str(
                i) + "+b," + str(i) + " FROM linearprediction;"
            self.cur.execute(insert)
            self.conn.commit()

    def task_f(self):
        query = "SELECT Year, SUM(Population), Min(Population), Max(Population), AVG(Population) FROM prediction GROUP BY Year"
        self.cur.execute(query)
        data = self.cur.fetchall()
        self.conn.commit()

        year = []
        predictions = []
        min_predictions = []
        max_predictions = []
        mean_predictions = []

        for r in data:
            if (r[0] != None and r[0] != None):
                year.append(float(r[0]))
                predictions.append(float(r[1]))
                min_predictions.append(float(r[2]))
                max_predictions.append(float(r[3]))
                mean_predictions.append(float(r[4]))
            else:
                print("Dropped tuple ", r)

        fig, axs = plt.subplots(2, 2)

        axs[0, 0].set(xlabel='Year', ylabel='Population')
        axs[0, 0].scatter(year, predictions, color='blue', s=2)
        axs[0, 0].set_title("Total population prediction")

        axs[0, 1].set(xlabel='Year', ylabel='Population')
        axs[0, 1].scatter(year, min_predictions, color='red', s=2)
        axs[0, 1].set_title("Min population prediction")

        axs[1, 0].set(xlabel='Year', ylabel='Population')
        axs[1, 0].scatter(year, max_predictions, color='green', s=2)
        axs[1, 0].set_title("Max population prediction")

        axs[1, 1].set(xlabel='Year', ylabel='Population')
        axs[1, 1].scatter(year, mean_predictions, color='purple', s=2)
        axs[1, 1].set_title("Mean population prediction")

        plt.show()

    def task_g(self):
        # Hypothesis: Countries which lie near the equator have a high population growth.
        query = "Select prediction.Year, prediction.Population from prediction join City on City.Country = prediction.Country where City.Latitude >= -10 AND City.Latitude <= 10 GROUP BY prediction.Year"

        try:
            self.cur.execute(query)
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

        plt.scatter(xs, ys, s=2)

        plt.show()

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
