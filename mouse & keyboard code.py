import cv2
import numpy as np
import pyautogui
import time
pyautogui.FAILSAFE = False
# Some global variables or others that need prior intialization are initalized here

# colour ranges for feeding to the inRange funtions
blue_range = np.array([[100, 150, 0], [120, 255, 255]])
yellow_range = np.array([[20, 100, 100], [30, 255, 255]])
red_range = np.array([[170, 120, 70], [180, 255, 255]])

# Prior initialization of all centers for safety
b_cen, y_pos, r_cen = [240, 320], [240, 320], [240, 320]
cursor = [960, 540]

# Area ranges for contours of different colours to be detected
r_area = [100, 1700]
b_area = [100, 1700]
y_area = [100, 1700]

# Rectangular kernal for eroding and dilating the mask for primary noise removal
kernel = np.ones((7, 7), np.uint8)

# Status variables defined globally
perform = False
showCentroid = False
kb= False
kb1=False

# To bring to the top the contours with largest area in the specified range
# Used in drawContour()
def swap(array, i, j):
    temp = array[i]
    array[i] = array[j]
    array[j] = temp


# Distance between two centroids
def distance(c1, c2):
    distance = pow(pow(c1[0] - c2[0], 2) + pow(c1[1] - c2[1], 2), 0.5)
    return distance


# To toggle status of control variables
def changeStatus(key):
    global perform
    global kb
    global kb1
    global showCentroid

    # toggle mouse simulation
    if key == ord('p'):
        perform = not perform
        if perform:
            print('Mouse Mode ON...')
        else:
            print('Mouse Mode OFF...')

    elif key == ord('a'):
        kb = not kb
        if kb:
            print('Keyboard Mode ON')
        else:
            print('Keboard Mode OFF')

    elif key == ord('b'):
        kb1 = not kb1
        if kb1:
            print('Keyboard 1 Mode ON')
        else:
            print('Keboard 1 Mode OFF')

    # toggle display of centroids
    elif key == ord('c'):
        showCentroid = not showCentroid
        if showCentroid:
            print('Showing Centroids...')
        else:
            print('Not Showing Centroids...')


    else:
        pass


# cv2.inRange function is used to filter out a particular color from the frame
# The result then undergoes morphosis i.e. erosion and dilation
# Resultant frame is returned as mask
def makeMask(hsv_frame, color_Range):
    mask = cv2.inRange(hsv_frame, color_Range[0], color_Range[1])
    # Morphosis next ...
    eroded = cv2.erode(mask, kernel, iterations=1)
    dilated = cv2.dilate(eroded, kernel, iterations=1)

    return dilated


# Contours on the mask are detected.. Only those lying in the previously set area
# range are filtered out and the centroid of the largest of these is drawn and returned
def drawCentroid(vid, color_area, mask, showCentroid):
    contour, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    l = len(contour)
    area = np.zeros(l)

    # filtering contours on the basis of area rane specified globally
    for i in range(l):
        if cv2.contourArea(contour[i]) > color_area[0] and cv2.contourArea(contour[i]) < color_area[1]:
            area[i] = cv2.contourArea(contour[i])
        else:
            area[i] = 0

    a = sorted(area, reverse=True)

    # bringing contours with largest valid area to the top
    for i in range(l):
        for j in range(1):
            if area[i] == a[j]:
                swap(contour, i, j)

    if l > 0:
        # finding centroid using method of 'moments'
        M = cv2.moments(contour[0])
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            center = (cx, cy)
            if showCentroid:
                cv2.circle(vid, center, 5, (0, 0, 0), -1)

            return center
    else:
        # return error handling values
        return (-1, -1)


'''
This function takes as input the center of yellow region (yc) and
the previous cursor position (pyp). The new cursor position is calculated
in such a way that the mean deviation for desired steady state is reduced.
'''


def setCursorPos(yc, pyp):
    yp = np.zeros(2)

    if abs(yc[0] - pyp[0]) < 5 and abs(yc[1] - pyp[1]) < 5:
        yp[0] = yc[0] + .7 * (pyp[0] - yc[0])
        yp[1] = yc[1] + .7 * (pyp[1] - yc[1])
    else:
        yp[0] = yc[0] + .1 * (pyp[0] - yc[0])
        yp[1] = yc[1] + .1 * (pyp[1] - yc[1])

    return yp




