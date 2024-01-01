import cv2
import mss
import numpy as np

# Screen capture settings
screen_size = {"top": 0, "left": 0, "width": 1920, "height": 1080}
f
# Screen capture loop
with mss.mss() as sct:
    try:
        while True:
            # Capture screen
            img = np.array(sct.grab(screen_size))

            # Display the screen
            cv2.imshow("Live Screen Feed", cv2.cvtColor(img, cv2.COLOR_BGRA2BGR))

            # Stop the live feed with the 'q' key
            if cv2.waitKey(1) == ord('q'):
                break
    except KeyboardInterrupt:
        pass

    # Clean up
    cv2.destroyAllWindows()
