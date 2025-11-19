import json
import os
from datetime import datetime
import matplotlib.pyplot as plt


# Constants
RECEIPT_STORE = "receipts.json"
TAX_RATE = 0.08
TIP_OPTIONS = [0.10, 0.15, 0.20]


def display_welcome():
    print("------------------------------------------")
    print("           Welcome to The Bistro!         ")
    print("------------------------------------------\n")
    print("Type 'help' to see available commands.\n")


def display_food_menu():
    print("️  FOOD MENU")
    print("1. Chicken Alfredo Pasta - $7.99")
    print("2. Pepperoni Pizza - $8.99")
    print("3. Famous Salad - $6.99")
    print("4. steak frites - $12.99\n")


def display_drink_menu():
    print("  DRINK MENU")
    print("4. Coffee - $2.99")
    print("5. Tea - $3.99")
    print("6. Juice - $3.99")
    print("7. Soda - $2.99\n")


def display_menu():
    print("\n------ MENU ------ ")
    display_food_menu()
    display_drink_menu()
    print("-----------------------\n")


def show_help():
    print("\n COMMANDS:")
    print(" show   - Display the menu again")
    print(" cart   - Show your current order")
    print(" remove - Remove an item from your cart")
    print(" done   - Checkout")
    print(" history - List saved receipts")
    print(" view X - View saved receipt number X")
    print(" chart  - Show spending graph")
    print(" help   - Show commands")
    print(" quit   - Exit\n")


