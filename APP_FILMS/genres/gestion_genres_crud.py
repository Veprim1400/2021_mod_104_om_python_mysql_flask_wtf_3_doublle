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
from APP_FILMS.genres.gestion_genres_wtf_forms import FormWTFAjouterGenres
from APP_FILMS.genres.gestion_genres_wtf_forms import FormWTFDeleteGenre
from APP_FILMS.genres.gestion_genres_wtf_forms import FormWTFUpdateGenre

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /genres_afficher
    
    Test : ex : http://127.0.0.1:5005/genres_afficher
    
    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                id_genre_sel = 0 >> tous les genres.
                id_genre_sel = "n" affiche le genre dont l'id est "n"
"""


@obj_mon_application.route("/genres_afficher/<string:order_by>/<int:id_genre_sel>", methods=['GET', 'POST'])
def genres_afficher(order_by, id_genre_sel):
    if request.method == "GET":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion genres ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur GestionGenres {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            with MaBaseDeDonnee().connexion_bd.cursor() as mc_afficher:
                if order_by == "ASC" and id_genre_sel == 0:
                    strsql_genres_afficher = """SELECT ID_equipe, nom_equipe, nom_president_equipe, nom_entraineur_equipe FROM t_equipe ORDER BY ID_equipe ASC"""
                    mc_afficher.execute(strsql_genres_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_equipe"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du genre sélectionné avec un nom de variable
                    valeur_id_genre_selected_dictionnaire = {"value_id_genre_selected": id_genre_sel}
                    strsql_genres_afficher = """SELECT ID_equipe, nom_equipe,nom_president_equipe, nom_entraineur_equipe FROM t_equipe WHERE ID_equipe = %(value_id_genre_selected)s"""

                    mc_afficher.execute(strsql_genres_afficher, valeur_id_genre_selected_dictionnaire)
                else:
                    strsql_genres_afficher = """SELECT ID_equipe, nom_equipe, nom_president_equipe, nom_entraineur_equipe FROM t_equipe ORDER BY ID_equipe DESC"""

                    mc_afficher.execute(strsql_genres_afficher)

                data_genres = mc_afficher.fetchall()

                print("data_genres ", data_genres, " Type : ", type(data_genres))

                # Différencier les messages si la table est vide.
                if not data_genres and id_genre_sel == 0:
                    flash("""La table "t_equipe" est vide. !!""", "warning")
                elif not data_genres and id_genre_sel > 0:
                    # Si l'utilisateur change l'id_genre dans l'URL et que le genre n'existe pas,
                    flash(f"Le genre demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "t_equipe" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données equipes affichés !!", "success")

        except Exception as erreur:
            print(f"RGG Erreur générale. genres_afficher")
            # OM 2020.04.09 On dérive "Exception" par le "@obj_mon_application.errorhandler(404)"
            # fichier "run_mon_app.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            flash(f"RGG Exception {erreur} genres_afficher", "danger")
            raise Exception(f"RGG Erreur générale. {erreur}")
            # raise MaBdErreurOperation(f"RGG Exception {msg_erreurs['ErreurNomBD']['message']} {erreur}")

    # Envoie la page "HTML" au serveur.
    return render_template("genres/genres_afficher.html", data=data_genres)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /genres_ajouter
    
    Test : ex : http://127.0.0.1:5005/genres_ajouter
    
    Paramètres : sans
    
    But : Ajouter un genre pour un film
    
    Remarque :  Dans le champ "name_genre_html" du formulaire "genres/genres_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/genres_ajouter", methods=['GET', 'POST'])
def genres_ajouter_wtf():
    form = FormWTFAjouterGenres()
    if request.method == "POST":
        try:
            try:
                # Renvoie une erreur si la connexion est perdue.
                MaBaseDeDonnee().connexion_bd.ping(False)
            except Exception as erreur:
                flash(f"Dans Gestion equipes ...terrible erreur, il faut connecter une base de donnée", "danger")
                print(f"Exception grave Classe constructeur GestionEquipes {erreur.args[0]}")
                raise MaBdErreurConnexion(f"{msg_erreurs['ErreurConnexionBD']['message']} {erreur.args[0]}")

            if form.validate_on_submit():
                name_equipe_wtf = form.nom_equipe_wtf.data
                name_president_wtf = form.nom_president_equipe_wtf.data
                name_entraineur_wtf = form.nom_entraineur_equipe_wtf.data

                name_equipe = name_equipe_wtf.lower()
                name_president = name_president_wtf.lower()
                name_entraineur = name_entraineur_wtf.lower()
                valeurs_insertion_dictionnaire = {"value_nom_equipe": name_equipe,"value_nom_president": name_president,"value_nom_entraineur": name_entraineur}
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                strsql_insert_equipe = """INSERT INTO t_equipe (ID_equipe, nom_equipe, nom_president_equipe, nom_entraineur_equipe) VALUES (NULL,%(value_nom_equipe)s,%(value_nom_president)s,%(value_nom_entraineur)s)"""
                with MaBaseDeDonnee() as mconn_bd:
                    mconn_bd.mabd_execute(strsql_insert_equipe, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('genres_afficher', order_by='DESC', id_genre_sel=0))

        # ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except pymysql.err.IntegrityError as erreur_genre_doublon:
            # Dérive "pymysql.err.IntegrityError" dans "MaBdErreurDoublon" fichier "erreurs/exceptions.py"
            # Ainsi on peut avoir un message d'erreur personnalisé.
            code, msg = erreur_genre_doublon.args

            flash(f"{error_codes.get(code, msg)} ", "warning")

        # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
        except (pymysql.err.OperationalError,
                pymysql.ProgrammingError,
                pymysql.InternalError,
                TypeError) as erreur_gest_genr_crud:
            code, msg = erreur_gest_genr_crud.args

            flash(f"{error_codes.get(code, msg)} ", "danger")
            flash(f"Erreur dans Gestion genres CRUD : {sys.exc_info()[0]} "
                  f"{erreur_gest_genr_crud.args[0]} , "
                  f"{erreur_gest_genr_crud}", "danger")

    return render_template("genres/genres_ajouter_wtf.html", form=form)


"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /genre_update
    
    Test : ex cliquer sur le menu "genres" puis cliquer sur le bouton "EDIT" d'un "genre"
    
    Paramètres : sans
    
    But : Editer(update) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_update_wtf" du formulaire "genres/genre_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@obj_mon_application.route("/genre_update", methods=['GET', 'POST'])
def genre_update_wtf():

    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "ID_equipe"
    ID_equipe_update = request.values['ID_equipe_btn_edit_html']
    print(ID_equipe_update)

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateGenre()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            # Récupèrer la valeur du champ depuis "genre_update_wtf.html" après avoir cliqué sur "SUBMIT".
            # Puis la convertir en lettres minuscules.
            nom_equipe_update = form_update.nom_equipe_update_wtf.data
            nom_president_equipe_update = form_update.nom_president_equipe_update_wtf.data
            nom_entraineur_equipe_update = form_update.nom_entraineur_equipe_update_wtf.data

            nom_equipe_update = nom_equipe_update.lower()
            nom_president_equipe_update = nom_president_equipe_update.lower()
            nom_entraineur_equipe_update = nom_entraineur_equipe_update.lower()

            valeur_update_dictionnaire = {"value_ID_equipe": ID_equipe_update, "value_nom_equipe": nom_equipe_update,"value_nom_president": nom_president_equipe_update,"value_nom_entraineur": nom_entraineur_equipe_update }
            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            str_sql_update_equipe = """UPDATE t_equipe SET nom_equipe = %(value_nom_equipe)s, nom_president_equipe = %(value_nom_president)s, nom_entraineur_equipe = %(value_nom_entraineur)s WHERE ID_equipe = %(value_ID_equipe)s"""
            with MaBaseDeDonnee() as mconn_bd:
                mconn_bd.mabd_execute(str_sql_update_equipe, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_genre_update"
            return redirect(url_for('genres_afficher', order_by="ASC", id_genre_sel=ID_equipe_update))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "id_genre" et "nom_equipe" de la "t_equipe"
            str_sql_id_genre = "SELECT * FROM t_equipe WHERE ID_equipe = %(value_ID_equipe)s"
            valeur_select_dictionnaire = {"value_ID_equipe": ID_equipe_update}
            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()
            mybd_curseur.execute(str_sql_id_genre, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom genre" pour l'UPDATE
            data_nom_genre = mybd_curseur.fetchone()
            print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                  data_nom_genre["nom_equipe"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_update_wtf.html"
            form_update.nom_equipe_update_wtf.data = data_nom_genre["nom_equipe"]
            form_update.nom_president_equipe_update_wtf.data = data_nom_genre["nom_president_equipe"]
            form_update.nom_entraineur_equipe_update_wtf.data = data_nom_genre["nom_entraineur_equipe"]

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans genre_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans genre_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")
        flash(f"Erreur dans genre_update_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")
        flash(f"__KeyError dans genre_update_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("genres/genre_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /genre_delete
    
    Test : ex. cliquer sur le menu "genres" puis cliquer sur le bouton "DELETE" d'un "genre"
    
    Paramètres : sans
    
    But : Effacer(delete) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_delete_wtf" du formulaire "genres/genre_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@obj_mon_application.route("/genre_delete", methods=['GET', 'POST'])
def genre_delete_wtf():
    data_films_attribue_genre_delete = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_genre"
    ID_equipe_delete = request.values['ID_equipe_btn_delete_html']

    # Objet formulaire pour effacer le genre sélectionné.
    form_delete = FormWTFDeleteGenre()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("genres_afficher", order_by="ASC", id_genre_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_films_attribue_genre_delete = session['data_films_attribue_genre_delete']
                print("data_films_attribue_genre_delete ", data_films_attribue_genre_delete)

                flash(f"Effacer l' équipe de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer genre" qui va irrémédiablement EFFACER le genre
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_ID_equipe": ID_equipe_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_films_genre = """DELETE FROM t_equipe_joueur WHERE FK_equipe = %(value_ID_equipe)s"""
                str_sql_delete_idgenre = """DELETE FROM t_equipe WHERE ID_equipe = %(value_ID_equipe)s"""

                # Manière brutale d'effacer d'abord la "FK_joueur", même si elle n'existe pas dans la "t_equipe_film"
                # Ensuite on peut effacer le genre vu qu'il n'est plus "lié" (INNODB) dans la "t_equipe_film"
                with MaBaseDeDonnee() as mconn_bd:
                    #mconn_bd.mabd_execute(str_sql_delete_films_genre, valeur_delete_dictionnaire)
                    mconn_bd.mabd_execute(str_sql_delete_films_genre, valeur_delete_dictionnaire)
                    mconn_bd.mabd_execute(str_sql_delete_idgenre, valeur_delete_dictionnaire)

                flash(f"Equipe définitivement effacée !!", "success")
                print(f"Equipe définitivement effacée !!")

                # afficher les données
                return redirect(url_for('genres_afficher', order_by="ASC", id_genre_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_ID_equipe": ID_equipe_delete}
            print(ID_equipe_delete, type(ID_equipe_delete))

            # Requête qui affiche tous les films qui ont le genre que l'utilisateur veut effacer
            str_sql_genres_films_delete = """SELECT id_dfgd, nom_joueur, ID_equipe, nom_equipe FROM t_equipe_joueur
                                            INNER JOIN t_joueur ON t_equipe_joueur.FK_joueur = t_joueur.ID_joueur
                                            INNER JOIN t_equipe ON t_equipe_joueur.FK_equipe = t_equipe.ID_equipe
                                            WHERE FK_equipe = %(value_ID_equipe)s"""

            mybd_curseur = MaBaseDeDonnee().connexion_bd.cursor()

            mybd_curseur.execute(str_sql_genres_films_delete, valeur_select_dictionnaire)
            data_films_attribue_genre_delete = mybd_curseur.fetchall()
            print("data_films_attribue_genre_delete...", data_films_attribue_genre_delete)

            # Nécessaire pour mémoriser les données afin d'afficher à nouveau
            # le formulaire "genres/genre_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
            session['data_films_attribue_genre_delete'] = data_films_attribue_genre_delete

            # Opération sur la BD pour récupérer "id_genre" et "nom_equipe" de la "t_equipe"
            str_sql_ID_equipe = "SELECT * FROM t_equipe WHERE ID_equipe = %(value_ID_equipe)s"

            mybd_curseur.execute(str_sql_ID_equipe, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()",
            # vu qu'il n'y a qu'un seul champ "nom genre" pour l'action DELETE
            data_nom_genre = mybd_curseur.fetchone()
            print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                  data_nom_genre["nom_equipe"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "genre_delete_wtf.html"
            form_delete.nom_equipe_delete_wtf.data = data_nom_genre["nom_equipe"]

            # Le bouton pour l'action "DELETE" dans le form. "genre_delete_wtf.html" est caché.
            btn_submit_del = False

    # OM 2020.04.16 ATTENTION à l'ordre des excepts, il est très important de respecter l'ordre.
    except KeyError:
        flash(f"__KeyError dans genre_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")
    except ValueError:
        flash(f"Erreur dans genre_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]}", "danger")
    except (pymysql.err.OperationalError,
            pymysql.ProgrammingError,
            pymysql.InternalError,
            pymysql.err.IntegrityError,
            TypeError) as erreur_gest_genr_crud:
        code, msg = erreur_gest_genr_crud.args
        flash(f"attention : {error_codes.get(code, msg)} {erreur_gest_genr_crud} ", "danger")

        flash(f"Erreur dans genre_delete_wtf : {sys.exc_info()[0]} "
              f"{erreur_gest_genr_crud.args[0]} , "
              f"{erreur_gest_genr_crud}", "danger")

        flash(f"__KeyError dans genre_delete_wtf : {sys.exc_info()[0]} {sys.exc_info()[1]} {sys.exc_info()[2]}",
              "danger")

    return render_template("genres/genre_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_films_associes=data_films_attribue_genre_delete)
