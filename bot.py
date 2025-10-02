from datetime import datetime, date, timedelta
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value: str):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be exactly 10 digits")
        super().__init__(value)

class Birthday:
    def __init__(self, date_str: str):
        try:
            self.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Birthday must be in YYYY-MM-DD format")

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None

    def add_birthday(self, date_str: str):
        self.birthday = Birthday(date_str)

    def add_phone(self, number: str):
        self.phones.append(Phone(number))

    def remove_phone(self, number: str):
        phone_obj = self.find_phone(number)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone not found")

    def edit_phone(self, old: str, new: str):
        phone_obj = self.find_phone(old)
        if not phone_obj:
            raise ValueError("Old phone not found")
        self.phones[self.phones.index(phone_obj)] = Phone(new)

    def find_phone(self, number: str):
        return next((p for p in self.phones if p.value == number), None)

    def __str__(self):
        phones = ": ".join(p.value for p in self.phones)
        bday = str(self.birthday) if self.birthday else "not set"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {bday}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        self.data.pop(name, None)

    def __str__(self):
        return "\n".join(str(rec) for rec in self.data.values())

    def get_upcoming_birthdays(self):
        result = []
        today = date.today()
        for record in self.data.values():
            if record.birthday is None:
                continue
            bday = record.birthday.date.replace(year=today.year)
            if bday < today:
                bday = bday.replace(year=today.year + 1)
            if bday.weekday() == 5:
                bday += timedelta(days=2)
            elif bday.weekday() == 6:
                bday += timedelta(days=1)
            if 0 <= (bday - today).days <= 6:
                result.append({"name": record.name.value, "birthday": bday.strftime("%Y-%m-%d")})
        return result

def parse_input(user_input: str):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]

def add_contact(args, book: AddressBook):
    if len(args) != 2:
        return "Usage: add <name> <phone>"
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return f"Contact {name} added/updated."

def change_contact(args, book: AddressBook):
    if len(args) != 3:
        return "Usage: change <name> <old_phone> <new_phone>"
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone for {name} changed."

def phone_username(args, book: AddressBook):
    if len(args) != 1:
        return "Usage: phone <name>"
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    phones = "; ".join(p.value for p in record.phones)
    return f"{name}: {phones}"

def all_contacts(book: AddressBook):
    return str(book) if book.data else "No contacts found."

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(phone_username(args, book))
        elif command == "show" and args and args[0] == "all":
            print(all_contacts(book))
        elif command == "birthdays":
            upcoming = book.get_upcoming_birthdays()
            if upcoming:
                for item in upcoming:
                    print(f"{item['name']} -> {item['birthday']}")
            else:
                print("No upcoming birthdays in the next 7 days.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

