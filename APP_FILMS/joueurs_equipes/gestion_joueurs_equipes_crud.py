"""
    Fichier : gestion_films_genres_crud.py
    Auteur : OM 2021.05.01
    Gestions des "routes" FLASK et des données pour l'association entre les films et les genres.
"""
import sys

import pymysql
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from APP_FILMS import obj_mon_application
from APP_FILMS.database.connect_db_context_manager import MaBaseDeDonnee
from APP_FILMS.erreurs.exceptions import *
from APP_FILMS.erreurs.msg_erreurs import *

"""
    Nom : joueurs_equipes_afficher
    Auteur : OM 2021.05.01
    Définition d'une "route" /joueurs_equipes_afficher
    
    But : Afficher les joueurs avec les equipes associées pour chaque joueur.
    
    Paramètres : id_genre_sel = 0 >> tous les films.
                 id_genre_sel = "n" affiche le film dont l'id est "n"
                 
"""


@obj_mon_application.route("/joueurs_equipes_afficher/<int:id_joueur_sel>", methods=['GET', 'POST'])
def joueurs_equipes_afficher(id_joueur_sel):
    if request.method == "GET":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as Exception_init_joueurs_equipes_afficher:
                code, msg = Exception_init_joueurs_equipes_afficher.args
                flash(f"{error_codes.get(code, msg)} ", "danger")
                flash(f"Exception _init_joueurs_equipes_afficher problème de connexion BD : {sys.exc_info()[0]} "
                      f"{Exception_init_joueurs_equipes_afficher.args[0]} , "
                      f"{Exception_init_joueurs_equipes_afficher}", "danger")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
                strsql_equipes_joueurs_afficher_data = """SELECT ID_joueur, nom_joueur, prenom_joueur, date_de_naissance, taille_joueur, poids_joueur, type_de_poste,
                                                            GROUP_CONCAT(nom_equipe) as EquipesJoueurs FROM t_equipe_joueur
                                                            RIGHT JOIN t_joueur ON t_joueur.ID_joueur = t_equipe_joueur.FK_joueur
                                                            LEFT JOIN t_equipe ON t_equipe.ID_equipe = t_equipe_joueur.FK_equipe
                                                            GROUP BY ID_joueur"""
                if id_joueur_sel == 0:
                    # le paramètre 0 permet d'afficher tous les films
                    # Sinon le paramètre représente la valeur de l'id du film
                    mc_afficher.execute(strsql_equipes_joueurs_afficher_data)
                else:
                    # Constitution d'un dictionnaire pour associer l'id du film sélectionné avec un nom de variable
                    valeur_id_joueur_selected_dictionnaire = {"value_id_joueur_selected": id_joueur_sel}
                    # En MySql l'instruction HAVING fonctionne comme un WHERE... mais doit être associée à un GROUP BY
                    # L'opérateur += permet de concaténer une nouvelle valeur à la valeur de gauche préalablement définie.
                    strsql_equipes_joueurs_afficher_data += """ HAVING ID_joueur= %(value_id_joueur_selected)s"""

                    mc_afficher.execute(strsql_equipes_joueurs_afficher_data, valeur_id_joueur_selected_dictionnaire)

                # Récupère les données de la requête.
                data_equipes_joueurs_afficher = mc_afficher.fetchall()
                print("data_equipes ", data_equipes_joueurs_afficher, " Type : ", type(data_equipes_joueurs_afficher))

                # Différencier les messages.
                if not data_equipes_joueurs_afficher and id_joueur_sel == 0:
                    flash("""La table "t_joueur" est vide. !""", "warning")
                elif not data_equipes_joueurs_afficher and id_joueur_sel > 0:
                    # Si l'utilisateur change l'id_film dans l'URL et qu'il ne correspond à aucun film
                    flash(f"Le joueur {id_joueur_sel} demandé n'existe pas !!", "warning")
                else:
                    flash(f"Données joueurs et equipes affichées !!", "success")

        except Exception as Exception_joueurs_equipes_afficher:
            code, msg = Exception_joueurs_equipes_afficher.args
            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Exception joueurs_equipes_afficher : {sys.exc_info()[0]} "
                  f"{Exception_joueurs_equipes_afficher.args[0]} , "
                  f"{Exception_joueurs_equipes_afficher}", "danger")

    # Envoie la page "HTML" au serveur.
    return render_template("joueurs_equipes/joueurs_equipes_afficher.html", data=data_equipes_joueurs_afficher)


