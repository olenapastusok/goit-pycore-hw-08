from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    """Зберігання імені контакту"""
    def __init__(self, value):
        super().__init__(value)
        if not value:
            raise ValueError("Name cannot be empty")

class Phone(Field):
    """Клас, який забезпечує валідацію номера телефону"""
    def __init__(self, value):
        super().__init__(value)
        """перевірка на 10 цифр"""
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number shoud have 10 digits")
        

class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date()
            self.value = birthday
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    """Клас, який відповідає за додавання, видалення, редагування та пошук телефонів"""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        """Додавання нового телефону"""
        return self.phones.append(Phone(phone))
    
    def add_birthday(self, birthday_value):
        """Додає день народження до контакту"""
        self.birthday = Birthday(birthday_value)

    
    def remove_phone(self, phone):
        """Видаляє номер телефону, який вказано на вхід"""
        ph = self.find_phone(phone)
        if ph:
            self.phones.remove(ph)
            return True
        return False
    
    def edit_phone(self, old_phone, new_phone):
        """Змінює старий номер телефону на новий"""
        ph = self.find_phone(old_phone)
        if ph:
            index = self.phones.index(ph)
            self.phones[index] = Phone(new_phone)
            return True
        return False
    
    def find_phone(self, phone):
        """Пошук телефону в записах"""
        for ph in self.phones:
            if ph.value == phone:
                return ph
        return None

    def __str__(self):
        phone_str = '; '.join(p.value for p in self.phones) 
        bithday_str = f", birthday: {self.birthday}" if self.birthday else " Bithday was not added"
        return f"Contact name: {self.name.value}, phones: {phone_str}{bithday_str}"

class AddressBook(UserDict):
    """" Клас, який відповідає за додавання нових записів, пошук записів за іменем та видалення записів за іменем"""
    def add_record(self, record):
        """Функція додавання нових записів"""
        self.data[record.name.value] = record
    
    def find(self, name):
          """Знаходить запис за вказаним іменем"""
          return self.data.get(name)

    def delete(self, name):
        """Видалення записів за іменем"""
        if name in self.data:
            del self.data[name]
    
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value
                this_year_bday = bday.replace(year=today.year)
                if this_year_bday < today:
                    this_year_bday = this_year_bday.replace(year=today.year + 1)
                delta_days = (this_year_bday - today).days
                if 0 <= delta_days <= 6:
                    congr_date = this_year_bday
                    if congr_date.weekday() == 5:
                        congr_date += timedelta(days=2)
                    elif congr_date.weekday() == 6:
                        congr_date += timedelta(days=1)
                    upcoming.append({
                        "name": record.name.value,
                        "congratulation_date": congr_date.strftime("%d.%m.%Y")
                    })
        return upcoming


def input_error(func):
    """Функція обробок помилок"""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"{e}"
        except Exception as e:
            return f"Unexceptional error, please check data one more time: {e}"
        except IndexError:
            return "There are not enoght arguments. Please enter all arguments."

    return inner

def parse_input(user_input: str):
    """Функція, яка парсить дані: ділить на команду і що необхідно зробити"""
    if not user_input:
        return None, []
    
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

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
def change_contact(args, book: AddressBook):
    name, old_phone_number, new_phone_number = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(old_phone_number, new_phone_number)
    return "Pnone number was updated"

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    return '; '.join(p.value for p in record.phones)

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "The Adress book is empty"
    result = []
    for item in book.data.values():
        result.append(str(item))
    return "\n".join(result)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise KeyError

    record.add_birthday(birthday)
    return "Bithday updated."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    return record.birthday if record.birthday else "Bithday was not added"

@input_error
def birthdays(book: AddressBook):
    b_days = book.get_upcoming_birthdays()
    if not b_days:
        return "The Birthday was not added"
    result = []
    for item in b_days:
        result.append(f"{item['name']}: {item['congratulation_date']}")
    return "\n".join(result)

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
    book = AddressBook()
    print("Welcome to the assistant bot!")
    book = load_data()
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
           print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()