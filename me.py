import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, datetime, tempfile, subprocess, sys

# ---------------- CONFIG ----------------
FILE = "bills.json"
HISTORY_FILE = "history.json"
TAX = 0.05
SERVICE = 0.10

RESTAURANT_NAME    = "SpiceByte Restaurant"
RESTAURANT_ADDRESS = "123 Food Street, Dhaka, Bangladesh"
RESTAURANT_PHONE   = "+880 1700-000000"
RESTAURANT_TAGLINE = "Thank you for dining with us!"

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
BG       = "#1a1a2e"
PANEL    = "#16213e"
CARD     = "#0f3460"
ACCENT   = "#e94560"
ACCENT2  = "#f5a623"
GREEN    = "#00b894"
TEAL     = "#00cec9"
TEXT     = "#eaeaea"
SUBTEXT  = "#a0a0b0"
WHITE    = "#ffffff"
DARK_BTN = "#0f3460"

# Receipt paper colors
R_BG     = "#fffef0"
R_TEXT   = "#1a1a1a"
R_BORDER = "#cccccc"
R_HEAD   = "#2d2d2d"
R_ACCENT = "#c0392b"
R_LINE   = "#888888"

# ---------------- FILE HELPERS ----------------
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
    return max([int(b["id"]) for b in bills], default=1000) + 1

