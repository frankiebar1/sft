# financial_tracker.py

import datetime
import json
import os

DATA_FILE = "financial_data.json"

class Income:
    def __init__(self, source: str, amount: float, date: datetime.date, frequency: str = "once"):
        self.source = source
        self.amount = amount
        self.date = date
        self.frequency = frequency # e.g., "once", "weekly", "monthly"

    def __str__(self):
        return f"Income: {self.source}, Amount: ${self.amount:.2f}, Date: {self.date}, Frequency: {self.frequency}"

class RecurringExpense:
    def __init__(self, description: str, amount: float, frequency: str, start_date: datetime.date):
        self.description = description
        self.amount = amount
        self.frequency = frequency # e.g., "weekly", "monthly", "annually"
        self.start_date = start_date
        self.tags: list[str] = tags if tags is not None else []

    def __str__(self):
        return f"Recurring Expense: {self.description}, Amount: ${self.amount:.2f}, Frequency: {self.frequency}, Starts: {self.start_date}, Tags: {self.tags}"

class OccasionalExpense:
    def __init__(self, description: str, amount: float, date: datetime.date, tags: list[str] | None = None):
        self.description = description
        self.amount = amount
        self.date = date
        self.tags: list[str] = tags if tags is not None else []

    def __str__(self):
        return f"Occasional Expense: {self.description}, Amount: ${self.amount:.2f}, Date: {self.date}, Tags: {self.tags}"

