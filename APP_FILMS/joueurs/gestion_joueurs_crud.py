"""
    Fichier : gestion_genres_crud.py
    Auteur : OM 2021.03.16
    Gestions des "routes" FLASK et des données pour les genres.
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
from APP_FILMS.joueurs.gestion_joueurs_wtf_forms import FormWTFAjouterJoueur
from APP_FILMS.joueurs.gestion_joueurs_wtf_forms import FormWTFDeleteJoueur
from APP_FILMS.joueurs.gestion_joueurs_wtf_forms import FormWTFUpdateJoueur

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /joueurs_afficher

    Test : ex : http://127.0.0.1:5005/joueurs_afficher

    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                id_joueur_sel = 0 >> tous les joueurs.
                id_joueur_sel = "n" affiche le joueur dont l'id est "n"
"""


@obj_mon_application.route("/joueurs_afficher/<string:order_by>/<int:id_joueur_sel>", methods=['GET', 'POST'])
def joueurs_afficher(order_by, id_joueur_sel):
    if request.method == "GET":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion joueurs ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur GestionJoueurs {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
                if order_by == "ASC" and id_joueur_sel == 0:
                    strsql_joueurs_afficher = """SELECT ID_joueur, nom_joueur, prenom_joueur, date_de_naissance, taille_joueur, poids_joueur, type_de_poste FROM t_joueur ORDER BY ID_joueur ASC"""
                    mc_afficher.execute(strsql_joueurs_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_genre"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du genre sélectionné avec un nom de variable
                    valeur_id_joueur_selected_dictionnaire = {"value_id_joueur_selected": id_joueur_sel}
                    strsql_joueurs_afficher = """SELECT ID_joueur, nom_joueur, prenom_joueur, date_de_naissance, taille_joueur, poids_joueur, type_de_poste FROM t_joueur WHERE ID_joueur = %(value_id_joueur_selected)s"""

                    mc_afficher.execute(strsql_joueurs_afficher, valeur_id_joueur_selected_dictionnaire)
                else:
                    strsql_joueurs_afficher = """SELECT ID_joueur, nom_joueur, prenom_joueur, date_de_naissance, taille_joueur, poids_joueur, type_de_poste FROM t_joueur ORDER BY ID_joueur DESC"""

                    mc_afficher.execute(strsql_joueurs_afficher)

                data_joueurs = mc_afficher.fetchall()

                print("data_joueurs ", data_joueurs, " Type : ", type(data_joueurs))

                # Différencier les messages si la table est vide.
                if not data_joueurs and id_joueur_sel == 0:
                    flash("""La table "t_joueur" est vide. !!""", "warning")
                elif not data_joueurs and id_joueur_sel > 0:
                    # Si l'utilisateur change l'id_genre dans l'URL et que le genre n'existe pas,
                    flash(f"Le joueur demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_genre" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données joueurs affichés !!", "success")

        except Exception as erreur:
            print(f"RGG Erreur générale. joueurs_afficher")
            # OM 2020.04.09 On dérive "Exception" par le "@obj_mon_application.errorhandler(404)"
            # fichier "run_mon_app.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            flash(f"RGG Exception {erreur} joueurs_afficher", "danger")
            raise Exception(f"RGG Erreur générale. {erreur}")
            # raise MaBdErreurOperation(f"RGG Exception {msg_erreurs['ErreurNomBD']['message']} {erreur}")

    # Envoie la page "HTML" au serveur.
    return render_template("joueurs/joueurs_afficher.html", data=data_joueurs)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /joueurs_ajouter

    Test : ex : http://127.0.0.1:5005/joueurs_ajouter

    Paramètres : sans

    But : Ajouter un joueur pour une equipe

    Remarque :  Dans le champ "name_joueur_html" du formulaire "joueurs/joueurs_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/joueurs_ajouter", methods=['GET', 'POST'])
def joueurs_ajouter_wtf():
    form = FormWTFAjouterJoueur()
    if request.method == "POST":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion joueurs ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur GestionJoueurs {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            if form.validate_on_submit():
                name_joueur_wtf = form.nom_joueur_wtf.data

                name_joueur = name_joueur_wtf.lower()
                valeurs_insertion_dictionnaire = {"value_nom_joueur": name_joueur}
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                strsql_insert_joueur = """INSERT INTO t_joueur (ID_joueur, nom_joueur) VALUES (NULL,%(value_nom_joueur)s)"""
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(strsql_insert_joueur, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('joueurs_afficher', order_by='DESC', id_joueur_sel=0))

        # ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except pymysql.err.IntegrityError as erreur_joueur_doublon:
            # Dérive "pymysql.err.IntegrityError" dans "MaBdErreurDoublon" fichier "erreurs/exceptions.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            code, msg = erreur_joueur_doublon.args

            flash(f"{error_codes.get(code, msg)} ", "warning")

        # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except (pymysql.err.OperationalError,
                pymysql.ProgrammingError,
                pymysql.InternalError,
                TypeError) as erreur_gest_joueur_crud:
            code, msg = erreur_gest_joueur_crud.args

            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Erreur dans Gestion joueurs CRUD : {sys.exc_info()[0]} "
                  f"{erreur_gest_joueur_crud.args[0]} , "
                  f"{erreur_gest_joueur_crud}", "danger")

    return render_template("joueurs/joueurs_ajouter_wtf.html", form=form)


"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /joueurs_update

    Test : ex cliquer sur le menu "joueurs" puis cliquer sur le bouton "EDIT" d'un "joueur"

    Paramètres : sans

    But : Editer(update) un joueur qui a été sélectionné dans le formulaire "joueurs_afficher.html"

    Remarque :  Dans le champ "nom_joueur_update_wtf" du formulaire "joueurs/joueur_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/joueurs_update", methods=['GET', 'POST'])