"""
    nom: edit_equipe_joueur_selected
    On obtient un objet "objet_dumpbd"

    Récupère la liste de tous les equipes du joueur sélectionné par le bouton "MODIFIER" de "joueurs_equipes_afficher.html"
    
    Dans une liste déroulante particulière (tags-selector-tagselect), on voit :
    1) Tous les equipes contenues dans la "t_equipe".
    2) Les equipes attribués au joueur selectionné.
    3) Les equipes non-attribués au joueur sélectionné.

    On signale les erreurs importantes

"""


@obj_mon_application.route("/edit_equipe_joueur_selected", methods=['GET', 'POST'])
def edit_equipe_joueur_selected():
    if request.method == "GET":
        try:
            with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
                strsql_equipes_afficher = """SELECT ID_equipe, nom_equipe, nom_president_equipe, nom_entraineur_equipe FROM t_equipe ORDER BY ID_equipe ASC"""
                mc_afficher.execute(strsql_equipes_afficher)
            data_equipes_all = mc_afficher.fetchall()
            print("dans edit_equipe_joueur_selected ---> data_equipes_all", data_equipes_all)

            # Récupère la valeur de "id_film" du formulaire html "films_genres_afficher.html"
            # l'utilisateur clique sur le bouton "Modifier" et on récupère la valeur de "id_film"
            # grâce à la variable "id_film_genres_edit_html" dans le fichier "films_genres_afficher.html"
            # href="{{ url_for('edit_genre_film_selected', id_film_genres_edit_html=row.id_film) }}"
            id_joueur_equipes_edit = request.values['id_joueur_equipes_edit_html']

            # Mémorise l'id du film dans une variable de session
            # (ici la sécurité de l'application n'est pas engagée)
            # il faut éviter de stocker des données sensibles dans des variables de sessions.
            session['session_id_joueur_equipes_edit'] = id_joueur_equipes_edit

            # Constitution d'un dictionnaire pour associer l'id du film sélectionné avec un nom de variable
            valeur_id_joueur_selected_dictionnaire = {"value_id_joueur_selected": id_joueur_equipes_edit}

            # Récupère les données grâce à 3 requêtes MySql définie dans la fonction equipes_joueurs_afficher_data
            # 1) Sélection du film choisi
            # 2) Sélection des genres "déjà" attribués pour le film.
            # 3) Sélection des genres "pas encore" attribués pour le film choisi.
            # ATTENTION à l'ordre d'assignation des variables retournées par la fonction "equipes_joueurs_afficher_data"
            data_equipe_joueur_selected, data_equipes_joueurs_non_attribues, data_equipes_joueurs_attribues = \
                equipes_joueurs_afficher_data(valeur_id_joueur_selected_dictionnaire)

            print(data_equipe_joueur_selected)
            lst_data_joueur_selected = [item['ID_joueur'] for item in data_equipe_joueur_selected]
            print("lst_data_joueur_selected  ", lst_data_joueur_selected,
                  type(lst_data_joueur_selected))

            # Dans le composant "tags-selector-tagselect" on doit connaître
            # les genres qui ne sont pas encore sélectionnés.
            lst_data_equipes_joueurs_non_attribues = [item['ID_equipe'] for item in data_equipes_joueurs_non_attribues]
            session['session_lst_data_equipes_joueurs_non_attribues'] = lst_data_equipes_joueurs_non_attribues
            print("lst_data_equipes_joueurs_non_attribues  ", lst_data_equipes_joueurs_non_attribues,
                  type(lst_data_equipes_joueurs_non_attribues))

            # Dans le composant "tags-selector-tagselect" on doit connaître
            # les genres qui sont déjà sélectionnés.
            lst_data_equipes_joueurs_old_attribues = [item['ID_equipe'] for item in data_equipes_joueurs_attribues]
            session['session_lst_data_equipes_joueurs_old_attribues'] = lst_data_equipes_joueurs_old_attribues
            print("lst_data_equipes_joueurs_old_attribues  ", lst_data_equipes_joueurs_old_attribues,
                  type(lst_data_equipes_joueurs_old_attribues))

            print(" data data_equipe_joueur_selected", data_equipe_joueur_selected, "type ", type(data_equipe_joueur_selected))
            print(" data data_equipes_joueurs_non_attribues ", data_equipes_joueurs_non_attribues, "type ",
                  type(data_equipes_joueurs_non_attribues))
            print(" data_equipes_joueurs_attribues ", data_equipes_joueurs_attribues, "type ",
                  type(data_equipes_joueurs_attribues))

            # Extrait les valeurs contenues dans la table "t_genres", colonne "intitule_genre"
            # Le composant javascript "tagify" pour afficher les tags n'a pas besoin de l'id_genre
            lst_data_equipes_joueurs_non_attribues = [item['nom_equipe'] for item in data_equipes_joueurs_non_attribues]
            print("lst_all_genres gf_edit_equipe_joueur_selected ", lst_data_equipes_joueurs_non_attribues,
                  type(lst_data_equipes_joueurs_non_attribues))

        except Exception as Exception_edit_equipe_joueur_selected:
            code, msg = Exception_edit_equipe_joueur_selected.args
            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Exception edit_equipe_joueur_selected : {sys.exc_info()[0]} "
                  f"{Exception_edit_equipe_joueur_selected.args[0]} , "
                  f"{Exception_edit_equipe_joueur_selected}", "danger")

    return render_template("joueurs_equipes/joueurs_equipes_modifier_tags_dropbox.html",
                           data_equipes=data_equipes_all,
                           data_joueur_selected=data_equipe_joueur_selected,
                           data_equipes_attribues=data_equipes_joueurs_attribues,
                           data_equipes_non_attribues=data_equipes_joueurs_non_attribues)