def main():
    # This main function will eventually be replaced by the GUI application setup
    print("Welcome to the Student Financial Tracker!")

    # Example usage (we'll build out the CLI later)
    salary = Income("Part-time Job", 200.00, datetime.date(2023, 10, 27), "weekly")
    rent = RecurringExpense("Rent", 500.00, "monthly", datetime.date(2023, 11, 1))
    textbook = OccasionalExpense("Biology Textbook", 75.50, datetime.date(2023, 10, 15))

    print("\n--- Sample Data ---")
    print(salary)
    print(rent)
    print(textbook)

    print("\n--- Adding items through functions ---")
    incomes = []
    recurring_expenses = []
    occasional_expenses = []

    new_income = add_income_item(incomes, "Scholarship", 1000.00, "2023-09-01", "once")
    new_recurring_expense = add_recurring_expense_item(recurring_expenses, "Gym Membership", 30.00, "monthly", "2023-10-01")
    new_occasional_expense = add_occasional_expense_item(occasional_expenses, "Concert Ticket", 65.00, "2023-11-05")

    print("\n--- All Items ---")
    for item in incomes:
        print(item)
    for item in recurring_expenses:
        print(item)
    for item in occasional_expenses:
        print(item)

    print("\n--- Financial Summaries (Oct 2023) ---")
    start_period = datetime.date(2023, 10, 1)
    end_period = datetime.date(2023, 10, 31)

    total_inc = calculate_total_income(incomes, start_period, end_period)
    total_rec_exp = calculate_total_recurring_expenses(recurring_expenses, start_period, end_period)
    total_occ_exp = calculate_total_occasional_expenses(occasional_expenses, start_period, end_period)
    net_balance = total_inc - total_rec_exp - total_occ_exp

    print(f"Total Income ({start_period} to {end_period}): ${total_inc:.2f}")
    print(f"Total Recurring Expenses ({start_period} to {end_period}): ${total_rec_exp:.2f}")
    print(f"Total Occasional Expenses ({start_period} to {end_period}): ${total_occ_exp:.2f}")
    # CLI interaction will replace direct calls here
    # print(f"Net Balance ({start_period} to {end_period}): ${net_balance:.2f}")

    # Load data at startup
    incomes, recurring_expenses, occasional_expenses = load_data()


    # --- CLI Loop ---
    while True:
        print("\nStudent Financial Tracker")
        print("1. Add Income")
        print("2. Add Recurring Expense")
        print("3. Add Occasional Expense")
        print("4. View Monthly Summary")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            add_income_cli(incomes)
            save_data(incomes, recurring_expenses, occasional_expenses)
        elif choice == '2':
            add_recurring_expense_cli(recurring_expenses)
            save_data(incomes, recurring_expenses, occasional_expenses)
        elif choice == '3':
            add_occasional_expense_cli(occasional_expenses)
            save_data(incomes, recurring_expenses, occasional_expenses)
        elif choice == '4':
            view_monthly_summary_cli(incomes, recurring_expenses, occasional_expenses)
        elif choice == '5':
            print("Exiting tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# --- CLI Helper Functions ---
def get_date_input(prompt: str) -> datetime.date | None:
    date_str = input(prompt + " (YYYY-MM-DD): ")
    try:
        return parse_date(date_str)
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return None

def add_income_cli(income_list: list[Income]):
    print("\n--- Add Income ---")
    source = input("Enter income source: ")
    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    date_obj = get_date_input("Enter date")
    if not date_obj:
        return

    frequency = input("Enter frequency (e.g., once, weekly, monthly - default 'once'): ") or "once"

    income_item = Income(source, amount, date_obj, frequency)
    income_list.append(income_item)
    print(f"Added: {income_item}")
    # Save after adding
    # For simplicity, passing all lists to save_data. Could be optimized.
    # Need to define incomes, recurring_expenses, occasional_expenses in the scope or pass them.
    # This will be handled by where add_income_cli is called from (main)

def add_recurring_expense_cli(expense_list: list[RecurringExpense]):
    print("\n--- Add Recurring Expense ---")
    description = input("Enter expense description: ")
    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    frequency = input("Enter frequency (weekly, monthly, annually): ")
    if frequency not in ["weekly", "monthly", "annually"]:
        print("Invalid frequency. Must be 'weekly', 'monthly', or 'annually'.")
        return

    start_date_obj = get_date_input("Enter start date")
    if not start_date_obj:
        return

    tags_str = input("Enter tags (comma-separated, e.g., food,utility): ")
    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

    # Call the core function, which now accepts tags
    expense_item = RecurringExpense(description, amount, frequency, start_date_obj, tags=tags)
    expense_list.append(expense_item) # Appending is technically done in add_recurring_expense_item, but good to be explicit if that changes
    print(f"Added: {expense_item}")

def add_occasional_expense_cli(expense_list: list[OccasionalExpense]):
    print("\n--- Add Occasional Expense ---")
    description = input("Enter expense description: ")
    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("Invalid amount.")
        return

    date_obj = get_date_input("Enter date")
    if not date_obj:
        return

    tags_str = input("Enter tags (comma-separated, e.g., books,entertainment): ")
    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

    # Call the core function, which now accepts tags
    expense_item = OccasionalExpense(description, amount, date_obj, tags=tags)
    expense_list.append(expense_item) # Appending is technically done in add_occasional_expense_item
    print(f"Added: {expense_item}")

def view_monthly_summary_cli(incomes: list[Income], recurring_expenses: list[RecurringExpense], occasional_expenses: list[OccasionalExpense]):
    print("\n--- View Monthly Summary ---")
    try:
        year = int(input("Enter year (e.g., 2023): "))
        month = int(input("Enter month (1-12): "))
        if not (1 <= month <= 12):
            print("Invalid month. Please enter a number between 1 and 12.")
            return
    except ValueError:
        print("Invalid year or month format.")
        return

    import calendar
    _, num_days = calendar.monthrange(year, month)
    start_period = datetime.date(year, month, 1)
    end_period = datetime.date(year, month, num_days)

    print(f"\n--- Financial Summary for {start_period.strftime('%B %Y')} ---")

    total_inc = calculate_total_income(incomes, start_period, end_period)
    total_rec_exp = calculate_total_recurring_expenses(recurring_expenses, start_period, end_period)
    total_occ_exp = calculate_total_occasional_expenses(occasional_expenses, start_period, end_period)
    net_balance = total_inc - total_rec_exp - total_occ_exp

    print(f"Total Income: ${total_inc:.2f}")
    print(f"Total Recurring Expenses: ${total_rec_exp:.2f}")
    print(f"Total Occasional Expenses: ${total_occ_exp:.2f}")
    print(f"Net Balance: ${net_balance:.2f}")


# --- Functions to add items (kept for potential direct use/testing, CLI functions wrap them) ---
def parse_date(date_str: str) -> datetime.date:
    """Helper function to parse date strings."""
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def add_income_item(income_list: list, source: str, amount: float, date_obj: datetime.date, frequency: str = "once") -> Income:
    """Adds an income item to the provided list."""
    # date_obj = parse_date(date_str) # Date parsing now happens in CLI or directly
    income_item = Income(source, amount, date_obj, frequency)
    income_list.append(income_item)
    # print(f"Added: {income_item}") # Logging moved to CLI functions
    return income_item

def add_recurring_expense_item(expense_list: list, description: str, amount: float, frequency: str, start_date_obj: datetime.date, tags: list[str] | None = None) -> RecurringExpense:
    """Adds a recurring expense item to the provided list."""
    expense_item = RecurringExpense(description, amount, frequency, start_date_obj, tags=tags)
    expense_list.append(expense_item)
    # print(f"Added: {expense_item}")
    return expense_item

def add_occasional_expense_item(expense_list: list, description: str, amount: float, date_obj: datetime.date, tags: list[str] | None = None) -> OccasionalExpense:
    """Adds an occasional expense item to the provided list."""
    expense_item = OccasionalExpense(description, amount, date_obj, tags=tags)
    expense_list.append(expense_item)
    # print(f"Added: {expense_item}")
    return expense_item

# --- Data Persistence Functions ---
def save_data(incomes: list[Income], recurring_expenses: list[RecurringExpense], occasional_expenses: list[OccasionalExpense]):
    data_to_save = {
        "incomes": [item.__dict__ for item in incomes],
        "recurring_expenses": [item.__dict__ for item in recurring_expenses],
        "occasional_expenses": [item.__dict__ for item in occasional_expenses],
    }
    # Convert datetime.date objects to ISO format strings
    for item_list_key in data_to_save:
        for item_dict in data_to_save[item_list_key]:
            for key, value in item_dict.items():
                if isinstance(value, datetime.date):
                    item_dict[key] = value.isoformat()

    with open(DATA_FILE, 'w') as f:
        json.dump(data_to_save, f, indent=4)
    print(f"Data saved to {DATA_FILE}")

def load_data() -> tuple[list[Income], list[RecurringExpense], list[OccasionalExpense]]:
    incomes = []
    recurring_expenses = []
    occasional_expenses = []

    if not os.path.exists(DATA_FILE):
        return incomes, recurring_expenses, occasional_expenses

    try:
        with open(DATA_FILE, 'r') as f:
            data_loaded = json.load(f)

        for item_data in data_loaded.get("incomes", []):
            item_data['date'] = datetime.date.fromisoformat(item_data['date'])
            incomes.append(Income(**item_data))

        for item_data in data_loaded.get("recurring_expenses", []):
            item_data['start_date'] = datetime.date.fromisoformat(item_data['start_date'])
            # Ensure 'tags' key exists, defaulting to empty list if not (for backward compatibility)
            item_data.setdefault('tags', [])
            recurring_expenses.append(RecurringExpense(**item_data))

        for item_data in data_loaded.get("occasional_expenses", []):
            item_data['date'] = datetime.date.fromisoformat(item_data['date'])
            # Ensure 'tags' key exists, defaulting to empty list if not
            item_data.setdefault('tags', [])
            occasional_expenses.append(OccasionalExpense(**item_data))

        print(f"Data loaded from {DATA_FILE}")

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error loading data from {DATA_FILE}: {e}. Starting with empty data.")
        # Return empty lists in case of file corruption or format issues
        return [], [], []

    return incomes, recurring_expenses, occasional_expenses

# --- Functions to calculate summaries ---
def calculate_total_income(income_list: list[Income], start_date: datetime.date, end_date: datetime.date) -> float:
    total = 0.0
    for item in income_list:
        if not all([isinstance(d, datetime.date) for d in [item.date, start_date, end_date]]):
            # print(f"Warning: Skipping income item '{item.source}' due to None date in calculation period.")
            continue

        if item.frequency == "once":
            if start_date <= item.date <= end_date:
                total += item.amount
        elif item.frequency == "weekly":
            if item.date <= end_date: # Ensure the income starts before or during the period end
                current_date = item.date
                while current_date <= end_date:
                    if current_date >= start_date:
                        total += item.amount
                    current_date += datetime.timedelta(days=7)
        elif item.frequency == "monthly":
            if item.date <= end_date: # Ensure the income starts before or during the period end
                current_month_date = item.date
                while current_month_date <= end_date:
                    if current_month_date >= start_date:
                        total += item.amount
                    # Move to next month
                    next_m, next_y = (current_month_date.month % 12) + 1, current_month_date.year + (current_month_date.month // 12)
                    try:
                        current_month_date = current_month_date.replace(year=next_y, month=next_m)
                    except ValueError: # Handles day not in next month e.g. Jan 31 to Feb
                        import calendar
                        last_day_of_next_month = calendar.monthrange(next_y, next_m)[1]
                        current_month_date = current_month_date.replace(year=next_y, month=next_m, day=last_day_of_next_month)

    return total

def calculate_total_recurring_expenses(expense_list: list[RecurringExpense], start_date: datetime.date, end_date: datetime.date) -> float:
    total = 0.0
    for item in expense_list:
        if not all([isinstance(d, datetime.date) for d in [item.start_date, start_date, end_date]]):
            # print(f"Warning: Skipping recurring expense item '{item.description}' due to None date in calculation period.")
            continue

        if item.start_date > end_date: # Expense starts after the period ends
            continue

        current_payment_date = item.start_date
        while current_payment_date <= end_date:
            if current_payment_date >= start_date: # Payment occurs within the period
                total += item.amount

            if item.frequency == "weekly":
                current_payment_date += datetime.timedelta(days=7)
            elif item.frequency == "monthly":
                # Advance to the next month, keeping the day the same (or last day of month if original day is too large)
                next_month = current_payment_date.month + 1
                next_year = current_payment_date.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                try:
                    current_payment_date = current_payment_date.replace(year=next_year, month=next_month)
                except ValueError: # Handles cases like advancing from Jan 31st to Feb
                    import calendar
                    last_day_of_next_month = calendar.monthrange(next_year, next_month)[1]
                    current_payment_date = current_payment_date.replace(year=next_year, month=next_month, day=last_day_of_next_month)
            elif item.frequency == "annually":
                try:
                    current_payment_date = current_payment_date.replace(year=current_payment_date.year + 1)
                except ValueError: # handles leap year Feb 29
                     current_payment_date = current_payment_date.replace(year=current_payment_date.year + 1, day=28)
            else: # Unknown frequency
                break # Avoid infinite loop for unknown frequencies
    return total

def calculate_total_occasional_expenses(expense_list: list[OccasionalExpense], start_date: datetime.date, end_date: datetime.date) -> float:
    total = 0.0
    for item in expense_list:
        if not all([isinstance(d, datetime.date) for d in [item.date, start_date, end_date]]):
            # print(f"Warning: Skipping occasional expense item '{item.description}' due to None date in calculation period.")
            continue
        if start_date <= item.date <= end_date:
            total += item.amount
    return total

if __name__ == "__main__":
    main()
