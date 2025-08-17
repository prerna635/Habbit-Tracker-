import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
import matplotlib.pyplot as plt


conn = sqlite3.connect("habit_tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER,
    date TEXT,
    status INTEGER,
    FOREIGN KEY(habit_id) REFERENCES habits(id)
)
""")

conn.commit()

def add_habit():
    habit = habit_entry.get()
    if habit.strip() == "":
        messagebox.showwarning("Input Error", "Please enter a habit.")
        return
    cursor.execute("INSERT INTO habits (name) VALUES (?)", (habit,))
    conn.commit()
    habit_entry.delete(0, tk.END)
    load_habits()

def mark_done(habit_id):
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT * FROM progress WHERE habit_id=? AND date=?", (habit_id, today))
    if cursor.fetchone():
        messagebox.showinfo("Already Marked", "You have already marked this habit today.")
    else:
        cursor.execute("INSERT INTO progress (habit_id, date, status) VALUES (?, ?, ?)",
                       (habit_id, today, 1))
        conn.commit()
        messagebox.showinfo("Success", "Habit marked as done!")

def load_habits():
    for widget in habits_frame.winfo_children():
        widget.destroy()
    cursor.execute("SELECT * FROM habits")
    habits = cursor.fetchall()
    for habit in habits:
        habit_id, habit_name = habit
        frame = tk.Frame(habits_frame)
        frame.pack(anchor="w", pady=2)
        tk.Label(frame, text=habit_name, font=("Arial", 12)).pack(side="left")
        tk.Button(frame, text="Mark Done ✅", command=lambda hid=habit_id: mark_done(hid)).pack(side="left", padx=10)

def show_progress():
    cursor.execute("""
        SELECT h.name, COUNT(p.status) 
        FROM habits h
        LEFT JOIN progress p ON h.id = p.habit_id
        GROUP BY h.id
    """)
    data = cursor.fetchall()
    
    if not data:
        messagebox.showwarning("No Data", "No habits tracked yet.")
        return
    
    habits = [row[0] for row in data]
    counts = [row[1] for row in data]
    
    plt.figure(figsize=(6,4))
    plt.bar(habits, counts, color="skyblue")
    plt.title("Habit Progress")
    plt.xlabel("Habits")
    plt.ylabel("Days Completed")
    plt.show()

root = tk.Tk()
root.title("Habit Tracker App ✅")
root.geometry("400x500")

tk.Label(root, text="Habit Tracker ✅", font=("Arial", 16, "bold")).pack(pady=10)

habit_entry = tk.Entry(root, font=("Arial", 12))
habit_entry.pack(pady=5)

tk.Button(root, text="Add Habit ➕", command=add_habit).pack(pady=5)

tk.Label(root, text="Your Habits:", font=("Arial", 14)).pack(pady=10)

habits_frame = tk.Frame(root)
habits_frame.pack()

tk.Button(root, text="Show Progress 📊", command=show_progress, bg="lightgreen").pack(pady=20)

load_habits()
root.mainloop()