"""
    nom: update_equipe_joueur_selected

    Récupère la liste de tous les equipes du joueur sélectionné par le bouton "MODIFIER" de "equipes_joueurs_afficher.html"
    
    Dans une liste déroulante particulière (tags-selector-tagselect), on voit :
    1) Tous les genres contenus dans la "t_genre".
    2) Les genres attribués au film selectionné.
    3) Les genres non-attribués au film sélectionné.

    On signale les erreurs importantes
"""


@obj_mon_application.route("/update_equipe_joueur_selected", methods=['GET', 'POST'])
def update_equipe_joueur_selected():
    if request.method == "POST":
        try:
            # Récupère l'id du film sélectionné
            id_joueur_selected = session['session_id_joueur_equipes_edit']
            print("session['session_id_joueur_equipes_edit'] ", session['session_id_joueur_equipes_edit'])

            # Récupère la liste des genres qui ne sont pas associés au film sélectionné.
            old_lst_data_equipes_joueurs_non_attribues = session['session_lst_data_equipes_joueurs_non_attribues']
            print("old_lst_data_equipes_joueurs_non_attribues ", old_lst_data_equipes_joueurs_non_attribues)

            # Récupère la liste des genres qui sont associés au film sélectionné.
            old_lst_data_equipes_joueurs_attribues = session['session_lst_data_equipes_joueurs_old_attribues']
            print("old_lst_data_equipes_joueurs_old_attribues ", old_lst_data_equipes_joueurs_attribues)

            # Effacer toutes les variables de session.
            session.clear()

            # Récupère ce que l'utilisateur veut modifier comme genres dans le composant "tags-selector-tagselect"
            # dans le fichier "equipes_joueurs_modifier_tags_dropbox.html"
            new_lst_str_equipes_joueurs = request.form.getlist('name_select_tags')
            print("new_lst_str_equipes_joueurs ", new_lst_str_equipes_joueurs)

            # OM 2021.05.02 Exemple : Dans "name_select_tags" il y a ['4','65','2']
            # On transforme en une liste de valeurs numériques. [4,65,2]
            new_lst_int_equipe_joueur_old = list(map(int, new_lst_str_equipes_joueurs))
            print("new_lst_equipe_joueur ", new_lst_int_equipe_joueur_old, "type new_lst_equipe_joueur ",
                  type(new_lst_int_equipe_joueur_old))

            # Pour apprécier la facilité de la vie en Python... "les ensembles en Python"
            # https://fr.wikibooks.org/wiki/Programmation_Python/Ensembles
            # OM 2021.05.02 Une liste de "id_genre" qui doivent être effacés de la table intermédiaire "t_genre_film".
            lst_diff_equipes_delete_b = list(
                set(old_lst_data_equipes_joueurs_attribues) - set(new_lst_int_equipe_joueur_old))
            print("lst_diff_equipes_delete_b ", lst_diff_equipes_delete_b)

            # Une liste de "id_genre" qui doivent être ajoutés à la "t_genre_film"
            lst_diff_equipes_insert_a = list(
                set(new_lst_int_equipe_joueur_old) - set(old_lst_data_equipes_joueurs_attribues))
            print("lst_diff_equipes_insert_a ", lst_diff_equipes_insert_a)

            # SQL pour insérer une nouvelle association entre
            # "fk_film"/"id_film" et "fk_genre"/"id_genre" dans la "t_genre_film"
            strsql_insert_equipe_joueur = """INSERT INTO t_equipe_joueur (id_dfgd, FK_equipe, FK_joueur)
                                                    VALUES (NULL, %(value_fk_equipe)s, %(value_fk_joueur)s)"""

            # SQL pour effacer une (des) association(s) existantes entre "id_film" et "id_genre" dans la "t_genre_film"
            strsql_delete_equipe_joueur = """DELETE FROM t_equipe_joueur WHERE FK_equipe = %(value_fk_equipe)s AND FK_joueur = %(value_fk_joueur)s"""

            with MaBaseDeDonnee() as mconn_bd:
                # Pour le film sélectionné, parcourir la liste des genres à INSÉRER dans la "t_genre_film".
                # Si la liste est vide, la boucle n'est pas parcourue.
                for id_equipe_ins in lst_diff_equipes_insert_a:
                    # Constitution d'un dictionnaire pour associer l'id du film sélectionné avec un nom de variable
                    # et "id_genre_ins" (l'id du genre dans la liste) associé à une variable.
                    valeurs_joueur_sel_equipe_sel_dictionnaire = {"value_fk_joueur": id_joueur_selected,
                                                               "value_fk_equipe": id_equipe_ins}

                    mconn_bd.mabd_execute(strsql_insert_equipe_joueur, valeurs_joueur_sel_equipe_sel_dictionnaire)

                # Pour le film sélectionné, parcourir la liste des genres à EFFACER dans la "t_genre_film".
                # Si la liste est vide, la boucle n'est pas parcourue.
                for id_equipe_del in lst_diff_equipes_delete_b:
                    # Constitution d'un dictionnaire pour associer l'id du film sélectionné avec un nom de variable
                    # et "id_genre_del" (l'id du genre dans la liste) associé à une variable.
                    valeurs_joueur_sel_equipe_sel_dictionnaire = {"value_fk_joueur": id_joueur_selected,
                                                               "value_fk_equipe": id_equipe_del}

                    # Du fait de l'utilisation des "context managers" on accède au curseur grâce au "with".
                    # la subtilité consiste à avoir une méthode "mabd_execute" dans la classe "MaBaseDeDonnee"
                    # ainsi quand elle aura terminé l'insertion des données le destructeur de la classe "MaBaseDeDonnee"
                    # sera interprété, ainsi on fera automatiquement un commit
                    mconn_bd.mabd_execute(strsql_delete_equipe_joueur, valeurs_joueur_sel_equipe_sel_dictionnaire)

        except Exception as Exception_update_equipe_joueur_selected:
            code, msg = Exception_update_equipe_joueur_selected.args
            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Exception update_equipe_joueur_selected : {sys.exc_info()[0]} "
                  f"{Exception_update_equipe_joueur_selected.args[0]} , "
                  f"{Exception_update_equipe_joueur_selected}", "danger")

    # Après cette mise à jour de la table intermédiaire "t_genre_film",
    # on affiche les films et le(urs) genre(s) associé(s).
    return redirect(url_for('joueurs_equipes_afficher', id_joueur_sel=id_joueur_selected))


