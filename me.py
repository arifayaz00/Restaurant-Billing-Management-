import tkinter as tk
from tkinter import ttk, messagebox, font
import json, os, datetime

# ---------------- CONFIG ----------------
FILE = "bills.json"
HISTORY_FILE = "history.json"
TAX = 0.05
SERVICE = 0.10

MENU = {
    "🥗 Starters": {
        "S01": ("Vegetable Soup", 120, 60),
        "S02": ("Chicken Wings", 180, 100),
        "S03": ("Spring Rolls", 150, 80),
        "S04": ("Garlic Bread", 90, 40),
        "S05": ("French Fries", 100, 50),
        "S06": ("Onion Rings", 110, 55),
        "S07": ("Stuffed Mushrooms", 160, 85),
        "S08": ("Prawn Cocktail", 220, 130),
        "S09": ("Caesar Salad", 200, 110),
        "S10": ("Nachos with Dip", 130, 65),
    },
    "🍖 Main Course": {
        "M01": ("Grilled Chicken", 350, 220),
        "M02": ("Beef Steak", 550, 350),
        "M03": ("Pasta Alfredo", 280, 150),
        "M04": ("Chicken Biryani", 300, 180),
        "M05": ("Fish Curry", 320, 200),
        "M06": ("Lamb Chops", 480, 300),
        "M07": ("Vegetable Stir Fry", 240, 120),
        "M08": ("Butter Chicken", 330, 190),
        "M09": ("Seafood Platter", 600, 380),
        "M10": ("Mushroom Risotto", 270, 140),
        "M11": ("Tandoori Chicken", 360, 210),
        "M12": ("BBQ Pork Ribs", 520, 330),
    },
    "🍔 Fast Food": {
        "F01": ("Beef Burger", 220, 120),
        "F02": ("Chicken Burger", 200, 110),
        "F03": ("Veggie Burger", 180, 90),
        "F04": ("Club Sandwich", 190, 100),
        "F05": ("Hotdog", 150, 70),
        "F06": ("Shawarma", 170, 85),
        "F07": ("Pizza Slice", 180, 90),
        "F08": ("Loaded Fries", 160, 80),
    },
    "🍹 Beverages": {
        "B01": ("Soft Drink", 60, 20),
        "B02": ("Coffee", 80, 30),
        "B03": ("Tea", 50, 20),
        "B04": ("Fresh Juice", 120, 60),
        "B05": ("Mango Lassi", 110, 55),
        "B06": ("Cold Coffee", 130, 65),
        "B07": ("Lemonade", 80, 35),
        "B08": ("Mineral Water", 40, 15),
        "B09": ("Milkshake", 150, 75),
        "B10": ("Hot Chocolate", 100, 50),
    },
    "🎂 Desserts": {
        "D01": ("Ice Cream", 120, 60),
        "D02": ("Brownie", 140, 70),
        "D03": ("Cake Slice", 150, 80),
        "D04": ("Tiramisu", 180, 90),
        "D05": ("Cheesecake", 170, 85),
        "D06": ("Pudding", 130, 65),
        "D07": ("Fruit Tart", 160, 80),
    }
}

# ---------------- COLORS ----------------
BG        = "#1a1a2e"
PANEL     = "#16213e"
CARD      = "#0f3460"
ACCENT    = "#e94560"
ACCENT2   = "#f5a623"
GREEN     = "#00b894"
TEAL      = "#00cec9"
TEXT      = "#eaeaea"
SUBTEXT   = "#a0a0b0"
WHITE     = "#ffffff"
DARK_BTN  = "#0f3460"

