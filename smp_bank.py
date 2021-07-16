import random
import sqlite3


def luhn_alg():
    number = '400000'
    dig_sum = 8
    for i in range(0, 9):
        dig = random.randint(0, 9)
        number += str(dig)
        if i % 2 == 0:
            dig_sum += (lambda x: x - 9 if x > 9 else x)(dig * 2)
        else:
            dig_sum += int(dig)
    number += (lambda x: '0' if x == 10 else str(x))(10 - (dig_sum % 10))
    return number


def luhn_alg_check(number):
    dig_sum = 0
    for i in range(0, len(number) - 1):
        if i % 2 == 0:
            dig_sum += (lambda x: x - 9 if x > 9 else x)(int(number[i]) * 2)
        else:
            dig_sum += int(number[i])
    print(dig_sum)
    return (10 - (dig_sum % 10)) == int(number[len(number) - 1])


def create_pin():
    pin = ''
    for i in range(0, 4):
        pin += str(random.randint(0, 9))
    return pin


class CreateCard:
    def __init__(self):

        self.current_users = {}
        self.id = 1
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
        self.from_table_to_dict()

    def look_through_table(self):
        for val in self.cur.execute("SELECT * FROM card"):
            print(val)

    def erase_all_table(self):
        self.cur.execute("DROP TABLE card")
        self.cur.execute("CREATE TABLE card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")

    def from_table_to_dict(self):
        if self.cur.fetchall() is not None:
            for val in self.cur.execute("SELECT * FROM card"):
                self.current_users[val[1]] = []
                self.current_users[val[1]].append(val[2])
                self.current_users[val[1]].append(val[3])
        self.id = len(self.current_users) + 1

    def create_acc(self):
        print("\nYour card has been created")
        print("Your card number:")
        card_num = luhn_alg()
        self.current_users[card_num] = []
        self.current_users[card_num].append(create_pin())
        self.current_users[card_num].append(0)
        self.cur.execute("INSERT INTO card(id, number, pin) VALUES(?,?,?)", (self.id, card_num, self.current_users[card_num][0]))
        self.conn.commit()
        print(card_num)
        print("Your card PIN:")
        print(self.current_users[card_num][0])
        print()

        self.menu()

    def login_into_acc(self, entered=False, num=''):
        if not entered:
            print("\nEnter your card number:")
            num = input()
            print("Enter your pin:")
            pin = input()
        if entered or num in self.current_users:
            if entered or pin == self.current_users[num][0]:
                print("\nYou have successfully logged in!\n")
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                n = input()
                if n == '1':
                    print(self.current_users[num][1])
                    self.login_into_acc(True, num)
                elif n == '2':
                    print("\nEnter income")
                    inc = int(input())
                    self.current_users[num][1] += inc
                    self.cur.execute("""UPDATE card
                                      SET balance = ? WHERE number = ?""",
                                     (self.current_users[num][1], num))
                    self.conn.commit()
                    print("Income was added!\n")
                    self.login_into_acc(True, num)
                elif n == '3':
                    print("Transfer")
                    print("Enter card number:")
                    crd = input()
                    self.do_transfer(num, crd)
                    self.login_into_acc(True, num)
                elif n == '4':
                    self.log_out(num)
                    self.menu()
                elif n == '5':
                    print("\nYou have successfully logged out!\n")
                    self.menu()
                elif n == '0':
                    print("Buy!")
            else:
                # wrong pin
                print("\nWrong card number or PIN!")
                self.menu()
        else:
            # wrong card number
            print("\nWrong card number or PIN!")
            self.menu()

    def do_transfer(self, card_number, trans_number):
        if not luhn_alg_check(trans_number):
            print("Probably you made a mistake in the card number. Please try again!\n")
        elif trans_number not in self.current_users:
            print("Such a card does not exist.\n")
        elif trans_number in self.current_users:
            print("Enter how much money you want to transfer:")
            money = int(input())
            if money > self.current_users[card_number][1]:
                print("Not enough money!\n")
            else:
                self.current_users[card_number][1] = self.current_users[card_number][1] - money
                self.cur.execute("UPDATE card SET balance = ? WHERE number = ?",
                                 (self.current_users[card_number][1], card_number))
                self.current_users[trans_number][1] = self.current_users[trans_number][1] + money
                self.cur.execute("UPDATE card SET balance = ? WHERE number = ?",
                                 (self.current_users[trans_number][1], trans_number))
                self.conn.commit()
                print("Success!\n")

    def log_out(self, card_num):
        self.current_users.pop(card_num)
        self.cur.execute("DELETE FROM card WHERE number = ?", [card_num])
        self.conn.commit()
        print("\nThe account has been closed!\n")

    def menu(self):
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        n = input()
        if n == '1':
            self.create_acc()
        elif n == '2':
            self.login_into_acc()
        elif n == '0':
            print("Bye!")
            self.cur.close()