"""
    nom: equipes_joueurs_afficher_data

    Récupère la liste de tous les genres du film sélectionné par le bouton "MODIFIER" de "films_genres_afficher.html"
    Nécessaire pour afficher tous les "TAGS" des genres, ainsi l'utilisateur voit les genres à disposition

    On signale les erreurs importantes
"""


def equipes_joueurs_afficher_data(valeur_id_joueur_selected_dict):
    print("valeur_id_joueur_selected_dict...", valeur_id_joueur_selected_dict)
    try:

        strsql_joueur_selected = """SELECT ID_joueur, nom_joueur, prenom_joueur, date_de_naissance, taille_joueur, poids_joueur, type_de_poste, GROUP_CONCAT(ID_equipe) as EquipesJoueurs FROM t_equipe_joueur
                                        INNER JOIN t_joueur ON t_joueur.ID_joueur = t_equipe_joueur.FK_joueur
                                        INNER JOIN t_equipe ON t_equipe.ID_equipe = t_equipe_joueur.FK_equipe
                                        WHERE ID_joueur = %(value_id_joueur_selected)s"""

        strsql_equipes_joueurs_non_attribues = """SELECT ID_equipe, nom_equipe FROM t_equipe WHERE ID_equipe not in(SELECT ID_equipe as idEquipesJoueurs FROM t_equipe_joueur
                                                    INNER JOIN t_joueur ON t_joueur.ID_joueur = t_equipe_joueur.FK_joueur
                                                    INNER JOIN t_equipe ON t_equipe.ID_equipe = t_equipe_joueur.FK_equipe
                                                    WHERE ID_joueur = %(value_id_joueur_selected)s)"""

        strsql_equipes_joueurs_attribues = """SELECT ID_joueur, ID_equipe, nom_equipe FROM t_equipe_joueur
                                            INNER JOIN t_joueur ON t_joueur.ID_joueur = t_equipe_joueur.FK_joueur
                                            INNER JOIN t_equipe ON t_equipe.ID_equipe = t_equipe_joueur.FK_equipe
                                            WHERE ID_joueur = %(value_id_joueur_selected)s"""

        # Du fait de l'utilisation des "context managers" on accède au curseur grâce au "with".
        with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
            # Envoi de la commande MySql
            mc_afficher.execute(strsql_equipes_joueurs_non_attribues, valeur_id_joueur_selected_dict)
            # Récupère les données de la requête.
            data_equipes_joueurs_non_attribues = mc_afficher.fetchall()
            # Affichage dans la console
            print("equipes_joueurs_afficher_data ----> data_equipes_joueurs_non_attribues ", data_equipes_joueurs_non_attribues,
                  " Type : ",
                  type(data_equipes_joueurs_non_attribues))

            # Envoi de la commande MySql
            mc_afficher.execute(strsql_joueur_selected, valeur_id_joueur_selected_dict)
            # Récupère les données de la requête.
            data_joueur_selected = mc_afficher.fetchall()
            # Affichage dans la console
            print("data_joueur_selected  ", data_joueur_selected, " Type : ", type(data_joueur_selected))

            # Envoi de la commande MySql
            mc_afficher.execute(strsql_equipes_joueurs_attribues, valeur_id_joueur_selected_dict)
            # Récupère les données de la requête.
            data_equipes_joueurs_attribues = mc_afficher.fetchall()
            # Affichage dans la console
            print("data_equipes_joueurs_attribues ", data_equipes_joueurs_attribues, " Type : ",
                  type(data_equipes_joueurs_attribues))

            # Retourne les données des "SELECT"
            return data_joueur_selected, data_equipes_joueurs_non_attribues, data_equipes_joueurs_attribues
    except pymysql.Error as pymysql_erreur:
        code, msg = pymysql_erreur.args
        flash(f"{error_codes.get(code, msg)} ", "danger")
        flash(f"pymysql.Error Erreur dans equipes_joueurs_afficher_data : {sys.exc_info()[0]} "
              f"{pymysql_erreur.args[0]} , "
              f"{pymysql_erreur}", "danger")
    except Exception as exception_erreur:
        code, msg = exception_erreur.args
        flash(f"{error_codes.get(code, msg)} ", "danger")
        flash(f"Exception Erreur dans equipes_joueurs_afficher_data : {sys.exc_info()[0]} "
              f"{exception_erreur.args[0]} , "
              f"{exception_erreur}", "danger")
    except pymysql.err.IntegrityError as IntegrityError_equipes_joueurs_afficher_data:
        code, msg = IntegrityError_equipes_joueurs_afficher_data.args
        flash(f"{error_codes.get(code, msg)} ", "danger")
        flash(f"pymysql.err.IntegrityError Erreur dans equipes_joueurs_afficher_data : {sys.exc_info()[0]} "
              f"{IntegrityError_equipes_joueurs_afficher_data.args[0]} , "
              f"{IntegrityError_equipes_joueurs_afficher_data}", "danger")
