from statistiques.models import NSP


def merge_stats(main, merged):
    """ Merge stats of two sujets according to priority order : main, then merged """
    # TODO: replace hardcoded field names with more flexible getters

    # Fields of 'Sujet' model
    for field in ('nom', 'prenom', 'surnom', 'age',):
        if not getattr(main, field):
            setattr(main, field, getattr(merged, field, None))

    # Première rencontre : retenir la plus ancienne
    if merged.premiere_rencontre:
        if not main.premiere_rencontre or main.premiere_rencontre > merged.premiere_rencontre:
            main.premiere_rencontre = merged.premiere_rencontre

    # Fields of 'FicheStatistique' model
    # NullBoolean fields
    for field in ('prob_psychiatrie', 'prob_somatique',
                  'prob_administratif', 'prob_addiction',
                  'connu_siao', 'lien_familial'):
        if not getattr(main.statistiques, field):  # Ignore if already filled
            setattr(main.statistiques, field, getattr(merged.statistiques, field, None))
    # Choice fields, None is NSP
    for field in ('habitation', 'ressources', 'parcours_de_vie'):
        if getattr(main.statistiques, field) == NSP:  # Ignore if already filled
            setattr(main.statistiques, field, getattr(merged.statistiques, field, NSP))


def merge_two(main, merged):
    """ Merge 'merged' sujet into 'main' one """
    merge_stats(main, merged)  # Merge statistics and informations
    for note in merged.notes.all():  # Move all notes
        note.sujet = main
        note.save()
    main.save()
    merged.delete()
