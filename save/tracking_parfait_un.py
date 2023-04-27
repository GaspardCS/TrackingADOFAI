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
            # Capture d'écran de la zone de la fenêtre
            screenshot = ImageGrab.grab(bbox=(fenetre.left, fenetre.top, fenetre.right, fenetre.bottom))
            
            # Enregistre la capture d'écran en tant qu'image
            screenshot.save('capture_ecran_fenetre.png')
            
            # Obtention de la couleur du pixel à la position (x, y)
            couleur = screenshot.getpixel((x, y))
            print(f"Couleur du pixel ({x}, {y}) dans la fenêtre '{titre}': {couleur}")
            return couleur
        else:
            print("Les coordonnées (x, y) sont en dehors de la zone de la fenêtre.")
            return None
    else:
        print("La fenêtre n'a pas été trouvée.")
        return None
    
def suivre_element_couleur(image, couleur_basse, couleur_haute):
    # Convertir l'image en espace de couleurs HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Créer un masque pour la plage de couleurs spécifiée
    masque = cv2.inRange(hsv, couleur_basse, couleur_haute)

    # Appliquer une érosion et une dilatation pour réduire le bruit et éliminer les petits objets indésirables
    kernel = np.ones((5,5), np.uint8)
    masque = cv2.erode(masque, kernel, iterations=2)
    masque = cv2.dilate(masque, kernel, iterations=2)

    # Appliquer un flou gaussien pour adoucir les contours
    masque = cv2.GaussianBlur(masque, (9, 9), 2, 2)

    # Détecter les cercles en utilisant la méthode Hough Circles
    circles = cv2.HoughCircles(masque, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        # Ne prendre que le premier cercle détecté
        circle = circles[0][0]

        # Extraire le centre et le rayon du cercle
        centre = (int(circle[0]), int(circle[1]))  # Convertir les coordonnées en entiers
        rayon = circle[2]

        # Retourner le centre et les coordonnées du rectangle englobant
        x, y = int(centre[0] - rayon), int(centre[1] - rayon)
        w, h = int(rayon * 2), int(rayon * 2)
        return centre, (x, y, w, h)
    else:
        return None, None
    
def montrer_resultats(image, centre, rectangle):
    img_affichage = image.copy()
    if centre is not None and rectangle is not None:
        x, y, w, h = rectangle
        cv2.rectangle(img_affichage, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(img_affichage, centre, 5, (0, 0, 255), -1)
        cv2.putText(img_affichage, f"Centre: {centre}", (centre[0] - 20, centre[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
    cv2.imshow("Suivi d'élément", img_affichage)

# Exemple d'utilisation
titre = "A Dance Of Fire And Ice"  # Remplace "Bloc-notes" par le titre de la fenêtre que tu souhaites analyser
x, y = 100, 50  # Remplace ces valeurs par les coordonnées du pixel dont tu veux obtenir la couleur
couleur = couleur_pixel_fenetre(titre, x, y)

if couleur:
    # Convertir la couleur de l'élément en plage HSV
    couleur_hsv = cv2.cvtColor(np.uint8([[couleur]]), cv2.COLOR_RGB2HSV)[0, 0]
    couleur_basse = np.array([couleur_hsv[0] - 10, 100, 100])
    couleur_haute = np.array([couleur_hsv[0] + 10, 255, 255])

    while True:
        # Récupérer la capture d'écran de la fenêtre
        fenetre = detecter_fenetre(titre)
        screenshot = ImageGrab.grab(bbox=(fenetre.left + 8, fenetre.top + 30, fenetre.right - 8, fenetre.bottom - 8))
        image = np.array(screenshot)

        # Suivre l'élément de couleur spécifique
        centre, rectangle = suivre_element_couleur(image, couleur_basse, couleur_haute)

        # Montrer les résultats à l'écran
        montrer_resultats(image, centre, rectangle)

        # Quitter la boucle en appuyant sur la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()