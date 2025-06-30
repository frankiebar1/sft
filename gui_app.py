import customtkinter as ctk
import datetime
import calendar # For monthrange
from collections import defaultdict

# Assuming financial_tracker.py is in the same directory
from financial_tracker import (
    load_data, save_data,
    Income, RecurringExpense, OccasionalExpense, # Data classes
    parse_date, # Utility
    add_income_item, add_recurring_expense_item, add_occasional_expense_item, # Item adders
    calculate_total_income, calculate_total_recurring_expenses, calculate_total_occasional_expenses # Calculators
)


class FinancialTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Student Financial Tracker")
        self.geometry("1100x750") # Initial size

        # --- Data ---
        self.incomes, self.recurring_expenses, self.occasional_expenses = load_data()
        self.current_month = datetime.date.today().month
        self.current_year = datetime.date.today().year

        # --- Main Layout Frames ---
        self.grid_columnconfigure(0, weight=1) # Control frame
        self.grid_columnconfigure(1, weight=4) # Main display area (increased weight)
        self.grid_rowconfigure(0, weight=1)

        # Control Frame (Left Panel)
        self.control_frame = ctk.CTkFrame(self, width=280) # Slightly wider
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid_propagate(False)

        # Main Display Frame (Right Panel)
        self.display_frame = ctk.CTkFrame(self)
        self.display_frame.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew") # No left padding for display_frame

        self.populate_control_frame()
        self.populate_display_frame_placeholders() # Start with placeholders
        # self.update_display() # Initial data load and display - to be called after widgets are ready

    def populate_control_frame(self):
        self.control_frame.grid_columnconfigure(0, weight=1)

        # Month/Year Selection
        month_year_frame = ctk.CTkFrame(self.control_frame)
        month_year_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        month_year_frame.grid_columnconfigure(0, weight=1) # Allow widgets to expand

        ctk.CTkLabel(month_year_frame, text="View Month & Year:").grid(row=0, column=0, columnspan=2, pady=(0,5))

        self.month_var = ctk.StringVar(value=datetime.date.today().strftime("%B"))
        self.year_var = ctk.StringVar(value=str(self.current_year))

        months = [datetime.date(2000, i, 1).strftime('%B') for i in range(1, 13)]
        ctk.CTkOptionMenu(month_year_frame, variable=self.month_var, values=months, command=self.on_period_change).grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # For simplicity, using an entry for year, could be OptionMenu too
        ctk.CTkEntry(month_year_frame, textvariable=self.year_var, width=80).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkButton(month_year_frame, text="Refresh View", command=self.update_display).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")


        # Action Buttons
        action_buttons_frame = ctk.CTkFrame(self.control_frame)
        action_buttons_frame.grid(row=1, column=0, padx=10, pady=(20,10), sticky="ew") # Pushed towards bottom
        action_buttons_frame.grid_columnconfigure(0, weight=1)


        ctk.CTkButton(action_buttons_frame, text="Add Income", command=self.add_income_window).grid(row=0, column=0, sticky="ew", pady=5)
        ctk.CTkButton(action_buttons_frame, text="Add Recurring Expense", command=self.add_recurring_expense_window).grid(row=1, column=0, sticky="ew", pady=5)
        ctk.CTkButton(action_buttons_frame, text="Add Occasional Expense", command=self.add_occasional_expense_window).grid(row=2, column=0, sticky="ew", pady=5)

        # Spacer to push action buttons to bottom if other elements are added above later
        self.control_frame.grid_rowconfigure(2, weight=1) # Spacer row
        action_buttons_frame.grid(row=3, column=0, padx=10, pady=10, sticky="sew")


    def populate_display_frame_placeholders(self):
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(0, weight=0) # Overview (less weight initially)
        self.display_frame.grid_rowconfigure(1, weight=1) # Fixed Costs
        self.display_frame.grid_rowconfigure(2, weight=1) # Variable Costs
        self.display_frame.grid_rowconfigure(3, weight=1) # Tag Statistics

        # Monthly Overview Section
        overview_frame = ctk.CTkFrame(self.display_frame)
        overview_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        overview_frame.grid_columnconfigure(0, weight=1) # Allow label to expand
        ctk.CTkLabel(overview_frame, text="Monthly Overview", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(5,10))

        self.lbl_total_income = ctk.CTkLabel(overview_frame, text="Total Income: $0.00", font=ctk.CTkFont(size=14))
        self.lbl_total_income.pack(anchor="w", padx=10)
        self.lbl_total_expenses = ctk.CTkLabel(overview_frame, text="Total Expenses: $0.00", font=ctk.CTkFont(size=14))
        self.lbl_total_expenses.pack(anchor="w", padx=10)
        self.lbl_net_balance = ctk.CTkLabel(overview_frame, text="Net Balance: $0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_net_balance.pack(anchor="w", padx=10, pady=(0,5))

        # Fixed Costs (Recurring Expenses) Section
        fixed_costs_frame = ctk.CTkFrame(self.display_frame)
        fixed_costs_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(fixed_costs_frame, text="Fixed Costs (Recurring)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        self.fixed_costs_text = ctk.CTkTextbox(fixed_costs_frame, height=150, state="disabled", font=("Consolas", 12))
        self.fixed_costs_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Variable Costs (Occasional Expenses) Section
        variable_costs_frame = ctk.CTkFrame(self.display_frame)
        variable_costs_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(variable_costs_frame, text="Variable Costs (Occasional)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        self.variable_costs_text = ctk.CTkTextbox(variable_costs_frame, height=150, state="disabled", font=("Consolas", 12))
        self.variable_costs_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Tag-Based Statistics Section
        tag_stats_frame = ctk.CTkFrame(self.display_frame)
        tag_stats_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(tag_stats_frame, text="Spending by Tag", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        self.tag_stats_text = ctk.CTkTextbox(tag_stats_frame, height=150, state="disabled", font=("Consolas", 12))
        self.tag_stats_text.pack(fill="both", expand=True, padx=5, pady=5)

    def on_period_change(self, choice):
        # This is called when month optionmenu changes.
        # We could trigger update_display here, or rely on the "Refresh View" button
        self.update_display() # Auto-refresh on month change for now
        pass

    def update_display(self):
        # 1. Getting the selected month/year
        try:
            selected_month_str = self.month_var.get()
            selected_year_str = self.year_var.get()

            # Convert month name to number
            month_number = datetime.datetime.strptime(selected_month_str, "%B").month
            year_number = int(selected_year_str)

            self.current_month = month_number
            self.current_year = year_number

        except ValueError:
            print("Invalid year format. Please enter a valid year.")
            # Optionally show an error to the user in the GUI
            # For now, just return and don't update
            return

        # 2. Calculate start and end dates for the selected period
        _, num_days_in_month = calendar.monthrange(self.current_year, self.current_month)
        start_date = datetime.date(self.current_year, self.current_month, 1)
        end_date = datetime.date(self.current_year, self.current_month, num_days_in_month)

        # 3. Use actual calculation functions
        total_inc = calculate_total_income(self.incomes, start_date, end_date)
        total_rec_exp = calculate_total_recurring_expenses(self.recurring_expenses, start_date, end_date)
        total_occ_exp = calculate_total_occasional_expenses(self.occasional_expenses, start_date, end_date)
        total_exp = total_rec_exp + total_occ_exp
        net_balance = total_inc - total_exp

        # 4. Update overview labels
        self.lbl_total_income.configure(text=f"Total Income: ${total_inc:.2f}")
        self.lbl_total_expenses.configure(text=f"Total Expenses: ${total_exp:.2f}")
        self.lbl_net_balance.configure(text=f"Net Balance: ${net_balance:.2f}")

        # 5. Populate Fixed Costs (Recurring Expenses) Textbox
        self.fixed_costs_text.configure(state="normal")
        self.fixed_costs_text.delete("1.0", "end")
        fixed_costs_header = f"{'Description':<30} {'Amount':>10} {'Frequency':>10} {'Tags'}\n"
        fixed_costs_header += "-" * (len(fixed_costs_header) -1) + "\n"
        self.fixed_costs_text.insert("end", fixed_costs_header)
        for item in self.recurring_expenses:
            # Check if the recurring item is active in the selected period (simplified check)
            # A more precise check would be to see if at least one payment instance falls in the month
            if item.start_date <= end_date: # Basic check: started before or during the month
                # More accurate: does it actually have a payment in this month?
                # This is implicitly handled by calculate_total_recurring_expenses, but for display list, we need to be sure.
                # For now, list if it *could* be active.
                formatted_tags = ", ".join(item.tags) if item.tags else "None"
                self.fixed_costs_text.insert("end", f"{item.description:<30} ${item.amount:>9.2f} {item.frequency:>10} {formatted_tags}\n")
        self.fixed_costs_text.configure(state="disabled")

        # 6. Populate Variable Costs (Occasional Expenses) Textbox
        self.variable_costs_text.configure(state="normal")
        self.variable_costs_text.delete("1.0", "end")
        variable_costs_header = f"{'Description':<30} {'Amount':>10} {'Date':>12} {'Tags'}\n"
        variable_costs_header += "-" * (len(variable_costs_header) -1) + "\n"
        self.variable_costs_text.insert("end", variable_costs_header)
        for item in self.occasional_expenses:
            if start_date <= item.date <= end_date:
                formatted_tags = ", ".join(item.tags) if item.tags else "None"
                self.variable_costs_text.insert("end", f"{item.description:<30} ${item.amount:>9.2f} {str(item.date):>12} {formatted_tags}\n")
        self.variable_costs_text.configure(state="disabled")

        # 7. Populate Tag-Based Statistics Textbox
        tag_spending = defaultdict(float)
        # Consider recurring expenses active in the month
        for item in self.recurring_expenses:
            # This is a simplification: it adds the full amount if the expense *could* occur.
            # A more accurate tag spending would be to sum actual occurrences in the month.
            # For now, we'll use the logic similar to how calculate_total_recurring_expenses works.

            current_payment_date = item.start_date
            while current_payment_date <= end_date:
                if current_payment_date >= start_date: # Payment occurs within the period
                    for tag in item.tags:
                        tag_spending[tag] += item.amount

                if item.frequency == "weekly": current_payment_date += datetime.timedelta(days=7)
                elif item.frequency == "monthly":
                    next_m, next_y = (current_payment_date.month % 12) + 1, current_payment_date.year + (current_payment_date.month // 12)
                    try: current_payment_date = current_payment_date.replace(year=next_y, month=next_m)
                    except ValueError: # handle day not in next month e.g. Jan 31 to Feb
                        last_day = calendar.monthrange(next_y, next_m)[1]
                        current_payment_date = current_payment_date.replace(year=next_y, month=next_m, day=last_day)
                elif item.frequency == "annually":
                    try: current_payment_date = current_payment_date.replace(year=current_payment_date.year + 1)
                    except ValueError: # Feb 29 on leap year
                        current_payment_date = current_payment_date.replace(year=current_payment_date.year + 1, day=28)
                else: break # unknown frequency
                if current_payment_date > end_date and item.start_date < current_payment_date : # Optimization: if next payment is past period end, stop.
                     break


        for item in self.occasional_expenses:
            if start_date <= item.date <= end_date:
                for tag in item.tags:
                    tag_spending[tag] += item.amount

        self.tag_stats_text.configure(state="normal")
        self.tag_stats_text.delete("1.0", "end")
        if tag_spending:
            tag_header = f"{'Tag':<20} {'Total Spent':>15}\n"
            tag_header += "-" * (len(tag_header)-1) + "\n"
            self.tag_stats_text.insert("end", tag_header)
            for tag, total in sorted(tag_spending.items()):
                self.tag_stats_text.insert("end", f"{tag:<20} ${total:>14.2f}\n")
        else:
            self.tag_stats_text.insert("end", "No tagged expenses this month.")
        self.tag_stats_text.configure(state="disabled")

        print(f"Display updated for {selected_month_str} {selected_year_str} with real data.")

    def save_and_refresh(self):
        """Saves all data and refreshes the main display."""
        save_data(self.incomes, self.recurring_expenses, self.occasional_expenses)
        self.update_display()

    # --- Action methods to open windows ---
    def add_income_window(self):
        # Ensure only one instance of the window is open
        if not hasattr(self, '_add_income_window') or not self._add_income_window.winfo_exists():
            self._add_income_window = AddIncomeWindow(self)
            self._add_income_window.grab_set() # Make window modal
        else:
            self._add_income_window.focus() # Bring to front if already open

    def add_recurring_expense_window(self):
        if not hasattr(self, '_add_recurring_expense_window') or not self._add_recurring_expense_window.winfo_exists():
            self._add_recurring_expense_window = AddRecurringExpenseWindow(self)
            self._add_recurring_expense_window.grab_set()
        else:
            self._add_recurring_expense_window.focus()

    def add_occasional_expense_window(self):
        if not hasattr(self, '_add_occasional_expense_window') or not self._add_occasional_expense_window.winfo_exists():
            self._add_occasional_expense_window = AddOccasionalExpenseWindow(self)
            self._add_occasional_expense_window.grab_set()
        else:
            self._add_occasional_expense_window.focus()

# --- Data Entry Windows ---

class AddIncomeWindow(ctk.CTkToplevel):
    def __init__(self, master_app: FinancialTrackerApp):
        super().__init__(master_app)
        self.master_app = master_app

        self.title("Add Income")
        self.geometry("450x350") # Adjusted size
        self.resizable(False, False)

        # Center on master window (approximately)
        # master_x = master_app.winfo_x()
        # master_y = master_app.winfo_y()
        # master_width = master_app.winfo_width()
        # master_height = master_app.winfo_height()
        # self.geometry(f"+{master_x + master_width//2 - 225}+{master_y + master_height//2 - 175}")


        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Source:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.source_entry = ctk.CTkEntry(main_frame, width=250)
        self.source_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.amount_entry = ctk.CTkEntry(main_frame, width=250)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(main_frame, width=250)
        self.date_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        self.date_entry.insert(0, datetime.date.today().isoformat()) # Default to today

        ctk.CTkLabel(main_frame, text="Frequency:").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.frequency_var = ctk.StringVar(value="once")
        frequencies = ["once", "weekly", "monthly", "annually"]
        ctk.CTkOptionMenu(main_frame, variable=self.frequency_var, values=frequencies).grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        self.error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=(0,10))

        button_frame = ctk.CTkFrame(main_frame) # Frame for buttons
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10,0))

        submit_button = ctk.CTkButton(button_frame, text="Add Income", command=self.submit_income)
        submit_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="gray")
        cancel_button.pack(side="left", padx=10)

        main_frame.grid_columnconfigure(1, weight=1) # Allow entry widgets to expand
        self.source_entry.focus() # Set focus to the first entry

    def submit_income(self):
        source = self.source_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get().strip()
        frequency = self.frequency_var.get()

        self.error_label.configure(text="") # Clear previous errors

        if not source or not amount_str or not date_str:
            self.error_label.configure(text="Source, Amount, and Date are required.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                self.error_label.configure(text="Amount must be positive.")
                return
        except ValueError:
            self.error_label.configure(text="Invalid amount format.")
            return

        try:
            income_date = parse_date(date_str) # Use imported parse_date
        except ValueError:
            self.error_label.configure(text="Invalid date. Use YYYY-MM-DD.")
            return

        # print(f"DUMMY SUBMIT Income: Source: {source}, Amount: {amount}, Date: {income_date}, Frequency: {frequency}")

        try:
            add_income_item(self.master_app.incomes, source, amount, income_date, frequency)
            self.master_app.save_and_refresh()
            self.destroy()
        except Exception as e:
            self.error_label.configure(text=f"Error adding income: {e}")
            return


class AddRecurringExpenseWindow(ctk.CTkToplevel):
    def __init__(self, master_app: FinancialTrackerApp):
        super().__init__(master_app)
        self.master_app = master_app

        self.title("Add Recurring Expense")
        self.geometry("450x400") # Slightly taller for tags
        self.resizable(False, False)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Description:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.description_entry = ctk.CTkEntry(main_frame, width=250)
        self.description_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.amount_entry = ctk.CTkEntry(main_frame, width=250)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Frequency:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.frequency_var = ctk.StringVar(value="monthly")
        frequencies = ["weekly", "monthly", "annually"]
        ctk.CTkOptionMenu(main_frame, variable=self.frequency_var, values=frequencies).grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.start_date_entry = ctk.CTkEntry(main_frame, width=250)
        self.start_date_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        self.start_date_entry.insert(0, datetime.date.today().isoformat())

        ctk.CTkLabel(main_frame, text="Tags (comma-sep):").grid(row=4, column=0, padx=5, pady=10, sticky="w")
        self.tags_entry = ctk.CTkEntry(main_frame, width=250)
        self.tags_entry.grid(row=4, column=1, padx=5, pady=10, sticky="ew")

        self.error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.error_label.grid(row=5, column=0, columnspan=2, pady=(0,10))

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10,0))

        submit_button = ctk.CTkButton(button_frame, text="Add Expense", command=self.submit_expense)
        submit_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="gray")
        cancel_button.pack(side="left", padx=10)

        main_frame.grid_columnconfigure(1, weight=1)
        self.description_entry.focus()

    def submit_expense(self):
        description = self.description_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        frequency = self.frequency_var.get()
        start_date_str = self.start_date_entry.get().strip()
        tags_str = self.tags_entry.get().strip()

        self.error_label.configure(text="")

        if not description or not amount_str or not start_date_str:
            self.error_label.configure(text="Description, Amount, and Start Date are required.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                self.error_label.configure(text="Amount must be positive.")
                return
        except ValueError:
            self.error_label.configure(text="Invalid amount format.")
            return

        try:
            start_date = parse_date(start_date_str) # Use imported parse_date
        except ValueError:
            self.error_label.configure(text="Invalid start date. Use YYYY-MM-DD.")
            return

        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

        # print(f"DUMMY SUBMIT Recurring Expense: Desc: {description}, Amount: {amount}, Freq: {frequency}, Start: {start_date}, Tags: {tags}")
        try:
            add_recurring_expense_item(self.master_app.recurring_expenses, description, amount, frequency, start_date, tags)
            self.master_app.save_and_refresh()
            self.destroy()
        except Exception as e:
            self.error_label.configure(text=f"Error adding recurring expense: {e}")
            return


class AddOccasionalExpenseWindow(ctk.CTkToplevel):
    def __init__(self, master_app: FinancialTrackerApp):
        super().__init__(master_app)
        self.master_app = master_app

        self.title("Add Occasional Expense")
        self.geometry("450x350")
        self.resizable(False, False)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Description:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.description_entry = ctk.CTkEntry(main_frame, width=250)
        self.description_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.amount_entry = ctk.CTkEntry(main_frame, width=250)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(main_frame, width=250)
        self.date_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        self.date_entry.insert(0, datetime.date.today().isoformat())

        ctk.CTkLabel(main_frame, text="Tags (comma-sep):").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.tags_entry = ctk.CTkEntry(main_frame, width=250)
        self.tags_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        self.error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        self.error_label.grid(row=4, column=0, columnspan=2, pady=(0,10))

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10,0))

        submit_button = ctk.CTkButton(button_frame, text="Add Expense", command=self.submit_expense)
        submit_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, fg_color="gray")
        cancel_button.pack(side="left", padx=10)

        main_frame.grid_columnconfigure(1, weight=1)
        self.description_entry.focus()

    def submit_expense(self):
        description = self.description_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get().strip()
        tags_str = self.tags_entry.get().strip()

        self.error_label.configure(text="")

        if not description or not amount_str or not date_str:
            self.error_label.configure(text="Description, Amount, and Date are required.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                self.error_label.configure(text="Amount must be positive.")
                return
        except ValueError:
            self.error_label.configure(text="Invalid amount format.")
            return

        try:
            expense_date = parse_date(date_str) # Use imported parse_date
        except ValueError:
            self.error_label.configure(text="Invalid date. Use YYYY-MM-DD.")
            return

        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

        # print(f"DUMMY SUBMIT Occasional Expense: Desc: {description}, Amount: {amount}, Date: {expense_date}, Tags: {tags}")
        try:
            add_occasional_expense_item(self.master_app.occasional_expenses, description, amount, expense_date, tags)
            self.master_app.save_and_refresh()
            self.destroy()
        except Exception as e:
            self.error_label.configure(text=f"Error adding occasional expense: {e}")
            return


if __name__ == "__main__":
    # ctk.set_appearance_mode("dark") # or "light"
    # ctk.set_default_color_theme("blue") # or "green", "dark-blue"
    app = FinancialTrackerApp()
    app.after(100, app.update_display) # Call update_display shortly after app starts
    app.mainloop()
```
