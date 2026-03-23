# final_prayer_tracker_auto_assign.py
import sqlite3

# -------------------------------
# Database setup
# -------------------------------
conn = sqlite3.connect("prayer_tracker.db")
cursor = conn.cursor()

# Drop old tables for clean start (optional)
cursor.execute("DROP TABLE IF EXISTS prayer_times")
cursor.execute("DROP TABLE IF EXISTS rooms")
cursor.execute("DROP TABLE IF EXISTS users")
conn.commit()

# Create Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# Create Rooms table
cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")

# Create Prayer Times table
cursor.execute("""
CREATE TABLE IF NOT EXISTS prayer_times (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    prayer_name TEXT NOT NULL,
    prayer_time TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(room_id) REFERENCES rooms(id)
)
""")
conn.commit()

# Sample rooms
rooms = [("Room A",), ("Room B",), ("Room C",)]
cursor.executemany("INSERT OR IGNORE INTO rooms (name) VALUES (?)", rooms)
conn.commit()

MAX_USERS_PER_ROOM = 30

# -------------------------------
# Helper Functions
# -------------------------------

def get_room_for_new_user():
    cursor.execute("""
        SELECT r.id, r.name, COUNT(u.id) as user_count
        FROM rooms r
        LEFT JOIN users u ON r.id = u.id
        GROUP BY r.id
        ORDER BY r.id
    """)
    rooms_list = cursor.fetchall()
    for room in rooms_list:
        if room[2] < MAX_USERS_PER_ROOM:
            return room[0], room[1]  # room_id, room_name
    return None, None  # all rooms full

def add_user_with_prayer():
    name = input("Enter user name: ").strip()
    if not name:
        print("Invalid name!\n")
        return

    # Add user
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    user_id = cursor.lastrowid

    # Assign room automatically
    cursor.execute("""
        SELECT r.id, r.name, COUNT(p.user_id) 
        FROM rooms r
        LEFT JOIN prayer_times p ON r.id = p.room_id
        GROUP BY r.id
        ORDER BY r.id
    """)
    rooms_list = cursor.fetchall()
    assigned_room_id = None
    assigned_room_name = None
    for room in rooms_list:
        if room[2] < MAX_USERS_PER_ROOM:
            assigned_room_id = room[0]
            assigned_room_name = room[1]
            break

    if assigned_room_id is None:
        print("All rooms are full! Cannot assign user.")
        return

    print(f"User '{name}' assigned to {assigned_room_name}.\n")

    # Add prayer for user
    prayer_name = input("Enter Prayer Name (Fajr/Zuhr/Asr/Maghrib/Isha): ").strip()
    prayer_time = input("Enter Prayer Time (e.g., 06:00 AM): ").strip()
    if prayer_name and prayer_time:
        cursor.execute("""
            INSERT INTO prayer_times (user_id, room_id, prayer_name, prayer_time)
            VALUES (?, ?, ?, ?)
        """, (user_id, assigned_room_id, prayer_name, prayer_time))
        conn.commit()
        print("Prayer recorded successfully!\n")
    else:
        print("Prayer not recorded due to invalid input.\n")

def list_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    if not users:
        print("No users found.\n")
    else:
        print("Users:")
        for u in users:
            print(f"ID: {u[0]}, Name: {u[1]}")
        print()

def list_rooms():
    cursor.execute("SELECT * FROM rooms")
    rooms_list = cursor.fetchall()
    print("Rooms:")
    for r in rooms_list:
        print(f"ID: {r[0]}, Name: {r[1]}")
    print()
    return rooms_list

def add_prayer_manual():
    list_users()
    user_id = input("Enter User ID for prayer: ").strip()
    list_rooms()
    room_id = input("Enter Room ID: ").strip()
    prayer_name = input("Enter Prayer Name (Fajr/Zuhr/Asr/Maghrib/Isha): ").strip()
    prayer_time = input("Enter Prayer Time (e.g., 06:00 AM): ").strip()
    if user_id and room_id and prayer_name and prayer_time:
        cursor.execute("""
            INSERT INTO prayer_times (user_id, room_id, prayer_name, prayer_time)
            VALUES (?, ?, ?, ?)
        """, (user_id, room_id, prayer_name, prayer_time))
        conn.commit()
        print("Prayer recorded successfully!\n")
    else:
        print("Invalid input!\n")

def view_prayers():
    cursor.execute("""
        SELECT u.id, u.name, r.name, p.prayer_name, p.prayer_time
        FROM prayer_times p
        JOIN users u ON p.user_id = u.id
        JOIN rooms r ON p.room_id = r.id
        ORDER BY u.id
    """)
    logs = cursor.fetchall()
    if not logs:
        print("No prayer logs found.\n")
    else:
        print("All Prayer Logs:")
        for l in logs:
            print(f"User ID: {l[0]}, Name: {l[1]}, Room: {l[2]}, Prayer: {l[3]}, Time: {l[4]}")
        print()

def stats_per_user():
    cursor.execute("""
        SELECT u.name, COUNT(p.id) 
        FROM users u
        LEFT JOIN prayer_times p ON u.id = p.user_id
        GROUP BY u.id
    """)
    stats = cursor.fetchall()
    print("Prayers per User:")
    for s in stats:
        print(f"User: {s[0]}, Total Prayers: {s[1]}")
    print()

def stats_per_room():
    cursor.execute("""
        SELECT r.name, COUNT(p.id) 
        FROM rooms r
        LEFT JOIN prayer_times p ON r.id = p.room_id
        GROUP BY r.id
    """)
    stats = cursor.fetchall()
    print("Prayers per Room:")
    for s in stats:
        print(f"Room: {s[0]}, Total Prayers: {s[1]}")
    print()

# -------------------------------
# CLI Menu
# -------------------------------
def main_menu():
    while True:
        print("=== CLI Prayer Tracker ===")
        print("1. Add New User (Auto Room Assign + Prayer)")
        print("2. Add Prayer Manually")
        print("3. View All Prayers")
        print("4. View Stats per User")
        print("5. View Stats per Room")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_user_with_prayer()
        elif choice == "2":
            add_prayer_manual()
        elif choice == "3":
            view_prayers()
        elif choice == "4":
            stats_per_user()
        elif choice == "5":
            stats_per_room()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice!\n")

# -------------------------------
# Run CLI
# -------------------------------
if __name__ == "__main__":
    main_menu()
    conn.close()
    print("Database connection closed. Bye!")