def load_receipts(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except (IOError, ValueError):
        print("Warning: could not read saved receipts; starting fresh.")
        return []


def save_receipts(path, receipts):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(receipts, f, ensure_ascii=False, indent=2)
    except IOError:
        print("Error: failed to save receipts to disk.")


def add_item_to_cart(name, menu, cart):
    matched = None
    for key in menu.keys():
        if key.lower() == name.lower():
            matched = key
            break
    if matched is None:
        print("Sorry, that item is not on the menu.")
        return
    cart[matched] = cart.get(matched, 0) + 1
    print(f"{matched} has been added to your cart.")


def show_cart(cart):
    if not cart:
        print("Your cart is currently empty.")
        return
    print("YOUR CART")
    total_items = 0
    for item, qty in cart.items():
        print(f" - {item} x{qty}")
        total_items += qty
    print("------------------")
    print(f"Total items: {total_items}")


def remove_item(cart):
    if not cart:
        print("Nothing to remove.")
        return
    remove_name = input("Enter the item to remove: ").strip()
    matched = None
    for key in cart.keys():
        if key.lower() == remove_name.lower():
            matched = key
            break
    if matched is None:
        print("Item not found in your cart.")
        return
    cart[matched] -= 1
    if cart[matched] <= 0:
        del cart[matched]
    print(f"{matched} has been removed from your cart.")


def calculate_totals(cart, menu):
    subtotal = 0.0
    lines = []
    for item, qty in cart.items():
        price = menu[item]
        line_total = price * qty
        lines.append((item, qty, price, line_total))
        subtotal += line_total
    tax = subtotal * TAX_RATE
    return subtotal, tax, lines


def choose_tip(subtotal):
    print("Choose tip option:")
    for i, t in enumerate(TIP_OPTIONS, 1):
        print(f" {i}. {int(t * 100)}%")
    print(f" {len(TIP_OPTIONS) + 1}. Custom amount")
    choice = input("Select 1-{0} (enter to skip tip): ".format(len(TIP_OPTIONS) + 1)).strip()
    if choice == "":
        return 0.0
    try:
        idx = int(choice)
        if 1 <= idx <= len(TIP_OPTIONS):
            return round(subtotal * TIP_OPTIONS[idx - 1], 2)
        elif idx == len(TIP_OPTIONS) + 1:
            custom = input("Enter custom tip amount (e.g. 3.50): ").strip()
            return float(custom)
    except Exception:
        pass
    print("Invalid tip choice; no tip will be added.")
    return 0.0


def format_money(value):
    return f"${value:,.2f}"


def checkout(cart, menu, receipts_store):
    if not cart:
        print("Nothing to checkout.")
        return

    print("\nReceipt")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    subtotal, tax, lines = calculate_totals(cart, menu)
    for item, qty, price, line_total in lines:
        print(f" - {item} (x{qty}) @ {format_money(price)} = {format_money(line_total)}")

    print("------------------")
    print(f"Subtotal: {format_money(subtotal)}")
    print(f"Sales tax ({int(TAX_RATE * 100)}%): {format_money(tax)}")
    tip_amount = choose_tip(subtotal)
    print(f"Tip: {format_money(tip_amount)}")

    total_due = subtotal + tax + tip_amount
    print(f"TOTAL DUE: {format_money(total_due)}")
    print("------------------")
    server = input("Enter server name (optional): ").strip()
    print("Thank you for dining at The Bistro!")

    receipt = {
        "timestamp": datetime.now().isoformat(),
        "server": server,
        "items": [{"name": i, "qty": q, "price": menu[i]} for i, q in cart.items()],
        "subtotal": subtotal,
        "tax": tax,
        "tip": tip_amount,
        "total": total_due
    }

    receipts_store.append(receipt)
    save_receipts(RECEIPT_STORE, receipts_store)
    cart.clear()


def list_receipts(receipts):
    if not receipts:
        print("No saved receipts.")
        return
    for i, r in enumerate(receipts, 1):
        t = r.get("timestamp", "unknown")
        total = r.get("total", 0.0)
        server = r.get("server", "")
        print(f"{i}. {t} - {format_money(total)}", end="")
        if server:
            print(f" - server: {server}")
        else:
            print()


def view_receipt(receipts, index):
    try:
        r = receipts[index]
    except IndexError:
        print("Receipt number not found.")
        return

    print("Saved Receipt")
    print(f"Date: {r.get('timestamp')}")
    if r.get("server"):
        print(f"Server: {r.get('server')}")

    for it in r.get("items", []):
        name = it.get("name")
        qty = it.get("qty")
        price = it.get("price")
        print(f" - {name} x{qty} @ {format_money(price)} = {format_money(price * qty)}")

    print("------------------")
    print(f"Subtotal: {format_money(r.get('subtotal', 0))}")
    print(f"Tax: {format_money(r.get('tax', 0))}")
    print(f"Tip: {format_money(r.get('tip', 0))}")
    print(f"TOTAL: {format_money(r.get('total', 0))}")
    print("------------------")



def show_spending_chart(receipts):
    if not receipts:
        print("No receipts available to chart.")
        return

    totals = [r.get("total", 0) for r in receipts]
    labels = [f"R{i+1}" for i in range(len(receipts))]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, totals)
    plt.title("Total Spending per Receipt")
    plt.xlabel("Receipt Number")
    plt.ylabel("Total ($)")
    plt.tight_layout()
    plt.show()


def main():
    menu = {
        "Chicken Alfredo Pasta": 7.99,
        "Pepperoni Pizza": 8.99,
        "Famous Salad": 6.99,
        "Coffee": 2.99,
        "Tea": 3.99,
        "Juice": 3.99,
        "Soda": 2.99
    }

    cart = {}
    receipts = load_receipts(RECEIPT_STORE)

    display_welcome()
    display_menu()
    show_help()

    while True:
        user_input = input("\nEnter command or item name: ").strip()
        if user_input == "":
            continue

        cmd = user_input.lower()

        if cmd == "help":
            show_help()
        elif cmd == "show":
            display_menu()
        elif cmd == "cart":
            show_cart(cart)
        elif cmd == "remove":
            remove_item(cart)
        elif cmd == "done":
            checkout(cart, menu, receipts)
        elif cmd == "history":
            list_receipts(receipts)
        elif cmd.startswith("view"):
            parts = user_input.split()
            if len(parts) == 2 and parts[1].isdigit():
                view_receipt(receipts, int(parts[1]) - 1)
            else:
                print("Usage: view X")
        elif cmd == "chart":
            show_spending_chart(receipts)
        elif cmd == "quit":
            print("Thank you for visiting The Bistro!")
            break
        else:
            add_item_to_cart(user_input, menu, cart)


if __name__ == "__main__":
    main()
