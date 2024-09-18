import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
import time

oyun_penceresi = None
for window in gw.getAllTitles():
  if "TelegramDesktop" in window:
      oyun_penceresi = gw.getWindowsWithTitle(window)[0]
      break

if oyun_penceresi:
  oyun_penceresi.activate()

if not oyun_penceresi:
  print("Oyun penceresi bulunamadı.")
  exit()

while True:
  start_time = time.time()

  sol, üst, genişlik, yükseklik = oyun_penceresi.left + 13, oyun_penceresi.top + 220, oyun_penceresi.width - 25, oyun_penceresi.height - 300
  yarı_yükseklik = yükseklik // 2

  screenshot = pyautogui.screenshot(region=(sol, üst, genişlik, yükseklik))
  screenshot = np.array(screenshot)

  screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

  lower_yellow = np.array([20, 100, 100])
  upper_yellow = np.array([30, 255, 255])
  hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
  mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

  contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  topmost_contour = None
  topmost_y = float('inf')
  pink_dot_center = None
  green_hitboxes = []

  for contour in contours_yellow:
      M = cv2.moments(contour)
      if M["m00"] != 0:
          cX = int(M["m10"] / M["m00"])
          cY = int(M["m01"] / M["m00"])
          x, y, w, h = cv2.boundingRect(contour)
          
          if y >= yarı_yükseklik:
              cv2.rectangle(screenshot, (x, y), (x + 3 * w, y + 3 * h), (0, 255, 0), 1)
          else:
              cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 1)

          if y < topmost_y:
              topmost_y = y
              topmost_contour = contour

          if y + h >= yükseklik - 700:
              green_hitboxes.append((x, y, w, h))

  if topmost_contour is not None:
      M = cv2.moments(topmost_contour)
      if M["m00"] != 0:
          cX = int(M["m10"] / M["m00"])
          cY = int(M["m01"] / M["m00"])
          pink_dot_center = (cX, cY)
          cv2.rectangle(screenshot, (cX - 5, cY - 5), (cX + 5, cY + 5), (255, 0, 255), -1)

  lower_white = np.array([0, 0, 200])
  upper_white = np.array([180, 25, 255])
  mask_white = cv2.inRange(hsv, lower_white, upper_white)

  contours_white, _ = cv2.findContours(mask_white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  nearest_white_point = None
  min_distance = float('inf')

  for contour in contours_white:
      M = cv2.moments(contour)
      if M["m00"] != 0:
          cX = int(M["m10"] / M["m00"])
          cY = int(M["m01"] / M["m00"])
          if pink_dot_center:
              distance = np.sqrt((cX - pink_dot_center[0]) ** 2 + (cY - pink_dot_center[1]) ** 2)
              if distance < min_distance:
                  min_distance = distance
                  nearest_white_point = (cX, cY)

  if pink_dot_center and nearest_white_point:

      dx = nearest_white_point[0] - pink_dot_center[0]
      dy = nearest_white_point[1] - pink_dot_center[1]
      
      if dx != 0:
          slope = dy / dx

          if slope != 0:

              x_bottom = int((yükseklik - pink_dot_center[1]) / slope + pink_dot_center[0])
              cv2.line(screenshot, pink_dot_center, (x_bottom, yükseklik), (255, 255, 255), 2)
          else:

              cv2.line(screenshot, pink_dot_center, (pink_dot_center[0], yükseklik), (255, 255, 255), 2)
      else:

          cv2.line(screenshot, pink_dot_center, (pink_dot_center[0], yükseklik), (255, 255, 255), 2)

 
      for (x, y, w, h) in green_hitboxes:
          if x_bottom >= x and x_bottom <= x + w:

              center_x = sol + genişlik // 2
              center_y = üst + yükseklik // 2
              pyautogui.moveTo(center_x, center_y)
              pyautogui.click(974, 760)
              break


  cv2.line(screenshot, (0, yükseklik - 700), (genişlik, yükseklik - 700), (0, 0, 255), 1)

 
  cv2.imshow("Hitbox", screenshot)


  if cv2.waitKey(1) & 0xFF == ord('q'):
      break


  elapsed_time = time.time() - start_time
  time.sleep(max(0, 0.033 - elapsed_time)) 

cv2.destroyAllWindows()