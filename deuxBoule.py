import pygetwindow as gw
import pyautogui
from PIL import ImageGrab
import cv2
import numpy as np

def detecter_fenetre(titre):
    try:
        fenetre = gw.getWindowsWithTitle(titre)[0]
        return fenetre
    except IndexError:
        return None
    
def couleur_pixel_fenetre(titre, x, y):
    fenetre = detecter_fenetre(titre)
    
    if fenetre is not None:
        largeur = fenetre.width
        hauteur = fenetre.height
        
        if 0 <= x < largeur and 0 <= y < hauteur:
            screenshot = ImageGrab.grab(bbox=(fenetre.left, fenetre.top, fenetre.right, fenetre.bottom))
            
            screenshot.save('capture_ecran_fenetre.png')
            
            couleur = screenshot.getpixel((x, y))
            print(f"Couleur du pixel ({x}, {y}) dans la fenêtre '{titre}': {couleur}")
            return couleur
        else:
            print("Les coordonnées (x, y) sont en dehors de la zone de la fenêtre.")
            return None
    else:
        print("La fenêtre n'a pas été trouvée.")
        return None

def suivre_elements_couleur(image, couleur_basse1, couleur_haute1, couleur_basse2, couleur_haute2):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    masque1 = cv2.inRange(hsv, couleur_basse1, couleur_haute1)
    masque2 = cv2.inRange(hsv, couleur_basse2, couleur_haute2)
    masque = cv2.bitwise_or(masque1, masque2)

    kernel = np.ones((5,5), np.uint8)
    masque = cv2.erode(masque, kernel, iterations=2)
    masque = cv2.dilate(masque, kernel, iterations=2)

    masque = cv2.GaussianBlur(masque, (9, 9), 2, 2)

    circles = cv2.HoughCircles(masque, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        return circles
    else:
        return None

def montrer_resultats(image, circles):
    img_affichage = image.copy()
    if circles is not None:
        for circle in circles[0]:
            centre = (int(circle[0]), int(circle[1]))
            rayon = int(circle[2])

            x, y = int(centre[0] - rayon), int(centre[1] - rayon)
            w, h = int(rayon * 2), int(rayon * 2)
            cv2.rectangle(img_affichage, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(img_affichage, centre, 5, (0, 0, 255), -1)
            cv2.putText(img_affichage, f"Centre: {centre}", (centre[0] - 20, centre[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow("Suivi d'éléments", img_affichage)
            
titre = "A Dance Of Fire And Ice"

couleur1 = (57, 42, 255)
couleur2 = (255, 66, 42)

if couleur1 and couleur2:
    couleur_hsv1 = cv2.cvtColor(np.uint8([[couleur1]]), cv2.COLOR_RGB2HSV)[0, 0]
    couleur_basse1 = np.array([couleur_hsv1[0] - 10, 100, 100])
    couleur_haute1 = np.array([couleur_hsv1[0] + 10, 255, 255])

    couleur_hsv2 = cv2.cvtColor(np.uint8([[couleur2]]), cv2.COLOR_RGB2HSV)[0, 0]
    couleur_basse2 = np.array([couleur_hsv2[0] - 10, 100, 100])
    couleur_haute2 = np.array([couleur_hsv2[0] + 10, 255, 255])

    while True:
        fenetre = detecter_fenetre(titre)
        screenshot = ImageGrab.grab(bbox=(fenetre.left + 8, fenetre.top + 30, fenetre.right - 8, fenetre.bottom - 8))
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        circles = suivre_elements_couleur(image, couleur_basse1, couleur_haute1, couleur_basse2, couleur_haute2)

        montrer_resultats(image, circles)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()