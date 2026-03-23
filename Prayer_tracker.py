# Prayer Tracker: Show User Names for Each Prayer and Time

# Step 1: Load existing data
prayer_data = {}
try:
    with open("prayer_times.txt", "r") as file:
        for line in file:
            user, prayers_str = line.strip().split(": ")
            prayers = {}
            for p in prayers_str.split(", "):
                name, time = p.split("-")
                prayers[name] = time
            prayer_data[user] = prayers
except FileNotFoundError:
    print("No existing data found. Starting fresh.")

# Step 2: Menu-driven app
while True:
    print("\n--- Prayer Tracker Menu ---")
    print("1. Add new user and prayer times")
    print("2. Show all users and prayer times")
    print("3. Check who prayed a specific prayer at a specific time")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ").strip()

    if choice == "1":
        # Add new user
        user_name = input("Enter user's name: ").strip()
        prayers = {}
        while True:
            prayer_name = input("Enter prayer name (Fajr, Zuhr, Asr, Maghrib, Isha) or 'done' to finish: ").strip()
            if prayer_name.lower() == "done":
                break
            prayer_time = input(f"Enter time for {prayer_name} (e.g., 12:00 PM): ").strip()
            prayers[prayer_name] = prayer_time
        prayer_data[user_name] = prayers
        print(f"Added {user_name} with prayers: {prayers}")

    elif choice == "2":
        # Show all users
        if not prayer_data:
            print("No data available.")
        else:
            print("\n--- All Users and Prayer Times ---")
            for user, prayers in prayer_data.items():
                prayer_list = [f"{name} at {time}" for name, time in prayers.items()]
                print(f"{user}: {', '.join(prayer_list)}")

    elif choice == "3":
        # Check users for a specific prayer at a specific time
        prayer_name = input("Enter the prayer name to check (e.g., Zuhr): ").strip()
        prayer_time = input("Enter the prayer time to check (e.g., 12:00 PM): ").strip()
        users_found = []
        for user, prayers in prayer_data.items():
            if prayer_name in prayers and prayers[prayer_name] == prayer_time:
                users_found.append(user)
        if users_found:
            print(f"Users who prayed {prayer_name} at {prayer_time}: {', '.join(users_found)}")
        else:
            print(f"No users found for {prayer_name} at {prayer_time}")

    elif choice == "4":
        # Save data to file and exit
        with open("prayer_times.txt", "w") as file:
            for user, prayers in prayer_data.items():
                prayers_str = ", ".join([f"{name}-{time}" for name, time in prayers.items()])
                file.write(f"{user}: {prayers_str}\n")
        print("Data saved. Exiting app.")
        break

    else:
        print("Invalid choice. Please enter 1-4.")