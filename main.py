import os

import cv2
import numpy as np

BIG_COIN_RADIUS = 33

# COLORS
TRAY_BORDER_COLOR = (0, 255, 255)

LABEL_COLOR = (255, 255, 255)

BIG_IN_COLOR = (0, 0, 255)
SMALL_IN_COLOR = (255, 102, 51)
BIG_OUT_COLOR = (80, 80, 255)
SMALL_OUT_COLOR = (204, 204, 51)

# FONTS
LABEL_FONT = cv2.FONT_HERSHEY_DUPLEX
STATS_FONT = cv2.FONT_HERSHEY_SIMPLEX
STATS_FONT_SIZE = 0.7
STATS_FONT_THICKNESS = 2


def find_tray_contour(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tray_contour = max(contours, key=cv2.contourArea)
    return tray_contour


def calculate_tray_area(contour):
    return cv2.contourArea(contour)


def put_custom_label(image, text, position, thickness):
    cv2.putText(image, text, position, LABEL_FONT, 0.7, (0, 0, 0), thickness + 1)
    cv2.putText(image, text, position, LABEL_FONT, 0.7, LABEL_COLOR, thickness)


def detect_coins(image, tray_contour):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20, param1=50, param2=30, minRadius=20,
                               maxRadius=40)

    big_coins_in_tray = 0
    small_coins_in_tray = 0
    big_coins_out_tray = 0
    small_coins_out_tray = 0

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, radius = circle
            if cv2.pointPolygonTest(tray_contour, (x, y), False) >= 0:
                if radius > BIG_COIN_RADIUS:
                    border_color = BIG_IN_COLOR
                    big_coins_in_tray += 1
                else:
                    border_color = SMALL_IN_COLOR
                    small_coins_in_tray += 1
            else:
                if radius > BIG_COIN_RADIUS:
                    border_color = BIG_OUT_COLOR
                    big_coins_out_tray += 1
                else:
                    border_color = SMALL_OUT_COLOR
                    small_coins_out_tray += 1
            cv2.circle(image, (x, y), radius, border_color, 2)
            put_custom_label(image, "Big" if radius > BIG_COIN_RADIUS else "Small", (x - 20, y - 20), 1)

    return big_coins_in_tray, small_coins_in_tray, big_coins_out_tray, small_coins_out_tray


def main():
    sources_dir = './data/source'
    output_dir = './data/output'

    image_names = os.listdir(sources_dir)

    for filename in image_names:
        fullpath = os.path.join(sources_dir, filename)
        image = cv2.imread(fullpath)
        tray_contour = find_tray_contour(image)
        tray_area = calculate_tray_area(tray_contour)
        big_coins_in_tray, small_coins_in_tray, big_coins_out_tray, small_coins_out_tray = detect_coins(image,
                                                                                                        tray_contour)

        # Draw tray contour and put counted coin stats
        cv2.drawContours(image, [tray_contour], -1, TRAY_BORDER_COLOR, 4)

        image = cv2.putText(image, f"BIG IN: {big_coins_in_tray}", (50, 50), STATS_FONT, STATS_FONT_SIZE,
                            BIG_IN_COLOR, STATS_FONT_THICKNESS)
        image = cv2.putText(image, f"BIG OUT: {big_coins_out_tray}", (50, 80), STATS_FONT, STATS_FONT_SIZE,
                            BIG_OUT_COLOR, STATS_FONT_THICKNESS)
        image = cv2.putText(image, f"SMALL IN: {small_coins_in_tray}", (50, 110), STATS_FONT, STATS_FONT_SIZE,
                            SMALL_IN_COLOR, STATS_FONT_THICKNESS)
        image = cv2.putText(image, f"SMALL OUT: {small_coins_out_tray}", (50, 140), STATS_FONT, STATS_FONT_SIZE,
                            SMALL_OUT_COLOR, STATS_FONT_THICKNESS)
        image = cv2.putText(image, f"AREA: {tray_area}", (530, 50), STATS_FONT, STATS_FONT_SIZE, (255, 255, 255),
                            STATS_FONT_THICKNESS)

        print(
            f"Image: {filename}\n"
            f"Tray area: {tray_area}\n"
            f"Big coins in tray: {big_coins_in_tray}\n"
            f"Small coins in tray: {small_coins_in_tray}\n"
            f"Big coins out of tray: {big_coins_out_tray}\n"
            f"Small coins out of tray: {small_coins_out_tray}\n\n"
        )

        cv2.imshow(filename, image)
        key = cv2.waitKey()
        cv2.destroyAllWindows()
        if key == ord('q'):
            return
        elif key == ord('s'):
            cv2.imwrite(f'{output_dir}/out-{filename}', image)


if __name__ == "__main__":
    main()