# Depending upon the relative positions of the three centroids, this function chooses whether
# the user desires free movement of cursor, left click, right click or dragging
def chooseAction(yp, rc, bc):
    out = np.array(['move', 'false'])
    if rc[0] != -1 and bc[0] != -1:

        if distance(yp, rc) < 50 and distance(yp, bc) < 50 and distance(rc, bc) < 50:
            out[0] = 'drag'
            out[1] = 'true'
            return out
        elif distance(rc, bc) < 40:
            out[0] = 'left'
            return out
        elif distance(yp, rc) < 40:
            out[0] = 'right'
            return out
        elif distance(yp, bc) < 40:
            out[0] = 'dob'
            return out

        elif distance(yp, rc) > 40 and rc[1] - bc[1] > 120:
            out[0] = 'down'
            return out

        elif bc[0] - rc[0] > 150 and distance(yp, rc) > 40 :
            out[0] = 'scree'

            return out

        elif bc[1] - rc[1] > 110:
            out[0] = 'up'
            return out
        else:
            return out

    else:
        out[0] = -1
        return out


# Movement of cursor on screen, left click, right click,scroll up, scroll down
# and dragging actions are performed here based on value stored in 'action'.
def performAction(yp, rc, bc, action, drag, perform):
    if perform:
        cursor[0] = 4 * (yp[0] - 110)
        cursor[1] = 4 * (yp[1] - 120)
        if action == 'move':

            if yp[0] > 110 and yp[0] < 590 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(cursor[0], cursor[1])
            elif yp[0] < 110 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(8, cursor[1])
            elif yp[0] > 590 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(1912, cursor[1])
            elif yp[0] > 110 and yp[0] < 590 and yp[1] < 120:
                pyautogui.moveTo(cursor[0], 8)
            elif yp[0] > 110 and yp[0] < 590 and yp[1] > 390:
                pyautogui.moveTo(cursor[0], 1072)
            elif yp[0] < 110 and yp[1] < 120:
                pyautogui.moveTo(8, 8)
            elif yp[0] < 110 and yp[1] > 390:
                pyautogui.moveTo(8, 1072)
            elif yp[0] > 590 and yp[1] > 390:
                pyautogui.moveTo(1912, 1072)
            else:
                pyautogui.moveTo(1912, 8)

        elif action == 'left':
            pyautogui.click(button='left')
            time.sleep(1)

        elif action == 'right':
            pyautogui.click(button='right')
            time.sleep(0.3)

        elif action == 'dob':
            pyautogui.press('volumedown')


        elif action == 'scree':
            pyautogui.press('volumeup')



        elif action == 'up':
            pyautogui.scroll(50)
        #			time.sleep(0.3)

        elif action == 'down':
            pyautogui.scroll(-50)
        #			time.sleep(0.3)


def KeyAction(yp, rc, bc, action, drag, Kb):
    if kb:
        cursor[0] = 4 * (yp[0] - 110)
        cursor[1] = 4 * (yp[1] - 120)
        if action == 'move':

            if yp[0] > 110 and yp[0] < 590 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(cursor[0], cursor[1])
            elif yp[0] < 110 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(8, cursor[1])
            elif yp[0] > 590 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(1912, cursor[1])
            elif yp[0] > 110 and yp[0] < 590 and yp[1] < 120:
                pyautogui.moveTo(cursor[0], 8)
            elif yp[0] > 110 and yp[0] < 590 and yp[1] > 390:
                pyautogui.moveTo(cursor[0], 1072)
            elif yp[0] < 110 and yp[1] < 120:
                pyautogui.moveTo(8, 8)
            elif yp[0] < 110 and yp[1] > 390:
                pyautogui.moveTo(8, 1072)
            elif yp[0] > 590 and yp[1] > 390:
                pyautogui.moveTo(1912, 1072)
            else:
                pyautogui.moveTo(1912, 8)

        elif action == 'left':
            pyautogui.click(button='left')
            time.sleep(0.3)

        elif action == 'right':
            pyautogui.write('We are working on our product called XYZ. We give full services and features of this product in a very low cost. Call us on the given number 090078601')
            time.sleep(0.3)

        elif action == 'dob':

            pyautogui.hotkey('ctrl','s')

        elif action == 'up':
            pyautogui.hotkey('ctrl' , 'a')

        elif action == 'scree':
            print("Text Copied")
            pyautogui.hotkey('ctrl','c')
            time.sleep(1.0)

        elif action == 'down':
            pyautogui.hotkey('ctrl','v')
            time.sleep(1.0)


