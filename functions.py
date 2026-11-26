import os
import pandas as pd

USERS_FILE = "users.csv"
RECORDS_FILE = "tax_records.csv"
YEAR_OF_ASSESSMENT = 2026

TAX_BANDS = [(5000, 0.00),
    (20000, 0.01),
    (35000, 0.03),
    (50000, 0.06),
    (70000, 0.11),
    (100000, 0.19),
    (400000, 0.25),
    (600000, 0.26),
    (2000000, 0.28),
    (float("inf"), 0.30),]

REBATE_AMOUNT = 400.00
REBATE_LIMIT = 35000.00

RECORD_KEYS = ["user_id", "test_case_id", "year_of_assessment", "annual_income",
    "total_tax_relief", "chargeable_income", "tax_before_rebate",
    "tax_rebate", "final_tax_payable",]

TEST_CASES = [
    ("T01", 9000, 9000),
    ("T02", 40000, 9000),
    ("T03", 65000, 14000),
    ("T04", 120000, 18000),
    ("T05", 83000, 12000),]

def validate_user_id(user_id):
    return len(user_id) > 0 and " " not in user_id and "," not in user_id


def validate_ic(ic):
    return len(ic) == 12 and ic.isdigit()


def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt).replace(",", ""))
        except ValueError:
            print("Error: please enter a valid number.")
            continue
        if value < 0 or value != value or value == float("inf"):
            print("Error: please enter a normal number that is not negative.")
        else:
            return value

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        df = pd.read_csv(USERS_FILE, dtype=str)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return []
    return df.to_dict("records")


def user_exists(user_id):
    for user in load_users():
        if user["user_id"] == user_id:
            return True
    return False


def register_user(user_id, ic):
    if not validate_user_id(user_id):
        return False, "Invalid User ID (cannot be empty or contain spaces/commas)."
    if not validate_ic(ic):
        return False, "Invalid IC number (must be exactly 12 digits)."
    if user_exists(user_id):
        return False, "User ID already exists."

    keys = ["user_id", "ic"]
    values = [user_id, ic]
    user = dict(zip(keys, values))          # list -> dictionary
    df = pd.DataFrame([user])               # dictionary -> DataFrame
    try:
        df.to_csv(USERS_FILE, mode="a", header=not os.path.exists(USERS_FILE), index=False)
    except OSError as error:
        return False, f"Could not save user: {error}"
    return True, "Registration successful. Your password is the last 4 digits of your IC."


def authenticate(user_id, password):
    for user in load_users():
        if user["user_id"] == user_id and user["ic"][-4:] == password:
            return True
    return False

def calculate_chargeable_income(annual_income, total_relief):
    return round(max(0.0, annual_income - total_relief), 2)


def calculate_tax_before_rebate(chargeable_income):
    tax = 0.0
    lower = 0.0
    for upper, rate in TAX_BANDS:
        if chargeable_income > lower:
            tax += (min(chargeable_income, upper) - lower) * rate
        lower = upper
    return round(tax, 2)


def calculate_rebate(chargeable_income, tax_before_rebate):
    if chargeable_income <= REBATE_LIMIT:
        return round(min(REBATE_AMOUNT, tax_before_rebate), 2)
    return 0.0


def calculate_final_tax(tax_before_rebate, rebate):
    return round(max(0.0, tax_before_rebate - rebate), 2)


def build_tax_record(user_id, annual_income, total_relief, test_case_id=""):
    chargeable = calculate_chargeable_income(annual_income, total_relief)
    tax_before = calculate_tax_before_rebate(chargeable)
    rebate = calculate_rebate(chargeable, tax_before)
    final_tax = calculate_final_tax(tax_before, rebate)

    values = [user_id, test_case_id, YEAR_OF_ASSESSMENT, annual_income,
              total_relief, chargeable, tax_before, rebate, final_tax]
    return dict(zip(RECORD_KEYS, values))    # list -> dictionary with meaningful keys


def display_result(record):
    print("\n----- TAX CALCULATION RESULT -----")
    print(f"Year of Assessment  : {record['year_of_assessment']}")
    print(f"Annual Income       : RM{record['annual_income']:,.2f}")
    print(f"Total Tax Relief    : RM{record['total_tax_relief']:,.2f}")
    print(f"Chargeable Income   : RM{record['chargeable_income']:,.2f}")
    print(f"Tax Before Rebate   : RM{record['tax_before_rebate']:,.2f}")
    print(f"Tax Rebate          : RM{record['tax_rebate']:,.2f}")
    print(f"Final Tax Payable   : RM{record['final_tax_payable']:,.2f}")
    print("----------------------------------")

def save_records(records):
    df = pd.DataFrame(records, columns=RECORD_KEYS)    # list of dicts -> DataFrame
    try:
        df.to_csv(RECORDS_FILE, mode="a", header=not os.path.exists(RECORDS_FILE), index=False)
    except OSError as error:
        print(f"Error: could not save records ({error}).")
        return False
    return True


def save_record(record):
    return save_records([record])


def load_records():
    if not os.path.exists(RECORDS_FILE):
        return pd.DataFrame(columns=RECORD_KEYS)
    try:
        return pd.read_csv(RECORDS_FILE, dtype={"user_id": str, "test_case_id": str})
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=RECORD_KEYS)


def display_user_records(user_id):
    df = load_records()
    df = df[(df["user_id"] == user_id) & (df["test_case_id"].isna())]
    if df.empty:
        print("\nNo saved records found.")
        return
    print(f"\n----- SAVED TAX RECORDS FOR {user_id} -----")
    print(df.drop(columns=["user_id", "test_case_id"]).to_string(index=False))


def display_test_cases():
    df = load_records()
    df = df[df["test_case_id"].notna()]
    if df.empty:
        print("\nNo test case records saved yet.")
        return
    print("\n----- SAVED TEST CASE RECORDS -----")
    print(df.drop(columns=["user_id"]).to_string(index=False))


def run_test_cases():
    df = load_records()
    already_saved = df[df["test_case_id"].notna()]["test_case_id"].tolist()
    new_records = []
    for case_id, income, relief in TEST_CASES:
        if case_id in already_saved:
            continue
        new_records.append(build_tax_record("TEST", income, relief, case_id))
    if new_records:
        save_records(new_records)
        print(f"{len(new_records)} test case record(s) saved to {RECORDS_FILE}.")
    else:
        print("Test cases were already saved earlier. Showing saved records.")
    display_test_cases()