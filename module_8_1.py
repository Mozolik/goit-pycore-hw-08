from collections import UserDict
from datetime import datetime, date, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        try:
            if isinstance(value, str):
                datetime.strptime(value, "%d.%m.%Y")
            else:
                raise ValueError
            super().__init__(value)
        except ValueError:
            raise ValueError("Недійсний формат дати, використання DD.MM.YYYY")

class Name(Field):
    # реалізація класу
    pass


class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону має містити рівно 10 цифр")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        phone_value = self.find_phone(phone)
        if phone_value:
            self.phones.remove(phone_value)
        else:
            raise ValueError("Номер телефону не знайдено")

    def edit_phone(self, phone_old: str, phone_new: str):
        phone = self.find_phone(phone_old)
        if not phone:
            raise ValueError("Номер телефону не знайдено")

        new_phone_value = Phone(phone_new)

        index = self.phones.index(phone)
        self.phones[index] = new_phone_value

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "no phones"
        birthday_str = f"birthday: {self.birthday.value}" if self.birthday else "birthday: no birthday"
        return f"Contact name: {self.name.value}, phones: {phones_str}, {birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name) 

    def delete(self, name):
        self.data.pop(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        end_date = today + timedelta(days=7)
        result = []

        for user in self.data.values():
            name = user.name.value 
            if user.birthday == None:
                continue    

            birthday = datetime.strptime(user.birthday.value, "%d.%m.%Y").date()

            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if today <= birthday_this_year <= end_date:
                congratulations_date = birthday_this_year

                if congratulations_date.weekday() == 5:  
                    congratulations_date += timedelta(days=2)
                elif congratulations_date.weekday() == 6:  
                    congratulations_date += timedelta(days=1)

                result.append({
                    "name": name,
                    "birthday": congratulations_date.strftime("%d.%m.%Y")
                })

        return result

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())  

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)  
        except (ValueError,IndexError):
            return "Invalid input."
        except (KeyError, AttributeError):
            return "Contact is not found"
    return inner

def parse_input(user_input: str):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, phone_old, phone_new, *_ = args
    record = book.find(name)
    record.edit_phone(phone_old, phone_new)
    return "Phone number changed."

@input_error
def show_phones(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record.phones:
        return "No phones."
    return "; ".join(p.value for p in record.phones)

@input_error
def all_contacts(args, book: AddressBook):
    if not book.data:
        return "No contacts."
    return str(book)

@input_error
def add_birthday(args, book: AddressBook):
    name, bday_str, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
    record.add_birthday(bday_str)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record.birthday:
        return "Birthday not set."
    return record.birthday.value

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    lines = [f"{item['name']}: {item['birthday']}" for item in upcoming]
    return "\n".join(lines)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()