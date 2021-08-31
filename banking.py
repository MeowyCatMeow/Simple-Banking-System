"""
https://hyperskill.org/projects/109/stages/594/implement
https://imgur.com/Zt1RwZ6
"""
import sqlite3
from random import sample


class BankingSystem:
    def __init__(self):
        self.database()  # init database
        self.card_data = None  # card_data is a list for storing logged in account's info
        # self.card_data initiated in login()
        #  self.cards = {}  This is for previous stage

    def menu(self):
        while True:
            try:
                print("1. Create an account\n2. Log into account\n0. Exit")
                self.to_1st_menu(input())()
            except KeyError:
                print('Unknown option.')

    def to_1st_menu(self, choice):
        switcher = {
            '1': self.create_acc,
            '2': self.login,
            '0': self.end
        }
        return switcher[choice]

    @staticmethod
    def database(card=None, pin=None, balance=None):
        with sqlite3.connect('card.s3db') as data:
            cursor = data.cursor()
            if not card:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS card(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                number TEXT,
                pin TEXT,
                balance INTEGER
                );
                ''')
            else:
                cursor.execute('''
                INSERT into card(number, pin, balance)
                VALUES(?,?,?)  
                ''', (card, pin, balance))

    @staticmethod
    def luhn_algorithm(card_number: str) -> bool:
        number = list(map(int, card_number))[::-1]
        for index in range(1, len(number), 2):
            if number[index] < 5:
                number[index] = number[index] * 2
            else:
                number[index] = ((number[index] * 2) // 10) + ((number[index] * 2) % 10)
        return (sum(number) % 10) == 0

    @staticmethod
    def generate_nums():
        while True:
            random_card = '400000' + ''.join([str(n) for n in sample(range(9), 9)]) + '7'
            random_pin = ''.join([str(n) for n in sample(range(9), 4)])
            if BankingSystem.luhn_algorithm(random_card):
                yield random_card, random_pin
            else:
                continue

    def create_acc(self):
        card, pin = next(self.generate_nums())
        # self.cards[card] = {'pin': pin, 'balance': 0}
        self.database(card, pin, 0)
        print('\nYour card has been created')
        print(f'Your card number:\n{card}')
        print(f'Your card PIN:\n{pin}\n')

    @staticmethod
    def check_credentials(card):
        with sqlite3.connect('card.s3db') as data:
            cursor = data.cursor()
            cursor.execute('''
            SELECT number, pin, balance FROM card WHERE number = (?);
            ''', (card,))  # card is card's number
            return list(cursor.fetchone())

    def login(self):
        card = input('Enter your card number:\n')
        pin = input('Enter your PIN:\n')
        try:
            # if self.cards[card]['pin'] == pin:
            self.card_data = self.check_credentials(card)
            if self.card_data[1] == pin:
                print('You have successfully logged in!\n')
                self.account()
            else:
                print('Wrong card number or PIN\n')
        except (KeyError, TypeError):
            print('Wrong card number or PIN\n')

    def add_income(self):
        income = int(input('Enter income:'))
        # self.card_data: ('4000001083457267', '7352', 0)   card number, pin, balance
        self.card_data[2] += income
        with sqlite3.connect('card.s3db') as data:
            cursor = data.cursor()
            cursor.execute('''
            UPDATE card SET balance = (?) WHERE number = (?);
            ''', (self.card_data[2], self.card_data[0]))
        print('Income was added!')

    def transfer(self):
        to_acc = input('Transfer\nEnter card number:')
        if BankingSystem.luhn_algorithm(to_acc) is False:
            print('Probably you made a mistake in the card number. Please try again!\n')
            return
        else:
            with sqlite3.connect('card.s3db') as data:
                cursor = data.cursor()
                cursor.execute('''
                SELECT balance FROM card WHERE number = (?);
                ''', (to_acc,))
                to_card = cursor.fetchone()
                if to_card is None:
                    print('Such a card does not exist.\n')
                    return
                else:
                    money = int(input('Enter how much money you want to transfer:'))
                    if self.card_data[2] < money:
                        print('Not enough money!')
                    else:
                        self.card_data[2] -= money
                        cursor.execute('''
                        UPDATE card SET balance = (?) WHERE number = (?);
                        ''', (self.card_data[2], self.card_data[0]))
                        to_balance = to_card[0]
                        to_balance += money
                        cursor.execute('''
                        UPDATE card SET balance = (?) WHERE number = (?);
                        ''', (to_balance, to_acc))
                        print('Success!')

    def close_acc(self):
        with sqlite3.connect('card.s3db') as data:
            cursor = data.cursor()
            cursor.execute('''
            DELETE FROM card WHERE number = (?);
            ''', (self.card_data[0],))
        print('The account has been closed!\n')

    def account(self):
        while True:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            choice = input()
            if choice == '1':
                print(self.card_data[2])
                # print(f"\nBalance: {self.cards[card]['balance']}\n")
            elif choice == '2':
                self.add_income()
            elif choice == '3':
                self.transfer()
            elif choice == '4':
                self.close_acc()
            elif choice == '5':
                self.card_data = None
                print('You have successfully logged out!\n')
                return
            elif choice == '0':
                print('Bye!')
                exit()
            else:
                print('Unknown option.\n')

    @staticmethod
    def end():
        print('Bye!')
        exit()


BankingSystem().menu()