def joueurs_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "id_genre"
    id_joueur_update = request.values['id_joueur_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateJoueur()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            # Récupèrer la valeur du champ depuis "genre_update_wtf.html" après avoir cliqué sur "SUBMIT".
            # Puis la convertir en lettres minuscules.
            name_joueur_update = form_update.nom_joueur_update_wtf.data
            name_joueur_update = name_joueur_update.lower()

            valeur_update_dictionnaire = {"value_id_joueur": id_joueur_update, "value_name_joueur": name_joueur_update}
            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            str_sql_update_nom_joueur = """UPDATE t_joueur SET nom_joueur = %(value_name_joueur)s WHERE ID_joueur = %(value_id_joueur)s"""
            with MaBaseDeDonnee() as mconn_bd:
                mconn_bd.mabd_execute(str_sql_update_nom_joueur, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_genre_update"
            return redirect(url_for('joueurs_afficher', order_by="ASC", id_joueur_sel=id_joueur_update))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "id_genre" et "intitule_genre" de la "t_genre"
            str_sql_id_joueur = "SELECT ID_joueur, nom_joueur FROM t_joueur WHERE ID_joueur = %(value_id_joueur)s"
            valeur_select_dictionnaire = {"value_id_joueur": id_joueur_update}
            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()
            mybd_curseur.execute(str_sql_id_joueur, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom genre" pour l'UPDATE
            data_nom_joueur = mybd_curseur.fetchone()
            print("data_nom_joueur ", data_nom_joueur, " type ", type(data_nom_joueur), " joueur ",
                  data_nom_joueur["nom_joueur"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_update_wtf.html"
            form_update.nom_joueur_update_wtf.data = data_nom_joueur["nom_joueur"]

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans joueur_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans joueur_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_joueur_crud:
        code, msg = erreur_gest_joueur_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_joueur_crud} ", "danger")
        flash(f"Erreur dans joueur_update_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_joueur_crud.args[0]} , "
              f"{erreur_gest_joueur_crud}", "danger")
        flash(f"__KeyError dans joueur_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("joueurs/joueurs_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /joueurs_delete

    Test : ex. cliquer sur le menu "joueurs" puis cliquer sur le bouton "DELETE" d'un "joueur"

    Paramètres : sans

    But : Effacer(delete) un joueur qui a été sélectionné dans le formulaire "joueurs_afficher.html"

    Remarque :  Dans le champ "nom_joueur_delete_wtf" du formulaire "joueurs/joueurs_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@obj_mon_application.route("/joueurs_delete", methods=['GET', 'POST'])
def joueurs_delete_wtf():
    data_equipes_attribue_joueur_delete = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_genre"
    id_joueur_delete = request.values['id_joueur_btn_delete_html']

    # Objet formulaire pour effacer le genre sélectionné.
    form_delete = FormWTFDeleteJoueur()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("joueurs_afficher", order_by="ASC", id_joueur_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_equipes_attribue_joueur_delete = session['data_equipes_attribue_joueur_delete']
                print("data_equipes_attribue_joueur_delete ", data_equipes_attribue_joueur_delete)

                flash(f"Effacer le joueur de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer genre" qui va irrémédiablement EFFACER le genre
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_id_joueur": id_joueur_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_equipes_joueur = """DELETE FROM t_equipe_joueur WHERE fk_joueur = %(value_id_joueur)s"""
                str_sql_delete_idjoueur = """DELETE FROM t_joueur WHERE id_joueur = %(value_id_joueur)s"""
                # Manière brutale d'effacer d'abord la "fk_genre", même si elle n'existe pas dans la "t_genre_film"
                # Ensuite on peut effacer le genre vu qu'il n'est plus "lié" (INNODB) dans la "t_genre_film"
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(str_sql_delete_equipes_joueur, valeur_delete_dictionnaire)
                    mconn_bd.mabd_execute(str_sql_delete_idjoueur, valeur_delete_dictionnaire)

                flash(f"Joueur définitivement effacé !!", "success")
                print(f"Joueur définitivement effacé !!")

                # afficher les données
                return redirect(url_for('joueurs_afficher', order_by="ASC", id_joueur_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_id_joueur": id_joueur_delete}
            print(id_joueur_delete, type(id_joueur_delete))

            # Requête qui affiche tous les films_genres qui ont le genre que l'utilisateur veut effacer
            str_sql_joueurs_equipes_delete = """SELECT id_dfgd, nom_equipe, ID_joueur, nom_joueur FROM t_equipe_joueur 
                                            INNER JOIN t_equipe ON t_equipe_joueur.FK_equipe = t_equipe.ID_equipe
                                            INNER JOIN t_joueur ON t_equipe_joueur.FK_joueur = t_joueur.ID_joueur
                                            WHERE FK_joueur = %(value_id_joueur)s"""

            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()

            mybd_curseur.execute(str_sql_joueurs_equipes_delete, valeur_select_dictionnaire)
            data_equipes_attribue_joueur_delete = mybd_curseur.fetchall()
            print("data_equipes_attribue_joueur_delete...", data_equipes_attribue_joueur_delete)

            # Nécessaire pour mémoriser les données afin d'afficher à nouveau
            # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
            session['data_equipes_attribue_joueur_delete'] = data_equipes_attribue_joueur_delete

            # Opération sur la BD pour récupérer "id_genre" et "intitule_genre" de la "t_genre"
            str_sql_id_joueur = "SELECT ID_joueur, nom_joueur FROM t_joueur WHERE ID_joueur = %(value_id_joueur)s"

            mybd_curseur.execute(str_sql_id_joueur, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()",
            # vu qu'il n'y a qu'un seul champ "nom genre" pour l'action DELETE
            data_nom_joueur = mybd_curseur.fetchone()
            print("data_nom_joueur ", data_nom_joueur, " type ", type(data_nom_joueur), " joueur ",
                  data_nom_joueur["nom_joueur"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_delete_wtf.html"
            form_delete.nom_joueur_delete_wtf.data = data_nom_joueur["nom_joueur"]

            # Le bouton pour l'action "DELETE" dans le form. "genre_delete_wtf.html" est caché.
            btn_submit_del = False

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans joueurs_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans joueurs_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_joueur_crud:
        code, msg = erreur_gest_joueur_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_joueur_crud} ", "danger")

        flash(f"Erreur dans joueurs_delete_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_joueur_crud.args[0]} , "
              f"{erreur_gest_joueur_crud}", "danger")

        flash(f"__KeyError dans joueurs_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("joueurs/joueurs_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_equipes_associes=data_equipes_attribue_joueur_delete)
