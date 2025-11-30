print("Select mode:")
print("1. Hand Tracking")
print("2. Hand Gesture Control (Media Player)")

choice = input("Enter 1 or 2: ").strip()

if choice == "1":
    print("Starting Hand Tracking...")

elif choice == "2":
    print("Starting Hand Gesture Control...")

else:
    print("Invalid choice. Exiting...")
