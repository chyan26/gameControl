from pynput.keyboard import Controller, Key
import time

# Initialize the keyboard controller
keyboard = Controller()

def press_key(key, duration):
    """
    Press and hold a key for a specified duration using a timing loop.
    """
    key_name = key.name if isinstance(key, Key) else key.upper()  # Handle Key objects and strings
    print(f"Pressing {key_name} for {duration} seconds...")
    start_time = time.perf_counter()
    keyboard.press(key)
    while time.perf_counter() - start_time < duration:
        pass  # Busy-wait loop
    keyboard.release(key)
    print(f"Released {key_name} after {duration} seconds.")


def execute_sequence():
    """
    Executes the key press sequence starting from 'w'.
    """
    press_key('w', 4.7)
    press_key('a', 0.9)
    press_key('w', 0.5)
    press_key('1', 0.5)
    time.sleep(4)

    press_key('t', 0.5)
    press_key('c', 0.5)
    press_key(Key.enter, 0.5)  # Use Key.enter for the Enter key
    #time.sleep(0.1)
    press_key(Key.enter, 0.1)  # Use Key.enter for the Enter key
    time.sleep(0.1)
    press_key(Key.enter, 0.1)  # Use Key.enter for the Enter key

# Wait for 5 seconds to give you time to activate the Chiaki-ng window
print("Starting in 3 seconds...")
time.sleep(3)

# Run the sequence in an infinite loop
sequence_count = 0
try:
    while True:
        sequence_count += 1
        print(f"Executing sequence {sequence_count}...")
        execute_sequence()

        # Wait for 6 seconds before the next sequence
        print("Waiting for 6 seconds...")
        time.sleep(6)
except KeyboardInterrupt:
    print("\nScript interrupted by user. Exiting...")

# Run the sequence in an infinite loopprint("Done!")
print("Done!")