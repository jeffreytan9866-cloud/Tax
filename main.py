from functions import (register_user, authenticate, get_positive_float, build_tax_record,
    display_result, save_record, display_user_records, run_test_cases,)

def register_menu():
    print("\n--- REGISTER ---")
    user_id = input("Enter User ID: ").strip()
    ic = input("Enter 12-digit IC number (no dashes): ").strip()
    success, message = register_user(user_id, ic)
    print(message)

def login_menu():
    print("\n--- LOGIN ---")
    attempts = 3
    while attempts > 0:
        user_id = input("User ID: ").strip()
        password = input("Password (last 4 digits of IC): ").strip()
        if authenticate(user_id, password):
            print(f"Login successful. Welcome, {user_id}!")
            return user_id
        attempts -= 1
        print(f"Invalid User ID or password. Attempts left: {attempts}")
    print("Too many failed attempts.")
    return None

def tax_menu(user_id):
    while True:
        print(f"\n--- TAX MENU ({user_id}) ---")
        print("1. Calculate income tax")
        print("2. View my saved tax records")
        print("3. Run and view the 5 test cases (T01-T05)")
        print("4. Logout")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            annual_income = get_positive_float("Enter annual income (RM): ")
            total_relief = get_positive_float("Enter total eligible tax relief (RM): ")
            record = build_tax_record(user_id, annual_income, total_relief)
            display_result(record)
            if input("Save this record? (y/n): ").strip().lower() == "y":
                if save_record(record):
                    print("Record saved.")
        elif choice == "2":
            display_user_records(user_id)
        elif choice == "3":
            run_test_cases()
        elif choice == "4":
            print("Logged out.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")


def main():
    while True:
        print("\n===== MALAYSIAN TAX INPUT PROGRAM (YA 2026) =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            register_menu()
        elif choice == "2":
            user_id = login_menu()
            if user_id:
                tax_menu(user_id)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2 or 3.")
if __name__ == "__main__":
    main()