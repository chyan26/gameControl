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
from PIL import Image, ImageChops, ImageStat, ImageFilter, ImageEnhance
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
    
class ImageProcessor:
    def __init__(self):
        self.last_image_path = None
        self.last_extracted_number = None

    def get_chiaki_window_id(self):
        """
        Retrieves the Chiaki window ID.
        """
        window_list = CG.CGWindowListCopyWindowInfo(CG.kCGWindowListOptionOnScreenOnly, CG.kCGNullWindowID)
        for window in window_list:
            owner = window.get('kCGWindowOwnerName', '')
            name = window.get('kCGWindowName', '')
            if 'chiaki' in owner.lower() or 'chiaki' in name.lower():
                return window['kCGWindowNumber']
        return None

    def capture_window(self, window_id, filename):
        """
        Captures the window image and saves it to the specified filename.
        """
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

    def extract_number_from_image(self, image_path):
        """
        Extracts a number from the lower-right corner of the given image using OCR.
        """
        img = Image.open(image_path)
        img = img.convert("L")  # Convert to grayscale

        # Crop the lower-right corner (adjust coordinates as needed)
        width, height = img.size
        left = width * 0.86  # Start at 86% of the width
        top = height * 0.86  # Start at 86% of the height
        right = width * 0.93  # End at 93% of the width
        bottom = height * 0.90  # End at 90% of the height

        cropped_img = img.crop((left, top, right, bottom))
        # Enhance the image
        cropped_img = cropped_img.filter(ImageFilter.SHARPEN)  # Sharpen the image
        enhancer = ImageEnhance.Contrast(cropped_img)
        cropped_img = enhancer.enhance(2.0)  # Increase contrast
        cropped_img.save("cropped_image.png")  # Save cropped image for debugging

        # Use pytesseract to extract text
        text = pytesseract.image_to_string(cropped_img, config='--psm 6 digits')
        print(f"OCR text: {text}")

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

    def compare_images(self, img1_path, img2_path, tolerance=10):
        """
        Compares two images and returns True if they are similar within the given tolerance.
        """
        if not os.path.exists(img1_path) or not os.path.exists(img2_path):
            return True  # If one doesn't exist, treat as equal for first run
        img1 = Image.open(img1_path).convert("RGB")
        img2 = Image.open(img2_path).convert("RGB")
        diff = ImageChops.difference(img1, img2)
        stat = ImageStat.Stat(diff)
        rms = sum([v**2 for v in stat.mean]) ** 0.5
        print(f"RMS difference: {rms}")
        return rms < tolerance  # True if images are similar enough

    def delete_old_images(self, current_image_path):
        """
        Deletes old screenshots except the last and current ones.
        """
        keep = {self.last_image_path, current_image_path}
        for f in glob.glob("chiaki_capture_*.png"):
            if f not in keep and f is not None:
                os.remove(f)  # Directly delete the file without waiting
                print(f"Deleted old image: {f}")

    def capture_and_process(self, window_id, sequence_count):
        """
        Captures the window image, extracts the number, and checks conditions.
        Returns True if the sequence should continue, False otherwise.
        """
        current_image_path = f"chiaki_capture_{sequence_count}.png"
        self.capture_window(window_id, current_image_path)

        # Extract number from the captured image
        extracted_number = self.extract_number_from_image(current_image_path)
        if extracted_number:
            print(f"Extracted number from image: {extracted_number}")
            logging.info(f"Extracted number: {extracted_number}")
            if self.last_extracted_number and int(extracted_number) < int(self.last_extracted_number):
                print("Extracted number reduced. Stopping sequence.")
                logging.info(f"Sequence stopped due to reduced number: {extracted_number} < {self.last_extracted_number}")
                return False  # Stop the sequence
            self.last_extracted_number = extracted_number  # Update the last extracted number
        else:
            print("No number extracted from the image. Stopping sequence.")
            logging.info("Sequence stopped due to failure to extract a number.")
            return False  # Stop the sequence

        # Delete old screenshots
        self.delete_old_images(current_image_path)

        self.last_image_path = current_image_path  # Update the last image path
        return True  # Continue the sequence


def main():
    print("Starting in 3 seconds...")
    time.sleep(3)

    sequence_count = 0
    image_processor = ImageProcessor()  # Initialize the ImageProcessor class

    try:
        while True:
            sequence_count += 1
            if sequence_count > 1:
                window_id = image_processor.get_chiaki_window_id()
                if window_id:
                    if not image_processor.capture_and_process(window_id, sequence_count):
                        break  # Stop the sequence if conditions are met
                else:
                    print("Chiaki-ng window not found.")
            print(f"Executing sequence {sequence_count}...")
            execute_sequence()
            
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")

    print("Done!")

if __name__ == "__main__":
    #main()
    image_processor = ImageProcessor()
    image_processor.extract_number_from_image("chiaki_capture_138.png")  # Example usage of the OCR function