# ---------------- FILE ----------------
def load(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def next_id(bills):
    return max([b["id"] for b in bills], default=1000) + 1


# ---------------- APP ----------------
class POS:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️  SpiceByte Restaurant POS")
        self.root.geometry("1350x780")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.bills   = load(FILE)
        self.history = load(HISTORY_FILE)
        self.cart    = []

        self._apply_styles()
        self.build_ui()

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
            background=CARD, foreground=TEXT,
            fieldbackground=CARD, rowheight=26,
            font=("Consolas", 10))
        style.configure("Treeview.Heading",
            background=ACCENT, foreground=WHITE,
            font=("Consolas", 10, "bold"))
        style.map("Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", WHITE)])

        style.configure("History.Treeview",
            background="#0a2744", foreground=TEXT,
            fieldbackground="#0a2744", rowheight=26,
            font=("Consolas", 10))
        style.configure("History.Treeview.Heading",
            background=GREEN, foreground=WHITE,
            font=("Consolas", 10, "bold"))
        style.map("History.Treeview",
            background=[("selected", GREEN)],
            foreground=[("selected", WHITE)])

    # -------- UI --------
    def build_ui(self):
        # Top header
        header = tk.Frame(self.root, bg=ACCENT, height=50)
        header.pack(fill="x")
        tk.Label(header, text="🍽️  SpiceByte Restaurant POS",
                 font=("Georgia", 18, "bold"),
                 bg=ACCENT, fg=WHITE).pack(side="left", padx=20, pady=10)
        self.clock_lbl = tk.Label(header, text="", font=("Consolas", 11),
                                  bg=ACCENT, fg=WHITE)
        self.clock_lbl.pack(side="right", padx=20)
        self._tick()

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=10, pady=8)

        # ---- LEFT: Menu ----
        left = tk.Frame(main, bg=PANEL, bd=0, relief="flat")
        left.pack(side="left", fill="both", expand=True, padx=(0,6))

        tk.Label(left, text="📋  MENU", font=("Georgia", 14, "bold"),
                 bg=PANEL, fg=ACCENT2).pack(pady=(8,4))

        # Search bar
        sf = tk.Frame(left, bg=PANEL)
        sf.pack(fill="x", padx=8, pady=2)
        tk.Label(sf, text="🔍", bg=PANEL, fg=SUBTEXT).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_menu)
        tk.Entry(sf, textvariable=self.search_var,
                 bg=CARD, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=("Consolas", 10)).pack(side="left", fill="x", expand=True, padx=4)

        tree_frame = tk.Frame(left, bg=PANEL)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self.menu_tree = ttk.Treeview(tree_frame)
        self.menu_tree["columns"] = ("Price",)
        self.menu_tree.column("#0", width=260)
        self.menu_tree.column("Price", width=80, anchor="e")
        self.menu_tree.heading("#0", text="Item")
        self.menu_tree.heading("Price", text="Price ৳")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.menu_tree.pack(fill="both", expand=True)

        self._populate_menu()

        # Qty row
        qf = tk.Frame(left, bg=PANEL)
        qf.pack(fill="x", padx=8, pady=6)
        tk.Label(qf, text="Qty:", bg=PANEL, fg=TEXT,
                 font=("Consolas", 11)).pack(side="left")
        self.qty = tk.Spinbox(qf, from_=1, to=99, width=5,
                              bg=CARD, fg=ACCENT2, insertbackground=TEXT,
                              buttonbackground=CARD, relief="flat",
                              font=("Consolas", 12, "bold"))
        self.qty.pack(side="left", padx=6)

        tk.Button(qf, text="➕ Add", bg=GREEN, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.add_item,
                  padx=8).pack(side="left", padx=4)
        tk.Button(qf, text="➖ Remove", bg=ACCENT, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.remove_item,
                  padx=8).pack(side="left", padx=4)

        # ---- RIGHT: Cart + Controls ----
        right = tk.Frame(main, bg=PANEL, width=400)
        right.pack(side="right", fill="both", padx=(6,0))
        right.pack_propagate(False)

        tk.Label(right, text="🛒  ORDER", font=("Georgia", 14, "bold"),
                 bg=PANEL, fg=TEAL).pack(pady=(8,4))

        # Customer / Table
        inf = tk.Frame(right, bg=PANEL)
        inf.pack(fill="x", padx=8, pady=2)
        self.customer = tk.Entry(inf, bg=CARD, fg=TEXT,
                                  insertbackground=TEXT, relief="flat",
                                  font=("Consolas", 10))
        self.customer.insert(0, "👤 Customer Name")
        self.customer.pack(side="left", fill="x", expand=True, padx=(0,4), ipady=4)

        self.table = tk.Entry(inf, bg=CARD, fg=TEXT,
                               insertbackground=TEXT, relief="flat",
                               font=("Consolas", 10), width=10)
        self.table.insert(0, "🪑 Table")
        self.table.pack(side="right", ipady=4)

        # Cart listbox
        cf = tk.Frame(right, bg=PANEL)
        cf.pack(fill="both", expand=True, padx=8, pady=4)
        self.cart_box = tk.Listbox(cf, bg=CARD, fg=TEXT, selectbackground=ACCENT,
                                    font=("Consolas", 10), relief="flat",
                                    highlightthickness=0, bd=0)
        csb = ttk.Scrollbar(cf, orient="vertical", command=self.cart_box.yview)
        self.cart_box.configure(yscrollcommand=csb.set)
        csb.pack(side="right", fill="y")
        self.cart_box.pack(fill="both", expand=True)

        # Totals panel
        totals = tk.Frame(right, bg=DARK_BTN)
        totals.pack(fill="x", padx=8, pady=4)
        self.sub_lbl   = tk.Label(totals, text="Subtotal:  ৳0.00",
                                   bg=DARK_BTN, fg=SUBTEXT, font=("Consolas", 10))
        self.sub_lbl.pack(anchor="w", padx=10, pady=2)
        self.tax_lbl   = tk.Label(totals, text="Tax (5%): ৳0.00",
                                   bg=DARK_BTN, fg=SUBTEXT, font=("Consolas", 10))
        self.tax_lbl.pack(anchor="w", padx=10)
        self.svc_lbl   = tk.Label(totals, text="Service (10%): ৳0.00",
                                   bg=DARK_BTN, fg=SUBTEXT, font=("Consolas", 10))
        self.svc_lbl.pack(anchor="w", padx=10, pady=2)
        self.total_lbl = tk.Label(totals, text="TOTAL:  ৳0.00",
                                   bg=DARK_BTN, fg=ACCENT2,
                                   font=("Georgia", 14, "bold"))
        self.total_lbl.pack(anchor="w", padx=10, pady=6)

        # Action buttons
        btns = [
            ("💳 Checkout",       ACCENT,  self.checkout),
            ("📄 View Bills",     CARD,    self.view_bills),
            ("📜 View History",   GREEN,   self.view_history),
            ("🔍 Search Bill",    TEAL,    self.search_bill),
            ("✅ Mark Paid",      "#5f27cd", self.mark_paid),
            ("🗑️  Delete Bill",   "#636e72", self.delete_bill),
            ("📊 Daily Summary",  ACCENT2, self.summary),
            ("🗑️  Clear Cart",    "#d63031", self.clear_cart),
        ]
        for txt, color, cmd in btns:
            tk.Button(right, text=txt, bg=color, fg=WHITE,
                      font=("Consolas", 10, "bold"), relief="flat",
                      cursor="hand2", command=cmd,
                      anchor="w", padx=12, pady=5).pack(
                          fill="x", padx=8, pady=2)

    # -------- MENU HELPERS --------
    def _populate_menu(self, filter_text=""):
        for i in self.menu_tree.get_children():
            self.menu_tree.delete(i)
        ft = filter_text.lower()
        for cat, items in MENU.items():
            parent = None
            for code, (name, price, cost) in items.items():
                if ft in name.lower() or ft in code.lower() or ft == "":
                    if parent is None:
                        parent = self.menu_tree.insert("", "end", text=cat,
                                                        tags=("cat",))
                        self.menu_tree.tag_configure("cat",
                            foreground=ACCENT2, font=("Georgia", 10, "bold"))
                    self.menu_tree.insert(parent, "end",
                                          text=f"  {code}  {name}",
                                          values=(f"৳{price}",))

    def _filter_menu(self, *args):
        self._populate_menu(self.search_var.get())

    def _tick(self):
        now = datetime.datetime.now().strftime("%a %d %b %Y   %H:%M:%S")
        self.clock_lbl.config(text=now)
        self.root.after(1000, self._tick)

    # -------- CART --------
    def add_item(self):
        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showerror("Error", "Please select a menu item first.")
            return
        item = self.menu_tree.item(sel[0])
        parts = item["text"].strip().split()
        if not parts or parts[0] not in [c for cat in MENU.values() for c in cat]:
            messagebox.showerror("Error", "Please select an item (not a category).")
            return
        code = parts[0]
        try:
            qty = int(self.qty.get())
            if qty < 1:
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter a valid quantity.")
            return

        for cat in MENU.values():
            if code in cat:
                name, price, cost = cat[code]
                # merge if already in cart
                for c in self.cart:
                    if c["name"] == name:
                        c["qty"] += qty
                        c["total"] += price * qty
                        c["cost"]  += cost  * qty
                        self._refresh_cart_display()
                        self.update_total()
                        return
                self.cart.append({
                    "code": code, "name": name,
                    "qty": qty, "price": price,
                    "total": price * qty, "cost": cost * qty
                })
                self._refresh_cart_display()
                self.update_total()
                return

    def remove_item(self):
        sel = self.cart_box.curselection()
        if not sel:
            messagebox.showerror("Error", "Select an item in the cart to remove.")
            return
        i = sel[0]
        self.cart_box.delete(i)
        del self.cart[i]
        self.update_total()

    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
            self.cart = []
            self.cart_box.delete(0, tk.END)
            self.update_total()

    def _refresh_cart_display(self):
        self.cart_box.delete(0, tk.END)
        for c in self.cart:
            self.cart_box.insert(tk.END,
                f"  {c['name']:25s} x{c['qty']:2d}  ৳{c['total']:,.0f}")

    def update_total(self):
        subtotal = sum(i["total"] for i in self.cart)
        tax      = subtotal * TAX
        service  = subtotal * SERVICE
        total    = subtotal + tax + service
        self.sub_lbl.config(text=f"Subtotal:       ৳{subtotal:,.2f}")
        self.tax_lbl.config(text=f"Tax (5%):       ৳{tax:,.2f}")
        self.svc_lbl.config(text=f"Service (10%):  ৳{service:,.2f}")
        self.total_lbl.config(text=f"TOTAL:  ৳{total:,.2f}")

    # -------- BILL --------
    def checkout(self):
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty.")
            return
        cname = self.customer.get().strip()
        tname = self.table.get().strip()
        if cname in ("", "👤 Customer Name"):
            cname = "Walk-in"
        if tname in ("", "🪑 Table"):
            tname = "—"

        subtotal   = sum(i["total"] for i in self.cart)
        total_cost = sum(i["cost"]  for i in self.cart)
        tax        = subtotal * TAX
        service    = subtotal * SERVICE
        total      = subtotal + tax + service
        profit     = subtotal - total_cost

        bill = {
            "id":       next_id(self.bills),
            "date":     str(datetime.datetime.now()),
            "customer": cname,
            "table":    tname,
            "items":    [{"name": i["name"], "qty": i["qty"],
                          "price": i["price"], "total": i["total"],
                          "cost": i["cost"]} for i in self.cart],
            "subtotal": round(subtotal, 2),
            "tax":      round(tax, 2),
            "service":  round(service, 2),
            "cost":     round(total_cost, 2),
            "profit":   round(profit, 2),
            "total":    round(total, 2),
            "status":   "unpaid"
        }

        self.bills.append(bill)
        save(FILE, self.bills)

        receipt = (
            f"{'─'*36}\n"
            f"  🧾 BILL #{bill['id']}\n"
            f"  Customer: {cname}   Table: {tname}\n"
            f"{'─'*36}\n"
        )
        for it in self.cart:
            receipt += f"  {it['name'][:22]:22s} x{it['qty']}  ৳{it['total']:,.0f}\n"
        receipt += (
            f"{'─'*36}\n"
            f"  Subtotal:    ৳{subtotal:>8,.2f}\n"
            f"  Tax (5%):    ৳{tax:>8,.2f}\n"
            f"  Service:     ৳{service:>8,.2f}\n"
            f"{'─'*36}\n"
            f"  TOTAL:       ৳{total:>8,.2f}\n"
            f"  Status:      UNPAID\n"
            f"{'─'*36}\n"
        )
        messagebox.showinfo(f"Bill #{bill['id']} Created", receipt)

        self.cart = []
        self.cart_box.delete(0, tk.END)
        self.update_total()
        self.customer.delete(0, tk.END)
        self.customer.insert(0, "👤 Customer Name")
        self.table.delete(0, tk.END)
        self.table.insert(0, "🪑 Table")

    # -------- MARK PAID --------
    def mark_paid(self):
        win = self._mini_win("✅ Mark Bill as Paid", 360, 160)
        tk.Label(win, text="Enter Bill ID to mark as PAID:",
                 bg=BG, fg=TEXT, font=("Consolas", 11)).pack(pady=12)
        e = tk.Entry(win, bg=CARD, fg=ACCENT2, insertbackground=TEXT,
                     font=("Consolas", 13, "bold"), width=12, justify="center")
        e.pack(pady=4)
        e.focus()

        def go():
            try:
                bid = int(e.get())
            except:
                messagebox.showerror("Error", "Enter a valid numeric Bill ID.", parent=win)
                return
            for b in self.bills:
                if b["id"] == bid:
                    b["status"] = "paid"
                    b["paid_at"] = str(datetime.datetime.now())
                    self.history.append(b)
                    self.bills.remove(b)
                    save(FILE, self.bills)
                    save(HISTORY_FILE, self.history)
                    messagebox.showinfo("✅ Paid", f"Bill #{bid} marked paid & moved to history!", parent=win)
                    win.destroy()
                    return
            messagebox.showerror("Error", f"Bill #{bid} not found in active bills.", parent=win)

        tk.Button(win, text="Mark Paid", bg=GREEN, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  command=go).pack(pady=8)

    # -------- VIEW BILLS --------
    def view_bills(self):
        win = tk.Toplevel(self.root)
        win.title("📄 Active Bills")
        win.geometry("700x420")
        win.configure(bg=BG)

        tk.Label(win, text="📄 ACTIVE BILLS", font=("Georgia", 14, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=10)

        frame = tk.Frame(win, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        tree = ttk.Treeview(frame)
        tree["columns"] = ("Customer", "Table", "Total", "Status", "Date")
        tree.column("#0",        width=70,  anchor="center")
        tree.column("Customer",  width=130, anchor="w")
        tree.column("Table",     width=70,  anchor="center")
        tree.column("Total",     width=100, anchor="e")
        tree.column("Status",    width=80,  anchor="center")
        tree.column("Date",      width=170, anchor="w")
        tree.heading("#0",       text="ID")
        tree.heading("Customer", text="Customer")
        tree.heading("Table",    text="Table")
        tree.heading("Total",    text="Total ৳")
        tree.heading("Status",   text="Status")
        tree.heading("Date",     text="Date")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for b in self.bills:
            date_str = b["date"][:19] if b.get("date") else "—"
            tree.insert("", "end",
                        text=b["id"],
                        values=(b.get("customer","—"),
                                b.get("table","—"),
                                f"৳{b['total']:,.2f}",
                                b["status"].upper(),
                                date_str))

        tk.Label(win, text=f"Total active bills: {len(self.bills)}",
                 bg=BG, fg=SUBTEXT, font=("Consolas", 10)).pack(pady=4)

    # -------- VIEW HISTORY --------
    def view_history(self):
        # Reload from disk to make sure it's fresh
        self.history = load(HISTORY_FILE)

        win = tk.Toplevel(self.root)
        win.title("📜 Payment History")
        win.geometry("820x480")
        win.configure(bg=BG)

        tk.Label(win, text="📜 PAYMENT HISTORY", font=("Georgia", 14, "bold"),
                 bg=BG, fg=GREEN).pack(pady=10)

        # Summary bar
        total_rev    = sum(b.get("total",0)  for b in self.history)
        total_profit = sum(b.get("profit",0) for b in self.history)
        bar = tk.Frame(win, bg=DARK_BTN)
        bar.pack(fill="x", padx=10, pady=4)
        tk.Label(bar, text=f"  Total Bills: {len(self.history)}",
                 bg=DARK_BTN, fg=TEXT, font=("Consolas", 10)).pack(side="left", padx=10)
        tk.Label(bar, text=f"Revenue: ৳{total_rev:,.2f}",
                 bg=DARK_BTN, fg=ACCENT2, font=("Consolas", 10, "bold")).pack(side="left", padx=10)
        tk.Label(bar, text=f"Profit: ৳{total_profit:,.2f}",
                 bg=DARK_BTN, fg=GREEN, font=("Consolas", 10, "bold")).pack(side="left", padx=10)

        frame = tk.Frame(win, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        tree = ttk.Treeview(frame, style="History.Treeview")
        tree["columns"] = ("Customer", "Table", "Subtotal", "Total", "Profit", "Paid At")
        tree.column("#0",         width=65,  anchor="center")
        tree.column("Customer",   width=120, anchor="w")
        tree.column("Table",      width=60,  anchor="center")
        tree.column("Subtotal",   width=90,  anchor="e")
        tree.column("Total",      width=100, anchor="e")
        tree.column("Profit",     width=90,  anchor="e")
        tree.column("Paid At",    width=170, anchor="w")
        tree.heading("#0",        text="ID")
        tree.heading("Customer",  text="Customer")
        tree.heading("Table",     text="Table")
        tree.heading("Subtotal",  text="Subtotal ৳")
        tree.heading("Total",     text="Total ৳")
        tree.heading("Profit",    text="Profit ৳")
        tree.heading("Paid At",   text="Paid At")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for b in reversed(self.history):        # newest first
            paid_at = b.get("paid_at", b.get("date","—"))[:19]
            tree.insert("", "end",
                        text=b["id"],
                        values=(b.get("customer","—"),
                                b.get("table","—"),
                                f"৳{b.get('subtotal',0):,.2f}",
                                f"৳{b['total']:,.2f}",
                                f"৳{b.get('profit',0):,.2f}",
                                paid_at))

        # Detail on double-click
        def on_select(event):
            sel = tree.selection()
            if not sel:
                return
            bid = tree.item(sel[0])["text"]
            for b in self.history:
                if b["id"] == bid:
                    detail = (
                        f"Bill #{b['id']}\n"
                        f"Customer: {b.get('customer','—')}\n"
                        f"Table: {b.get('table','—')}\n"
                        f"Date: {b.get('date','—')[:19]}\n"
                        f"Paid: {b.get('paid_at','—')[:19]}\n\n"
                        + "\n".join(f"  {i['name']} x{i['qty']} = ৳{i['total']:,.0f}"
                                    for i in b.get("items", []))
                        + f"\n\nSubtotal: ৳{b.get('subtotal',0):,.2f}"
                          f"\nTax:      ৳{b.get('tax',0):,.2f}"
                          f"\nService:  ৳{b.get('service',0):,.2f}"
                          f"\nTOTAL:    ৳{b['total']:,.2f}"
                          f"\nProfit:   ৳{b.get('profit',0):,.2f}"
                    )
                    messagebox.showinfo(f"Bill #{bid} Detail", detail, parent=win)

        tree.bind("<Double-1>", on_select)
        tk.Label(win, text="Double-click a row to see full bill detail",
                 bg=BG, fg=SUBTEXT, font=("Consolas", 9)).pack(pady=3)

    # -------- SEARCH BILL --------
    def search_bill(self):
        win = self._mini_win("🔍 Search Bill", 360, 160)
        tk.Label(win, text="Enter Bill ID:", bg=BG, fg=TEXT,
                 font=("Consolas", 11)).pack(pady=12)
        e = tk.Entry(win, bg=CARD, fg=TEAL, insertbackground=TEXT,
                     font=("Consolas", 13, "bold"), width=12, justify="center")
        e.pack(pady=4)
        e.focus()

        def go():
            try:
                bid = int(e.get())
            except:
                messagebox.showerror("Error", "Enter a valid Bill ID.", parent=win)
                return
            self.history = load(HISTORY_FILE)
            for b in self.bills + self.history:
                if b["id"] == bid:
                    detail = (
                        f"Bill #{b['id']}  [{b['status'].upper()}]\n"
                        f"Customer: {b.get('customer','—')}\n"
                        f"Table: {b.get('table','—')}\n"
                        f"Date: {b.get('date','—')[:19]}\n\n"
                        + "\n".join(f"  {i['name']} x{i['qty']} = ৳{i['total']:,.0f}"
                                    for i in b.get("items",[]))
                        + f"\n\nTOTAL:  ৳{b['total']:,.2f}"
                          f"\nProfit: ৳{b.get('profit',0):,.2f}"
                    )
                    messagebox.showinfo(f"Bill #{bid}", detail, parent=win)
                    return
            messagebox.showerror("Not Found", f"Bill #{bid} does not exist.", parent=win)

        tk.Button(win, text="Search", bg=TEAL, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  command=go).pack(pady=8)

    # -------- DELETE BILL --------
    def delete_bill(self):
        win = self._mini_win("🗑️ Delete Bill", 360, 170)
        tk.Label(win, text="Enter Bill ID to DELETE:", bg=BG, fg=TEXT,
                 font=("Consolas", 11)).pack(pady=12)
        e = tk.Entry(win, bg=CARD, fg=ACCENT, insertbackground=TEXT,
                     font=("Consolas", 13, "bold"), width=12, justify="center")
        e.pack(pady=4)
        e.focus()

        def go():
            try:
                bid = int(e.get())
            except:
                messagebox.showerror("Error", "Enter a valid Bill ID.", parent=win)
                return
            if not messagebox.askyesno("Confirm", f"Delete Bill #{bid}?", parent=win):
                return
            before = len(self.bills)
            self.bills = [b for b in self.bills if b["id"] != bid]
            if len(self.bills) < before:
                save(FILE, self.bills)
                messagebox.showinfo("Deleted", f"Bill #{bid} deleted.", parent=win)
                win.destroy()
            else:
                messagebox.showerror("Error", f"Bill #{bid} not found.", parent=win)

        tk.Button(win, text="Delete", bg=ACCENT, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  command=go).pack(pady=8)

    # -------- DAILY SUMMARY --------
    def summary(self):
        self.history = load(HISTORY_FILE)
        today = datetime.date.today().strftime("%Y-%m-%d")
        today_bills = [b for b in self.history if b.get("date","").startswith(today)]

        revenue     = sum(b.get("total",0)  for b in today_bills)
        profit      = sum(b.get("profit",0) for b in today_bills)
        cost        = sum(b.get("cost",0)   for b in today_bills)
        items_sold  = sum(sum(i["qty"] for i in b.get("items",[])) for b in today_bills)

        msg = (
            f"📅 Daily Summary — {today}\n"
            f"{'─'*34}\n"
            f"  Bills Closed:   {len(today_bills)}\n"
            f"  Items Sold:     {items_sold}\n"
            f"{'─'*34}\n"
            f"  Revenue:  ৳{revenue:>10,.2f}\n"
            f"  Cost:     ৳{cost:>10,.2f}\n"
            f"  Profit:   ৳{profit:>10,.2f}\n"
            f"{'─'*34}\n"
            f"  Margin:   {(profit/revenue*100 if revenue else 0):.1f}%\n"
        )
        messagebox.showinfo("📊 Daily Summary", msg)

    # -------- HELPERS --------
    def _mini_win(self, title, w, h):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{w}x{h}")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        return win


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = POS(root)
    root.mainloop()