def normalize_id(val):
    """Always compare IDs as integers, regardless of how they were saved."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return val

def repair_ids(bills, history):
    """
    Fix duplicate / string IDs across both lists.
    Assigns fresh sequential IDs to any duplicates,
    then saves both files so corruption does not persist.
    """
    seen = set()
    next_free = [1001]

    def fresh():
        while next_free[0] in seen:
            next_free[0] += 1
        v = next_free[0]
        seen.add(v)
        next_free[0] += 1
        return v

    # First pass: convert to int, flag duplicates
    for b in bills + history:
        try:
            b["id"] = int(b["id"])
        except Exception:
            b["id"] = 0
        if b["id"] in seen:
            b["id"] = 0          # duplicate, will be reassigned
        elif b["id"] > 0:
            seen.add(b["id"])

    # Second pass: assign new IDs to flagged entries
    changed = False
    for b in bills + history:
        if b["id"] == 0:
            b["id"] = fresh()
            changed = True

    if changed:
        save(FILE, bills)
        save(HISTORY_FILE, history)

    return bills, history


# ================================================================
#  RECEIPT TEXT BUILDER  (used for print & save-as-txt)
# ================================================================
def build_receipt_text(bill):
    W   = 44
    now = bill.get("date", "")[:19]
    paid_at = bill.get("paid_at", "")[:19]

    def center(s):  return s.center(W)
    def rule(c="─"): return c * W
    def thick():     return "═" * W

    lines = [
        thick(),
        center(RESTAURANT_NAME),
        center(RESTAURANT_ADDRESS),
        center(f"Tel: {RESTAURANT_PHONE}"),
        thick(),
        f"  Bill No  : #{bill['id']}",
        f"  Customer : {bill.get('customer','Walk-in')}",
        f"  Table    : {bill.get('table','—')}",
        f"  Date     : {now}",
    ]
    if paid_at:
        lines.append(f"  Paid At  : {paid_at}")
    lines.append(f"  Status   : {bill.get('status','—').upper()}")
    lines.append(rule())
    lines.append(f"  {'ITEM':<22} {'QTY':>4}  {'PRICE':>6}  {'TOTAL':>6}")
    lines.append(rule())

    for item in bill.get("items", []):
        n = item["name"][:22]
        q = item["qty"]
        p = item.get("price", 0)
        t = item["total"]
        lines.append(f"  {n:<22} {q:>4}  {p:>6}  {t:>6,}")

    lines += [
        rule(),
        f"  {'Subtotal':<32} {bill.get('subtotal',0):>8,.2f}",
        f"  {'Tax (5%)':<32} {bill.get('tax',0):>8,.2f}",
        f"  {'Service Charge (10%)':<32} {bill.get('service',0):>8,.2f}",
        thick(),
        f"  {'GRAND TOTAL (BDT)':<32} {bill['total']:>8,.2f}",
        thick(),
        "",
        center(RESTAURANT_TAGLINE),
        center("Please come again  ★"),
        "",
        f"{'Powered by SpiceByte POS':>{W}}",
        thick(),
    ]
    return "\n".join(lines)


# ================================================================
#  RECEIPT WINDOW  — on-screen paper receipt
# ================================================================
class ReceiptWindow:

    def __init__(self, parent, bill):
        self.bill   = bill
        self.parent = parent
        self.win    = tk.Toplevel(parent)
        self.win.title(f"🧾 Receipt — Bill #{bill['id']}")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)
        self.win.grab_set()
        self._build()

    # ---- build the window ----
    def _build(self):
        # Top bar
        bar = tk.Frame(self.win, bg=ACCENT, height=46)
        bar.pack(fill="x")
        tk.Label(bar, text="🧾  CUSTOMER RECEIPT",
                 font=("Georgia", 14, "bold"),
                 bg=ACCENT, fg=WHITE).pack(side="left", padx=16, pady=8)
        status = self.bill.get("status", "unpaid").upper()
        sc = GREEN if status == "PAID" else "#e67e22"
        tk.Label(bar, text=f"Bill #{self.bill['id']}  ●  {status}",
                 font=("Consolas", 10, "bold"),
                 bg=ACCENT, fg=sc).pack(side="right", padx=16)

        # Outer padding frame
        outer = tk.Frame(self.win, bg="#b0b0a0", padx=3, pady=3)
        outer.pack(padx=24, pady=14)

        # Paper
        paper = tk.Frame(outer, bg=R_BG)
        paper.pack()

        # torn-edge top
        tk.Frame(paper, bg="#e6e6d2", height=5).pack(fill="x")

        body = tk.Frame(paper, bg=R_BG, padx=26, pady=18)
        body.pack()

        W = 38

        # --- Restaurant header ---
        tk.Label(body, text=RESTAURANT_NAME,
                 bg=R_BG, fg=R_ACCENT,
                 font=("Georgia", 15, "bold"),
                 width=W, anchor="center").pack(pady=(2, 0))
        tk.Label(body, text=RESTAURANT_ADDRESS,
                 bg=R_BG, fg=R_LINE,
                 font=("Courier", 9),
                 width=W, anchor="center").pack()
        tk.Label(body, text=f"Tel: {RESTAURANT_PHONE}",
                 bg=R_BG, fg=R_LINE,
                 font=("Courier", 9),
                 width=W, anchor="center").pack(pady=(0, 8))

        self._thick(body, W)

        # --- Bill info rows ---
        now     = self.bill.get("date", "")[:19]
        paid_at = self.bill.get("paid_at", "")[:19] if self.bill.get("paid_at") else ""

        for lbl, val in [
            ("Bill No",   f"#{self.bill['id']}"),
            ("Customer",  self.bill.get("customer", "Walk-in")),
            ("Table",     self.bill.get("table", "—")),
            ("Date",      now),
        ]:
            self._info_row(body, lbl, val)

        if paid_at:
            self._info_row(body, "Paid At", paid_at, val_color=GREEN)

        sc2 = GREEN if status == "PAID" else "#e67e22"
        self._info_row(body, "Status", status, val_color=sc2)

        # --- Items table ---
        tk.Frame(body, bg=R_BG, height=8).pack()
        self._divider(body, W)

        hf = tk.Frame(body, bg="#f0eedc")
        hf.pack(fill="x")
        for txt, w, anchor in [
            ("  ITEM", 23, "w"), ("QTY", 4, "e"),
            ("  PRICE", 7, "e"), ("  TOTAL", 8, "e")
        ]:
            tk.Label(hf, text=txt, bg="#f0eedc", fg=R_HEAD,
                     font=("Courier", 9, "bold"),
                     width=w, anchor=anchor).pack(side="left")

        self._divider(body, W)

        # alternating row bg
        colors = [R_BG, "#f7f6e8"]
        for idx, item in enumerate(self.bill.get("items", [])):
            rbg = colors[idx % 2]
            rf  = tk.Frame(body, bg=rbg)
            rf.pack(fill="x")
            name  = item["name"][:22]
            qty   = item["qty"]
            price = item.get("price", 0)
            total = item["total"]
            tk.Label(rf, text=f"  {name}", bg=rbg, fg=R_TEXT,
                     font=("Courier", 10), width=25, anchor="w").pack(side="left")
            tk.Label(rf, text=f"{qty}", bg=rbg, fg=R_TEXT,
                     font=("Courier", 10), width=4, anchor="e").pack(side="left")
            tk.Label(rf, text=f"{price:,}", bg=rbg, fg=R_LINE,
                     font=("Courier", 10), width=7, anchor="e").pack(side="left")
            tk.Label(rf, text=f"{total:,}", bg=rbg, fg=R_HEAD,
                     font=("Courier", 10, "bold"), width=8, anchor="e").pack(side="left")

        # --- Totals ---
        self._divider(body, W)

        subtotal = self.bill.get("subtotal", 0)
        tax_v    = self.bill.get("tax", 0)
        svc_v    = self.bill.get("service", 0)
        total_v  = self.bill.get("total", 0)

        for lbl, val, bold in [
            ("Subtotal",             subtotal, False),
            ("Tax (5%)",             tax_v,    False),
            ("Service Charge (10%)", svc_v,    False),
        ]:
            tf = tk.Frame(body, bg=R_BG)
            tf.pack(fill="x")
            tk.Label(tf, text=f"  {lbl}", bg=R_BG, fg=R_LINE,
                     font=("Courier", 9), width=30, anchor="w").pack(side="left")
            tk.Label(tf, text=f"Tk {val:,.2f}", bg=R_BG, fg=R_TEXT,
                     font=("Courier", 9 if not bold else 10),
                     width=12, anchor="e").pack(side="left")

        self._thick(body, W)

        # Grand total — large
        gf = tk.Frame(body, bg="#fff8e0")
        gf.pack(fill="x", pady=4)
        tk.Label(gf, text="  GRAND TOTAL", bg="#fff8e0", fg=R_ACCENT,
                 font=("Georgia", 12, "bold"), width=22, anchor="w").pack(side="left")
        tk.Label(gf, text=f"Tk {total_v:,.2f}", bg="#fff8e0", fg=R_ACCENT,
                 font=("Georgia", 12, "bold"), width=16, anchor="e").pack(side="left")

        self._thick(body, W)

        # Footer
        tk.Frame(body, bg=R_BG, height=8).pack()
        tk.Label(body, text=RESTAURANT_TAGLINE,
                 bg=R_BG, fg=R_ACCENT,
                 font=("Georgia", 10, "italic"),
                 width=W, anchor="center").pack()
        tk.Label(body, text="★  Please Come Again  ★",
                 bg=R_BG, fg=R_LINE,
                 font=("Courier", 9),
                 width=W, anchor="center").pack(pady=(2, 10))

        # torn-edge bottom
        tk.Frame(paper, bg="#e6e6d2", height=5).pack(fill="x")

        # --- Action buttons ---
        btn_row = tk.Frame(self.win, bg=BG)
        btn_row.pack(pady=14)

        for txt, bg, cmd in [
            ("🖨️  Print Receipt", ACCENT,    self.do_print),
            ("💾  Save as TXT",   TEAL,      self.save_txt),
            ("❌  Close",         "#636e72", self.win.destroy),
        ]:
            tk.Button(btn_row, text=txt, bg=bg, fg=WHITE,
                      font=("Consolas", 11, "bold"),
                      relief="flat", cursor="hand2",
                      padx=18, pady=8,
                      command=cmd).pack(side="left", padx=8)

    # ---- small helpers ----
    def _divider(self, parent, W):
        tk.Label(parent, text="─" * W,
                 bg=R_BG, fg=R_LINE,
                 font=("Courier", 8)).pack(anchor="w")

    def _thick(self, parent, W):
        tk.Label(parent, text="═" * W,
                 bg=R_BG, fg=R_HEAD,
                 font=("Courier", 8)).pack(anchor="w")

    def _info_row(self, parent, label, value, val_color=None):
        rf = tk.Frame(parent, bg=R_BG)
        rf.pack(anchor="w", fill="x")
        tk.Label(rf, text=f"  {label:<12}:",
                 bg=R_BG, fg=R_LINE,
                 font=("Courier", 9)).pack(side="left")
        tk.Label(rf, text=f" {value}",
                 bg=R_BG, fg=val_color or R_TEXT,
                 font=("Courier", 10, "bold")).pack(side="left")

    # ---- Print ----
    def do_print(self):
        text = build_receipt_text(self.bill)
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8")
            tmp.write(text)
            tmp.close()

            if sys.platform.startswith("win"):
                os.startfile(tmp.name, "print")
                messagebox.showinfo(
                    "🖨️ Printing",
                    "Receipt sent to your default printer.\n"
                    "Make sure a printer is connected.",
                    parent=self.win)
            else:
                result = subprocess.run(["lpr", tmp.name], capture_output=True)
                if result.returncode == 0:
                    messagebox.showinfo("🖨️ Printing",
                        "Receipt sent to printer.", parent=self.win)
                else:
                    raise RuntimeError(result.stderr.decode())
        except Exception as ex:
            messagebox.showerror(
                "Print Error",
                f"Could not send to printer:\n{ex}\n\n"
                "Tip: Use '💾 Save as TXT' and print from any text editor.",
                parent=self.win)

    # ---- Save TXT ----
    def save_txt(self):
        default = f"Receipt_Bill_{self.bill['id']}.txt"
        path = filedialog.asksaveasfilename(
            parent=self.win,
            title="Save Receipt as Text File",
            defaultextension=".txt",
            initialfile=default,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(build_receipt_text(self.bill))
            messagebox.showinfo("✅ Saved",
                f"Receipt saved:\n{path}", parent=self.win)
        except Exception as ex:
            messagebox.showerror("Save Error", str(ex), parent=self.win)


# ================================================================
#  MAIN POS APP
# ================================================================
class POS:
    def __init__(self, root):
        self.root = root
        self.root.title("🍽️  SpiceByte Restaurant POS")
        self.root.geometry("1350x780")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.bills   = load(FILE)
        self.history = load(HISTORY_FILE)
        # Repair any duplicate or string IDs from older versions
        self.bills, self.history = repair_ids(self.bills, self.history)
        self.cart    = []

        self._apply_styles()
        self.build_ui()

    # -------- Styles --------
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

    # -------- Build UI --------
    def build_ui(self):
        # Header
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

        # ---------- LEFT panel ----------
        left = tk.Frame(main, bg=PANEL)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))

        tk.Label(left, text="📋  MENU", font=("Georgia", 14, "bold"),
                 bg=PANEL, fg=ACCENT2).pack(pady=(8, 4))

        # Search
        sf = tk.Frame(left, bg=PANEL)
        sf.pack(fill="x", padx=8, pady=2)
        tk.Label(sf, text="🔍", bg=PANEL, fg=SUBTEXT).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_menu)
        tk.Entry(sf, textvariable=self.search_var,
                 bg=CARD, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=("Consolas", 10)
                 ).pack(side="left", fill="x", expand=True, padx=4)

        # Menu tree
        tf = tk.Frame(left, bg=PANEL)
        tf.pack(fill="both", expand=True, padx=8, pady=4)
        self.menu_tree = ttk.Treeview(tf)
        self.menu_tree["columns"] = ("Price",)
        self.menu_tree.column("#0",    width=260)
        self.menu_tree.column("Price", width=80, anchor="e")
        self.menu_tree.heading("#0",    text="Item")
        self.menu_tree.heading("Price", text="Price ৳")
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.menu_tree.yview)
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

        # ---------- RIGHT panel ----------
        right = tk.Frame(main, bg=PANEL, width=400)
        right.pack(side="right", fill="both", padx=(6, 0))
        right.pack_propagate(False)

        tk.Label(right, text="🛒  ORDER", font=("Georgia", 14, "bold"),
                 bg=PANEL, fg=TEAL).pack(pady=(8, 4))

        # Customer / Table
        inf = tk.Frame(right, bg=PANEL)
        inf.pack(fill="x", padx=8, pady=2)
        self.customer = tk.Entry(inf, bg=CARD, fg=TEXT,
                                  insertbackground=TEXT, relief="flat",
                                  font=("Consolas", 10))
        self.customer.insert(0, "👤 Customer Name")
        self.customer.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=4)
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
        self.sub_lbl = tk.Label(totals, text="Subtotal:       ৳0.00",
                                 bg=DARK_BTN, fg=SUBTEXT, font=("Consolas", 10))
        self.sub_lbl.pack(anchor="w", padx=10, pady=2)
        self.tax_lbl = tk.Label(totals, text="Tax (5%):       ৳0.00",
                                 bg=DARK_BTN, fg=SUBTEXT, font=("Consolas", 10))
        self.tax_lbl.pack(anchor="w", padx=10)
        self.svc_lbl = tk.Label(totals, text="Service (10%):  ৳0.00",
                                 bg=DARK_BTN, fg=SUBTEXT, font=("Consolas", 10))
        self.svc_lbl.pack(anchor="w", padx=10, pady=2)
        self.total_lbl = tk.Label(totals, text="TOTAL:  ৳0.00",
                                   bg=DARK_BTN, fg=ACCENT2,
                                   font=("Georgia", 14, "bold"))
        self.total_lbl.pack(anchor="w", padx=10, pady=6)

        # Buttons
        btns = [
            ("💳  Checkout",         ACCENT,    self.checkout),
            ("🖨️   Print Receipt",   "#8e44ad",  self.print_receipt_by_id),
            ("📄  View Bills",        CARD,      self.view_bills),
            ("📜  View History",      GREEN,     self.view_history),
            ("🔍  Search Bill",       TEAL,      self.search_bill),
            ("✅  Mark Paid",         "#5f27cd",  self.mark_paid),
            ("🗑️   Delete Bill",      "#636e72",  self.delete_bill),
            ("📊  Daily Summary",     ACCENT2,   self.summary),
            ("🗑️   Clear Cart",       "#d63031",  self.clear_cart),
        ]
        for txt, color, cmd in btns:
            tk.Button(right, text=txt, bg=color, fg=WHITE,
                      font=("Consolas", 10, "bold"), relief="flat",
                      cursor="hand2", command=cmd,
                      anchor="w", padx=12, pady=5
                      ).pack(fill="x", padx=8, pady=2)

    # -------- Menu --------
    def _populate_menu(self, filter_text=""):
        for i in self.menu_tree.get_children():
            self.menu_tree.delete(i)
        ft = filter_text.lower()
        for cat, items in MENU.items():
            parent = None
            for code, (name, price, _) in items.items():
                if ft in name.lower() or ft in code.lower() or ft == "":
                    if parent is None:
                        parent = self.menu_tree.insert("", "end", text=cat, tags=("cat",))
                        self.menu_tree.tag_configure(
                            "cat", foreground=ACCENT2, font=("Georgia", 10, "bold"))
                    self.menu_tree.insert(parent, "end",
                                          text=f"  {code}  {name}",
                                          values=(f"৳{price}",))

    def _filter_menu(self, *args):
        self._populate_menu(self.search_var.get())

    def _tick(self):
        self.clock_lbl.config(
            text=datetime.datetime.now().strftime("%a %d %b %Y   %H:%M:%S"))
        self.root.after(1000, self._tick)

    # -------- Cart --------
    def add_item(self):
        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showerror("Error", "Please select a menu item first.")
            return
        parts = self.menu_tree.item(sel[0])["text"].strip().split()
        if not parts or parts[0] not in [c for cat in MENU.values() for c in cat]:
            messagebox.showerror("Error", "Please select an item, not a category.")
            return
        code = parts[0]
        try:
            qty = int(self.qty.get())
            assert qty >= 1
        except:
            messagebox.showerror("Error", "Enter a valid quantity.")
            return

        for cat in MENU.values():
            if code in cat:
                name, price, cost = cat[code]
                for c in self.cart:
                    if c["name"] == name:
                        c["qty"]   += qty
                        c["total"] += price * qty
                        c["cost"]  += cost  * qty
                        self._refresh_cart_display()
                        self.update_total()
                        return
                self.cart.append({"code": code, "name": name, "qty": qty,
                                   "price": price, "total": price*qty, "cost": cost*qty})
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
        if messagebox.askyesno("Clear Cart", "Remove all items?"):
            self.cart = []
            self.cart_box.delete(0, tk.END)
            self.update_total()

    def _refresh_cart_display(self):
        self.cart_box.delete(0, tk.END)
        for c in self.cart:
            self.cart_box.insert(
                tk.END, f"  {c['name']:25s} x{c['qty']:2d}  ৳{c['total']:,.0f}")

    def update_total(self):
        sub = sum(i["total"] for i in self.cart)
        tax = sub * TAX
        svc = sub * SERVICE
        tot = sub + tax + svc
        self.sub_lbl.config(text=f"Subtotal:       ৳{sub:,.2f}")
        self.tax_lbl.config(text=f"Tax (5%):       ৳{tax:,.2f}")
        self.svc_lbl.config(text=f"Service (10%):  ৳{svc:,.2f}")
        self.total_lbl.config(text=f"TOTAL:  ৳{tot:,.2f}")

    # -------- Checkout --------
    def checkout(self):
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty.")
            return
        cname = self.customer.get().strip()
        tname = self.table.get().strip()
        if cname in ("", "👤 Customer Name"):  cname = "Walk-in"
        if tname in ("", "🪑 Table"):           tname = "—"

        sub  = sum(i["total"] for i in self.cart)
        cost = sum(i["cost"]  for i in self.cart)
        tax  = sub * TAX
        svc  = sub * SERVICE
        tot  = sub + tax + svc

        bill = {
            "id":       next_id(self.bills + self.history),
            "date":     str(datetime.datetime.now()),
            "customer": cname,
            "table":    tname,
            "items":    [{"name": i["name"], "qty": i["qty"], "price": i["price"],
                          "total": i["total"], "cost": i["cost"]} for i in self.cart],
            "subtotal": round(sub,  2),
            "tax":      round(tax,  2),
            "service":  round(svc,  2),
            "cost":     round(cost, 2),
            "profit":   round(sub - cost, 2),
            "total":    round(tot,  2),
            "status":   "unpaid"
        }

        self.bills.append(bill)
        save(FILE, self.bills)

        self.cart = []
        self.cart_box.delete(0, tk.END)
        self.update_total()
        self.customer.delete(0, tk.END);  self.customer.insert(0, "👤 Customer Name")
        self.table.delete(0, tk.END);     self.table.insert(0, "🪑 Table")

        # Ask to print
        ans = messagebox.askyesno(
            f"✅ Bill #{bill['id']} Saved",
            f"Bill #{bill['id']} created!\n\n"
            f"Customer : {cname}\nTable    : {tname}\n"
            f"Total    : ৳{round(tot,2):,.2f}\n\n"
            "🖨️  Open receipt to print now?"
        )
        if ans:
            ReceiptWindow(self.root, bill)

    # -------- Print Receipt (by ID) --------
    def print_receipt_by_id(self):
        win = self._mini_win("🖨️ Print Receipt", 380, 185)
        tk.Label(win, text="Enter Bill ID to open receipt:",
                 bg=BG, fg=TEXT, font=("Consolas", 11)).pack(pady=14)
        e = tk.Entry(win, bg=CARD, fg=ACCENT2, insertbackground=TEXT,
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
                    win.destroy()
                    ReceiptWindow(self.root, b)
                    return
            messagebox.showerror("Not Found", f"Bill #{bid} not found.", parent=win)

        tk.Button(win, text="Open Receipt", bg="#8e44ad", fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  command=go).pack(pady=10)

    # -------- Mark Paid --------
    def mark_paid(self):
        win = self._mini_win("✅ Mark Bill as Paid", 360, 185)
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
                messagebox.showerror("Error", "Invalid ID.", parent=win)
                return

            # Check active bills first
            for b in self.bills:
                if int(b["id"]) == bid:
                    b["id"]      = bid
                    b["status"]  = "paid"
                    b["paid_at"] = str(datetime.datetime.now())
                    self.history.append(b)
                    self.bills.remove(b)
                    save(FILE, self.bills)
                    save(HISTORY_FILE, self.history)
                    win.destroy()
                    messagebox.showinfo("✅ Paid",
                        f"Bill #{bid} marked as paid!\nMoved to history.",
                        parent=self.root)
                    return

            # Check if already paid (in history)
            fresh_history = load(HISTORY_FILE)
            for b in fresh_history:
                if int(b["id"]) == bid:
                    messagebox.showinfo("Already Paid",
                        f"Bill #{bid} is already marked as PAID.\n"
                        f"Customer : {b.get('customer','—')}\n"
                        f"Paid At  : {b.get('paid_at','—')[:19]}\n"
                        f"Total    : {b.get('total',0):,.2f}",
                        parent=win)
                    return

            # Not found anywhere
            messagebox.showerror("Not Found",
                f"Bill #{bid} does not exist in active bills or history.",
                parent=win)

        tk.Button(win, text="Mark Paid", bg=GREEN, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  command=go).pack(pady=8)

    # -------- View Bills --------
    def view_bills(self):
        win = tk.Toplevel(self.root)
        win.title("📄 Active Bills")
        win.geometry("740x440")
        win.configure(bg=BG)
        tk.Label(win, text="📄 ACTIVE BILLS", font=("Georgia", 14, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=10)

        fr = tk.Frame(win, bg=BG)
        fr.pack(fill="both", expand=True, padx=10, pady=5)
        tree = ttk.Treeview(fr)
        tree["columns"] = ("Customer","Table","Total","Status","Date")
        for col, w, anc in [("#0",70,"center"),("Customer",130,"w"),
                             ("Table",70,"center"),("Total",100,"e"),
                             ("Status",80,"center"),("Date",170,"w")]:
            tree.column(col, width=w, anchor=anc)
        for col, hd in [("#0","ID"),("Customer","Customer"),("Table","Table"),
                        ("Total","Total ৳"),("Status","Status"),("Date","Date")]:
            tree.heading(col, text=hd)
        sb = ttk.Scrollbar(fr, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for b in self.bills:
            tree.insert("", "end", text=b["id"],
                        values=(b.get("customer","—"), b.get("table","—"),
                                f"৳{b['total']:,.2f}", b["status"].upper(),
                                b.get("date","")[:19]))

        def on_dbl(event):
            sel = tree.selection()
            if not sel: return
            bid = tree.item(sel[0])["text"]
            for b in self.bills:
                if int(b["id"]) == int(bid):
                    ReceiptWindow(win, b); return

        tree.bind("<Double-1>", on_dbl)
        tk.Label(win, text=f"Total active bills: {len(self.bills)}   |   Double-click to view/print receipt",
                 bg=BG, fg=SUBTEXT, font=("Consolas", 9)).pack(pady=4)

    # -------- View History --------
    def view_history(self):
        self.history = load(HISTORY_FILE)
        win = tk.Toplevel(self.root)
        win.title("📜 Payment History")
        win.geometry("860x500")
        win.configure(bg=BG)
        tk.Label(win, text="📜 PAYMENT HISTORY", font=("Georgia", 14, "bold"),
                 bg=BG, fg=GREEN).pack(pady=10)

        total_rev    = sum(b.get("total", 0)  for b in self.history)
        total_profit = sum(b.get("profit", 0) for b in self.history)
        bar = tk.Frame(win, bg=DARK_BTN)
        bar.pack(fill="x", padx=10, pady=4)
        tk.Label(bar, text=f"  Total Bills: {len(self.history)}",
                 bg=DARK_BTN, fg=TEXT, font=("Consolas", 10)).pack(side="left", padx=10)
        tk.Label(bar, text=f"Revenue: ৳{total_rev:,.2f}",
                 bg=DARK_BTN, fg=ACCENT2, font=("Consolas", 10, "bold")).pack(side="left", padx=10)
        tk.Label(bar, text=f"Profit: ৳{total_profit:,.2f}",
                 bg=DARK_BTN, fg=GREEN, font=("Consolas", 10, "bold")).pack(side="left", padx=10)

        fr = tk.Frame(win, bg=BG)
        fr.pack(fill="both", expand=True, padx=10, pady=5)
        tree = ttk.Treeview(fr, style="History.Treeview")
        tree["columns"] = ("Customer","Table","Subtotal","Total","Profit","Paid At")
        for col, w, anc in [("#0",65,"center"),("Customer",120,"w"),
                             ("Table",60,"center"),("Subtotal",90,"e"),
                             ("Total",100,"e"),("Profit",90,"e"),("Paid At",170,"w")]:
            tree.column(col, width=w, anchor=anc)
        for col, hd in [("#0","ID"),("Customer","Customer"),("Table","Table"),
                        ("Subtotal","Subtotal ৳"),("Total","Total ৳"),
                        ("Profit","Profit ৳"),("Paid At","Paid At")]:
            tree.heading(col, text=hd)
        sb = ttk.Scrollbar(fr, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for b in reversed(self.history):
            paid_at = b.get("paid_at", b.get("date","—"))[:19]
            tree.insert("", "end", text=b["id"],
                        values=(b.get("customer","—"), b.get("table","—"),
                                f"৳{b.get('subtotal',0):,.2f}",
                                f"৳{b['total']:,.2f}",
                                f"৳{b.get('profit',0):,.2f}",
                                paid_at))

        def on_dbl(event):
            sel = tree.selection()
            if not sel: return
            bid = tree.item(sel[0])["text"]
            for b in self.history:
                if int(b["id"]) == int(bid):
                    ReceiptWindow(win, b); return

        tree.bind("<Double-1>", on_dbl)
        tk.Label(win, text="Double-click a row to view & print receipt",
                 bg=BG, fg=SUBTEXT, font=("Consolas", 9)).pack(pady=3)

    # -------- Search Bill --------
    def search_bill(self):
        win = self._mini_win("🔍 Search Bill", 380, 185)
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
                if int(b["id"]) == bid:
                    win.destroy()
                    ReceiptWindow(self.root, b)
                    return
            messagebox.showerror("Not Found", f"Bill #{bid} not found.", parent=win)

        tk.Button(win, text="Search & Open Receipt", bg=TEAL, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  command=go).pack(pady=8)

    # -------- Delete Bill --------
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
                messagebox.showerror("Error", "Invalid Bill ID.", parent=win)
                return
            if not messagebox.askyesno("Confirm", f"Delete Bill #{bid}?", parent=win):
                return
            before = len(self.bills)
            self.bills = [b for b in self.bills if int(b["id"]) != bid]
            if len(self.bills) < before:
                save(FILE, self.bills)
                messagebox.showinfo("Deleted", f"Bill #{bid} deleted.", parent=win)
                win.destroy()
            else:
                messagebox.showerror("Error", f"Bill #{bid} not found in active bills.", parent=win)

        tk.Button(win, text="Delete", bg=ACCENT, fg=WHITE,
                  font=("Consolas", 10, "bold"), relief="flat",
                  command=go).pack(pady=8)

    # -------- Daily Summary --------
    def summary(self):
        self.history = load(HISTORY_FILE)
        today = datetime.date.today().strftime("%Y-%m-%d")
        tb = [b for b in self.history if b.get("date","").startswith(today)]
        rev    = sum(b.get("total",0)  for b in tb)
        profit = sum(b.get("profit",0) for b in tb)
        cost   = sum(b.get("cost",0)   for b in tb)
        items  = sum(sum(i["qty"] for i in b.get("items",[])) for b in tb)
        messagebox.showinfo("📊 Daily Summary",
            f"📅 Daily Summary — {today}\n{'─'*34}\n"
            f"  Bills Closed:   {len(tb)}\n"
            f"  Items Sold:     {items}\n{'─'*34}\n"
            f"  Revenue:  ৳{rev:>10,.2f}\n"
            f"  Cost:     ৳{cost:>10,.2f}\n"
            f"  Profit:   ৳{profit:>10,.2f}\n{'─'*34}\n"
            f"  Margin:   {(profit/rev*100 if rev else 0):.1f}%\n")

    # -------- Helper --------
    def _mini_win(self, title, w, h):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{w}x{h}")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()
        return win


# ================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app  = POS(root)
    root.mainloop()