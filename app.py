from flask import Flask,render_template, request
import matplotlib.pyplot as plt
import io
import base64
import os
import json
import math
import statistics
import numpy as np
from matplotlib.ticker import MaxNLocator
app = Flask(__name__)
@app.route('/')
def accueil():
    return render_template('choix.html')
@app.route('/saisie')
def saisie():
    return render_template('index.html')
@app.route('/calculer',methods=['POST'])
def calculer():
    nom = request.form.get('utilisateur')
    tel = request.form.get('telephone')
    poids = float(request.form.get('poids'))
    taille = float(request.form.get('taille'))
    imc = poids/(taille*taille)
    imc = round(imc,2)
    if imc<18.5:
        etat = "Insuffisance ponderale(maigreur)"
        conseil = "Pensez à consulter un nutritioniste pour un regime adapté."
    elif 18.5 <= imc <25:
        etat = "Corpulance normale"
        conseil = "Bravo ! Continuez à maintenir votre hygiène de vie."
    elif 25 <= imc <30:
        etat = "Surpoids"
        conseil = "Attention une activité physique régulière est recommandée."
    else:
        etat = "Obésité"
        conseil = "Il est fortement conseillé de consulter un médecin."
    nouvelle_donnee = {
        "nom": nom,
        "telephone": tel,
        "poids": poids,
        "taille": taille,
        "imc": imc,
        "etat": etat
    }  
    if not os.path.exists('donnees.json'):
        with open('donnees.json','w') as f:
            json.dump([],f)
    with open('donnees.json','r') as f:
        archives = json.load(f)
    archives.append(nouvelle_donnee)
    with open('donnees.json','w')as f:
        json.dump(archives,f,indent=4)
    return render_template('resultat.html',nom=nom,imc=imc,etat=etat,conseil=conseil)
@app.route('/stats')
def stats():
    if not os.path.exists('donnees.json'):
        return "Aucune donnees collecte pour le moment."
    with open('donnees.json','r') as f:
        data = json.load(f)
    if not data:
        return "Le fichier de donnees est vide."
    liste_imc= [d['imc'] for d in data]
    n = len(liste_imc)
    total_collectes = n
    moyenne = sum(liste_imc)/n
    somme_carres = sum((x-moyenne)**2 for x in liste_imc)
    variance = somme_carres/n
    ecart_type = math.sqrt(variance)
    if liste_imc:
        mediane_imc = statistics.median(liste_imc)
    else:
        mediane_imc = 0
    try:
        mode_imc = statistics.mode(liste_imc) 
    except: 
        mode_imc = liste_imc[0] if liste_imc else 0
    nb_critiques = 0
    for d in data:
        if  float(d['imc'])>=30:
            nb_critiques+=1             

    plt.figure(figsize=(10, 6))
    bins_fines = np.arange(0, 105, 5)

    
    n, bins, patches = plt.hist(liste_imc, bins=bins_fines, edgecolor='white', linewidth=0.5)

   
    for i in range(len(patches)):
        milieu_segment = (bins[i] + bins[i+1]) / 2
        if milieu_segment < 18.5:
            patches[i].set_facecolor('#3498db') # Bleu - Maigre
        elif milieu_segment < 25:
            patches[i].set_facecolor('#2ecc71') # Vert - Normal
        elif milieu_segment < 30:
            patches[i].set_facecolor('#f1c40f') # Jaune - Surpoids
        else:
            patches[i].set_facecolor('#e74c3c') # Rouge - Obèse

    
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    if len(n) > 0:
        plt.ylim(0, max(n) + 1)

    
    plt.xticks(np.arange(0, 101, 10))
    nb_critiques = sum(1 for x in liste_imc if x >= 30)
    moyenne = sum(liste_imc) / len(liste_imc) if liste_imc else 0
    plt.xlim(0, 100)   
    nb_critiques = sum(1 for x in liste_imc if x >= 30)
    plt.title("Distribution des IMC par Catégories")
    plt.ylabel("Nombre de personnes")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return render_template('stats.html',donnees=data,moyenne=round(moyenne,2),mediane=round(mediane_imc,2), mode=round(mode_imc,2),variance=round(variance,2),nb_critiques=nb_critiques,ecart_type=round(ecart_type,2), total=total_collectes,graphique=plot_url)
if __name__ == '__main__':
    app.run(debug=True)