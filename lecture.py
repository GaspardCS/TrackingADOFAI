import pygetwindow as gw
import pyautogui
from PIL import ImageGrab


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


titre = "A Dance Of Fire And Ice"
x, y = 378,298
couleur = couleur_pixel_fenetre(titre, x, y)