def KeyAction1(yp, rc, bc, action, drag, Kb1):
    if kb1:
        cursor[0] = 4 * (yp[0] - 110)
        cursor[1] = 4 * (yp[1] - 120)
        if action == 'move':

            if yp[0] > 110 and yp[0] < 590 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(cursor[0], cursor[1])
            elif yp[0] < 110 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(8, cursor[1])
            elif yp[0] > 590 and yp[1] > 120 and yp[1] < 390:
                pyautogui.moveTo(1912, cursor[1])
            elif yp[0] > 110 and yp[0] < 590 and yp[1] < 120:
                pyautogui.moveTo(cursor[0], 8)
            elif yp[0] > 110 and yp[0] < 590 and yp[1] > 390:
                pyautogui.moveTo(cursor[0], 1072)
            elif yp[0] < 110 and yp[1] < 120:
                pyautogui.moveTo(8, 8)
            elif yp[0] < 110 and yp[1] > 390:
                pyautogui.moveTo(8, 1072)
            elif yp[0] > 590 and yp[1] > 390:
                pyautogui.moveTo(1912, 1072)
            else:
                pyautogui.moveTo(1912, 8)

        elif action == 'left':
            pyautogui.click(button='left')
            time.sleep(1.0)

        elif action == 'right':
            pyautogui.hotkey('win' , 'printscreen')
            time.sleep(3.0)

        elif action == 'dob':

            pyautogui.hotkey('ctrl', 'p')
            time.sleep(2.0)

        elif action == 'up':
            pyautogui.hotkey('win' , 'up')
            time.sleep(1.0)

        elif action == 'scree':
            pyautogui.hotkey('alt','f4')
            time.sleep(2)

        elif action == 'down':
            pyautogui.hotkey('win','down')
            time.sleep(1.0)



cap = cv2.VideoCapture(0)

cv2.namedWindow('Frame')
print('Press C to display the centroid of various colours.')
print('Press P to turn ON OFF Mouse Mode \nPress A to turn ON OFF Keyboard Mode \nPress B to turn ON OFF Keyboard 1 Mode')
print('	Press ESC to exit.')


while (1):

    k = cv2.waitKey(10) & 0xFF
    changeStatus(k)

    _, frameinv = cap.read()
    # flip horizontaly to get mirror image in camera
    frame = cv2.flip(frameinv, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    b_mask = makeMask(hsv, blue_range)
    r_mask = makeMask(hsv, red_range)
    y_mask = makeMask(hsv, yellow_range)
    py_pos = y_pos

    b_cen = drawCentroid(frame, b_area, b_mask, showCentroid)
    r_cen = drawCentroid(frame, r_area, r_mask, showCentroid)
    y_cen = drawCentroid(frame, y_area, y_mask, showCentroid)

    if py_pos[0] != -1 and y_cen[0] != -1 and y_pos[0] != -1:
        y_pos = setCursorPos(y_cen, py_pos)

    output = chooseAction(y_pos, r_cen, b_cen)
    if output[0] != -1 and perform == True and kb == False and kb1 == False:
        performAction(y_pos, r_cen, b_cen, output[0], output[1], perform)

    if output[0] != -1 and perform == False and kb == True and kb1 == False:

        KeyAction(y_pos, r_cen, b_cen, output[0], output[1], kb)

    if output[0] != -1 and perform == False and kb == False and kb1 == True:

        KeyAction1(y_pos, r_cen, b_cen, output[0], output[1], kb1)

    cv2.imshow('Frame', frame)

    if k == 27:
        break

cv2.destroyAllWindows()