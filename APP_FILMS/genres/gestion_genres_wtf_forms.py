"""
    Fichier : gestion_genres_wtf_forms.py
    Auteur : OM 2021.03.22
    Gestion des formulaires avec WTF
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import Length
from wtforms.validators import Regexp


class FormWTFAjouterGenres(FlaskForm):
    """
        Dans le formulaire "genres_ajouter_wtf.html" on impose que le champ soit rempli.
        Définition d'un "bouton" submit avec un libellé personnalisé.
    """
    nom_equipe_regexp = "^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ]+$"
    nom_equipe_wtf = StringField("Clavioter le nom de l'équipe ",
                                 validators=[Length(min=2, max=20, message="min 2 max 20"),
                                             Regexp(nom_equipe_regexp,
                                                    message="Pas de chiffres, de caractères "
                                                            "spéciaux, "
                                                            "d'espace à double, de double "
                                                            "apostrophe, de double trait union")
                                             ])
    nom_president_equipe_regexp = "^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ]+$"
    nom_president_equipe_wtf = StringField("Clavioter le nom du president de l'équipe ",
                                           validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                       Regexp(nom_president_equipe_regexp,
                                                              message="Pas de chiffres, de caractères "
                                                                      "spéciaux, "
                                                                      "d'espace à double, de double "
                                                                      "apostrophe, de double trait union")
                                                       ])

    nom_entraineur_equipe_regexp = "^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ]+$"
    nom_entraineur_equipe_wtf = StringField("Clavioter le nom de l'entraîneur de l'équipe",
                                            validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                        Regexp(nom_entraineur_equipe_regexp,
                                                               message="Pas de chiffres, de caractères "
                                                                       "spéciaux, "
                                                                       "d'espace à double, de double "
                                                                       "apostrophe, de double trait union")
                                                        ])
    submit = SubmitField("Enregistrer equipe")


class FormWTFUpdateGenre(FlaskForm):
    """
        Dans le formulaire "genre_update_wtf.html" on impose que le champ soit rempli.
        Définition d'un "bouton" submit avec un libellé personnalisé.
    """
    nom_equipe_regexp = "^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ]+$"
    nom_equipe_update_wtf = StringField("Clavioter le nom de l'équipe ",
                                        validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                    Regexp(nom_equipe_regexp,
                                                           message="pas d'espace")
                                                    ])
    nom_president_equipe_regexp = "^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ]+$"
    nom_president_equipe_update_wtf = StringField("Clavioter le nom du president de l'équipe ",
                                                  validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                              Regexp(nom_president_equipe_regexp,
                                                                     message="pas d'espace")
                                                              ])
    nom_entraineur_equipe_regexp = "^([A-Z]|[a-zÀ-ÖØ-öø-ÿ])[A-Za-zÀ-ÖØ-öø-ÿ]*['\- ]?[A-Za-zÀ-ÖØ-öø-ÿ]+$"
    nom_entraineur_equipe_update_wtf = StringField("Clavioter le nom de l'entraîneur de l'équipe ",
                                                   validators=[Length(min=2, max=20, message="min 2 max 20"),
                                                               Regexp(nom_entraineur_equipe_regexp,
                                                                      message="pas d'espace")
                                                               ])

    submit = SubmitField("Update equipe")


class FormWTFDeleteGenre(FlaskForm):
    """
        Dans le formulaire "genre_delete_wtf.html"

        nom_genre_delete_wtf : Champ qui reçoit la valeur du genre, lecture seule. (readonly=true)
        submit_btn_del : Bouton d'effacement "DEFINITIF".
        submit_btn_conf_del : Bouton de confirmation pour effacer un "genre".
        submit_btn_annuler : Bouton qui permet d'afficher la table "t_genre".
    """
    nom_equipe_delete_wtf = StringField("Effacer cette equipe")
    submit_btn_del = SubmitField("Effacer equipe")
    submit_btn_conf_del = SubmitField("Etes-vous sur d'effacer ?")
    submit_btn_annuler = SubmitField("Annuler")
