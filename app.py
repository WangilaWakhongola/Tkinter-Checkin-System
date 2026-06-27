import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"attendees": [], "checkins": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


class CheckInApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Check-In System")
        self.root.geometry("700x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f4f8")

        self.data = load_data()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 5])
        style.configure("TButton", font=("Segoe UI", 10))

        self.build_checkin_tab()
        self.build_register_tab()
        self.build_records_tab()

    # ── Tab 1: Check-In ──────────────────────────────────────────────────────
    def build_checkin_tab(self):
        frame = tk.Frame(self.notebook, bg="#f0f4f8")
        self.notebook.add(frame, text="  Check-In  ")

        tk.Label(frame, text="Event Check-In", font=("Segoe UI", 16, "bold"),
                 bg="#f0f4f8", fg="#1a202c").pack(pady=(20, 5))
        tk.Label(frame, text="Enter your name or ID to check in",
                 font=("Segoe UI", 10), bg="#f0f4f8", fg="#718096").pack()

        tk.Label(frame, text="Name or ID:", font=("Segoe UI", 11),
                 bg="#f0f4f8", anchor="w").pack(padx=60, pady=(20, 3), fill="x")
        self.checkin_entry = tk.Entry(frame, font=("Segoe UI", 12), width=30,
                                      bd=1, relief="solid")
        self.checkin_entry.pack(ipady=6, padx=60)
        self.checkin_entry.bind("<Return>", lambda e: self.do_checkin())

        tk.Button(frame, text="Check In", font=("Segoe UI", 11, "bold"),
                  bg="#3b82f6", fg="white", relief="flat", cursor="hand2",
                  activebackground="#2563eb", width=18,
                  command=self.do_checkin).pack(pady=15)

        self.checkin_status = tk.Label(frame, text="", font=("Segoe UI", 11),
                                       bg="#f0f4f8")
        self.checkin_status.pack()

        # today's count
        self.today_label = tk.Label(frame, text="", font=("Segoe UI", 10),
                                    bg="#f0f4f8", fg="#718096")
        self.today_label.pack(pady=6)
        self.refresh_today_count()

    def do_checkin(self):
        raw = self.checkin_entry.get().strip()
        if not raw:
            self.checkin_status.config(text="Please enter a name or ID.", fg="#e53e3e")
            return

        # look up registered attendee
        match = next((a for a in self.data["attendees"]
                      if a["name"].lower() == raw.lower() or a["id"] == raw), None)

        if not match:
            self.checkin_status.config(
                text="Not found. Please register first.", fg="#e53e3e")
            return

        # prevent duplicate check-in today
        today = datetime.now().strftime("%Y-%m-%d")
        already = any(c["attendee_id"] == match["id"] and c["date"] == today
                      for c in self.data["checkins"])
        if already:
            self.checkin_status.config(
                text=f"⚠  {match['name']} already checked in today.", fg="#d97706")
            return

        record = {
            "attendee_id": match["id"],
            "name": match["name"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": today
        }
        self.data["checkins"].append(record)
        save_data(self.data)

        self.checkin_status.config(
            text=f"✓  Welcome, {match['name']}!", fg="#16a34a")
        self.checkin_entry.delete(0, tk.END)
        self.refresh_today_count()
        self.refresh_records_table()

    def refresh_today_count(self):
        today = datetime.now().strftime("%Y-%m-%d")
        count = sum(1 for c in self.data["checkins"] if c["date"] == today)
        self.today_label.config(text=f"Check-ins today: {count}")

    # ── Tab 2: Register ──────────────────────────────────────────────────────
    def build_register_tab(self):
        frame = tk.Frame(self.notebook, bg="#f0f4f8")
        self.notebook.add(frame, text="  Register  ")

        tk.Label(frame, text="Register Attendee", font=("Segoe UI", 16, "bold"),
                 bg="#f0f4f8", fg="#1a202c").pack(pady=(20, 5))

        for label, attr in [("Full Name:", "reg_name"), ("ID / Badge No.:", "reg_id"),
                             ("Email (optional):", "reg_email")]:
            tk.Label(frame, text=label, font=("Segoe UI", 11),
                     bg="#f0f4f8", anchor="w").pack(padx=60, pady=(12, 2), fill="x")
            entry = tk.Entry(frame, font=("Segoe UI", 12), width=30, bd=1, relief="solid")
            entry.pack(ipady=6, padx=60)
            setattr(self, attr, entry)

        tk.Button(frame, text="Register", font=("Segoe UI", 11, "bold"),
                  bg="#10b981", fg="white", relief="flat", cursor="hand2",
                  activebackground="#059669", width=18,
                  command=self.do_register).pack(pady=15)

        self.reg_status = tk.Label(frame, text="", font=("Segoe UI", 11), bg="#f0f4f8")
        self.reg_status.pack()

    def do_register(self):
        name = self.reg_name.get().strip()
        uid = self.reg_id.get().strip()
        email = self.reg_email.get().strip()

        if not name or not uid:
            self.reg_status.config(text="Name and ID are required.", fg="#e53e3e")
            return

        if any(a["id"] == uid for a in self.data["attendees"]):
            self.reg_status.config(text="ID already registered.", fg="#e53e3e")
            return

        self.data["attendees"].append({"name": name, "id": uid, "email": email})
        save_data(self.data)

        self.reg_status.config(text=f"✓  {name} registered successfully!", fg="#16a34a")
        for e in [self.reg_name, self.reg_id, self.reg_email]:
            e.delete(0, tk.END)

    # ── Tab 3: Records ───────────────────────────────────────────────────────
    def build_records_tab(self):
        frame = tk.Frame(self.notebook, bg="#f0f4f8")
        self.notebook.add(frame, text="  Records  ")

        tk.Label(frame, text="Check-In Records", font=("Segoe UI", 16, "bold"),
                 bg="#f0f4f8", fg="#1a202c").pack(pady=(15, 8))

        cols = ("Name", "ID", "Timestamp")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col != "ID" else 120)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        sb.pack(side="left", fill="y", pady=5)

        tk.Button(frame, text="Refresh", font=("Segoe UI", 10),
                  bg="#6366f1", fg="white", relief="flat", cursor="hand2",
                  command=self.refresh_records_table).pack(side="bottom", pady=8)

        self.refresh_records_table()

    def refresh_records_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in reversed(self.data["checkins"]):
            self.tree.insert("", tk.END, values=(c["name"], c["attendee_id"], c["timestamp"]))


if __name__ == "__main__":
    root = tk.Tk()
    app = CheckInApp(root)
    root.mainloop()
