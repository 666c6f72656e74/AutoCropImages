# Importer les modules nécessaires
import tkinter as tk
from tkinter import filedialog
import cv2
import os

version = "1.1"

"""
Problèmes connus:
L'autocrop des fichiers contenant des caractères spéciaux dans leur nom ou chemin ne fonctionne pas.
"""

# Créer une fonction pour sélectionner des images
def select_images():
    # Ouvrir une boîte de dialogue pour choisir les fichiers
    filenames = filedialog.askopenfilenames(title="Sélectionner des images", filetypes=[("Fichiers image", "*.jpg *.png")])

    # Parcourir la liste des fichiers choisis
    if filenames:
        # Mettre à jour le nombre d'images sélectionnées
        nbr_fic = len(filenames)
        progress.insert(tk.END, f"\n{nbr_fic} image(s) sélectionnée(s). Traitement...\n\n")
        window.update()

        for i in filenames:
            filename = os.path.abspath(i)
            print(filename)

            try:
                # Récupère le nom du fichier filename à cropper
                nom_filename = os.path.basename(i)
                # Charger l'image avec cv2
                img = cv2.imread(i, cv2.IMREAD_UNCHANGED)
                # Convertir l'image en nuances de gris
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                ############
                img_blur = cv2.GaussianBlur(gray, (5, 5), 0)
                edged = cv2.Canny(img_blur, 10, 20)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                dilate = cv2.dilate(edged, kernel, iterations=1)
                #############
                # Appliquer un seuil adaptatif pour binariser l'image
                thresh = cv2.adaptiveThreshold(dilate, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                # Trouver les contours dans l'image binarisée
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # Trier les contours par aire décroissante
                sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
                # Prendre le premier contour comme le plus gros objet
                biggest_object = sorted_contours[0]
                # Calculer le rectangle englobant du plus gros objet
                x, y, w, h = cv2.boundingRect(biggest_object)
                # Ajouter une marge de 10 pixels autour du rectangle
                margin = 10
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(img.shape[1] - x, w + 2 * margin)
                h = min(img.shape[0] - y, h + 2 * margin)
                # Cropper l'image autour du rectangle
                cropped_img = img[y:y+h, x:x+w]
                # Sauvegarder l'image croppée avec un nouveau nom
                new_filename = filename[:-4] + "_cropped.jpg"
                cv2.imwrite(new_filename, cropped_img)
                # Afficher le message "OK" dans la fenêtre principale quand le traitement est terminé sans erreur
                progress.insert(tk.END, f"OK : {nom_filename}\n")
                window.update()
            except:
                progress.insert(tk.END, f"ERREUR : {nom_filename}\n")
                window.update()
                continue
        progress.insert(tk.END, "\nTerminé.\n")
        window.update()

# Créer une fenêtre principale
window = tk.Tk()
window.title(f"AutoCropImages v{version}")

# Créer un bouton pour sélectionner des images
button = tk.Button(window, text="Sélectionner des images", font=("Arial", 16, "bold"), command=select_images)
button.pack(padx=20, pady=20)

# Créer une fenêtre qui affichera l'avancé des traitements.
progress = tk.Text(window, wrap=tk.NONE, height=30, width=100)
progress.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Créer un widget Scrollbar et le lier au widget Text
scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=progress.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
progress['yscrollcommand'] = scrollbar.set

progress.insert(tk.END, "\nINFO: Les images croppées sont enregistrées dans le même dossier que les images originales.\n")
window.update()
progress.insert(tk.END, "\nSélectionnez des images.\n")
window.update()

# Lancer la boucle principale de la fenêtre
window.mainloop()
