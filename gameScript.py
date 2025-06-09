import time
start_import = time.time()

# --- your imports ---
from pynput.keyboard import Controller, Key
import Quartz
import Quartz.CoreGraphics as CG
try:
    from CoreServices import kUTTypePNG
except ImportError:
    import objc
    kUTTypePNG = objc.lookUpClass("NSString").stringWithString_("public.png")
from PIL import Image, ImageChops, ImageStat
import pytesseract
import re
import os
import time
os.environ["TESSDATA_PREFIX"] = "/opt/local/share/tessdata"
import glob
import logging
# --- end of imports ---

print(f"Imports took {time.time() - start_import:.3f} seconds")

# Configure logging
LOG_FILE = "extracted_numbers.log"
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',  # Overwrite the log file each time the program starts
    format='%(asctime)s - %(message)s',
    level=logging.INFO
)

# Initialize the keyboard controller
keyboard = Controller()

def get_chiaki_window_id():
    window_list = CG.CGWindowListCopyWindowInfo(CG.kCGWindowListOptionOnScreenOnly, CG.kCGNullWindowID)
    for window in window_list:
        owner = window.get('kCGWindowOwnerName', '')
        name = window.get('kCGWindowName', '')
        if 'chiaki' in owner.lower() or 'chiaki' in name.lower():
            return window['kCGWindowNumber']
    return None

def capture_window(window_id, filename):
    image = CG.CGWindowListCreateImage(
        CG.CGRectNull,
        CG.kCGWindowListOptionIncludingWindow,
        window_id,
        CG.kCGWindowImageDefault)
    if image is None:
        print("Failed to capture window.")
        return
    dest = Quartz.CGImageDestinationCreateWithURL(
        Quartz.CFURLCreateWithFileSystemPath(None, filename, Quartz.kCFURLPOSIXPathStyle, False),
        kUTTypePNG, 1, None)
    Quartz.CGImageDestinationAddImage(dest, image, None)
    Quartz.CGImageDestinationFinalize(dest)
    print(f"Screenshot saved to {filename}")

def press_key(key, duration):
    """
    Press and hold a key for a specified duration using a timing loop.
    """
    key_name = key.name if isinstance(key, Key) else key.upper()  # Handle Key objects and strings
    print(f"Pressing {key_name} for {duration} seconds...")
    start_time = time.perf_counter()
    keyboard.press(key)
    try:
        while time.perf_counter() - start_time < duration:
            time.sleep(0.01)  # Reduce CPU usage
    finally:
        keyboard.release(key)
        #print(f"Released {key_name} after {duration} seconds.")

def goback_to_start():
    """
    This script is used to return to the start position in the game.
    """
    press_key('t', 0.5)
    press_key('c', 0.5)
    press_key(Key.up, 0.1)
    time.sleep(0.2)    
    press_key(Key.up, 0.1)
    time.sleep(0.2) 
    press_key(Key.up, 0.1)
    time.sleep(0.2) 
    press_key(Key.up, 0.1)
    time.sleep(0.2) 
    press_key(Key.enter, 0.5)
    time.sleep(0.2)
    press_key(Key.enter, 0.2)
    time.sleep(0.2)
    press_key(Key.enter, 0.2)
    print("Waiting for 6 seconds...")
    time.sleep(6)

def execute_sequence():
    """
    Executes the key press sequence starting from 'w'.
    """
    press_key('w', 4.7)
    press_key('a', 1.0)
    press_key('w', 0.5)
    press_key('1', 0.5)
    time.sleep(4)

    press_key('t', 0.5)
    press_key('c', 0.5)
    press_key(Key.enter, 0.5)
    time.sleep(0.2)
    press_key(Key.enter, 0.2)
    time.sleep(0.2)
    press_key(Key.enter, 0.2)
    print("Waiting for 6 seconds...")
    time.sleep(6)
    
def images_are_equal(img1_path, img2_path, tolerance=10):
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        return True  # If one doesn't exist, treat as equal for first run
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")
    diff = ImageChops.difference(img1, img2)
    stat = ImageStat.Stat(diff)
    rms = sum([v**2 for v in stat.mean]) ** 0.5
    print(f"RMS difference: {rms}")
    return rms < tolerance  # True if images are similar enough

def extract_number_from_image(image_path):
    """
    Extracts a number from the lower-right corner of the given image using OCR.
    """
    img = Image.open(image_path)
    img = img.convert("L")  # Convert to grayscale

    # Crop the lower-right corner (adjust coordinates as needed)
    width, height = img.size
    cropped_img = img.crop((1200, 740, 1300, 770))  # Example coordinates
    cropped_img.save("cropped_image.png")  # Save cropped image for debugging

    # Use pytesseract to extract text
    text = pytesseract.image_to_string(cropped_img, config='--psm 6 digits')
    #print(f"OCR text: {text}")

    # Extract the number using regex
    match = re.search(r'\d+', text)
    if match:
        number = match.group()
        print(f"Extracted number: {number}")
        logging.info(f"Extracted number: {number}")  # Log the extracted number
        return number
    else:
        print("No number found.")
        logging.info("No number found.")  # Log the failure to extract a number
        return None
    
def main():
    print("Starting in 3 seconds...")
    time.sleep(3)

    sequence_count = 0
    last_image_path = None
    last_extracted_number = None  # Store the last extracted number
    try:
        while True:
            sequence_count += 1
            current_image_path = None
            if sequence_count > 1:
                window_id = get_chiaki_window_id()
                if window_id:
                    current_image_path = f"chiaki_capture_{sequence_count}.png"
                    capture_window(window_id, current_image_path)
                    # Extract number from the captured image
                    extracted_number = extract_number_from_image(current_image_path)
                    if extracted_number:
                        print(f"Extracted number from image: {extracted_number}")
                        if last_extracted_number and int(extracted_number) < int(last_extracted_number):
                            print("Extracted number reduced. Stopping sequence.")
                            logging.info(f"Sequence stopped due to reduced number: {extracted_number} < {last_extracted_number}")
                            break  # Stop the sequence
                        last_extracted_number = extracted_number  # Update the last extracted number
                    else:
                        print("No number extracted from the image. Stopping sequence.")
                        logging.info("Sequence stopped due to failure to extract a number.")
                        break  # Stop the sequence

                    # Delete all other chiaki_capture_*.png except last and current
                    keep = {last_image_path, current_image_path}
                    for f in glob.glob("chiaki_capture_*.png"):
                        if f not in keep and f is not None:
                            try:
                                os.remove(f)
                                print(f"Deleted old image: {f}")
                            except Exception as e:
                                print(f"Could not delete {f}: {e}")
                    if last_image_path and not images_are_equal(last_image_path, current_image_path):
                        print("Window image changed! Going back to start and resetting sequence.")
                        goback_to_start()
                        sequence_count = 0
                        last_image_path = None  # Keep the latest image for next comparison
                        continue  # Restart the loop
                    last_image_path = current_image_path
                else:
                    print("Chiaki-ng window not found.")
            print(f"Executing sequence {sequence_count}...")
            execute_sequence()
            
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")

    print("Done!")

if __name__ == "__main__":
    main()
    #extract_number_from_image("chiaki_capture_2.png")  # Example usage of the OCR function