from .models import Sujet
from statistiques.models import FicheStatistique, NSP


def merge_stats(main, merged):
    """ Merge stats of two sujets according to priority order : main, then merged """

    # Première rencontre : retenir la plus ancienne
    if merged.premiere_rencontre:
        if not main.premiere_rencontre or main.premiere_rencontre > merged.premiere_rencontre:
            main.premiere_rencontre = merged.premiere_rencontre

    # NullBoolean and Nullable ('age') fields
    for field in ('age', 'prob_psychiatrie', 'prob_somatique',
                  'prob_administratif', 'prob_addiction',
                  'connu_siao', 'lien_familial'):
        if not getattr(main, field): # Ignore if already filled
            setattr(main, field, getattr(merged, field))

    # Choice fields, None is NSP
    for field in ('habitation', 'ressources', 'parcours_de_vie'):
        if getattr(main, field) == NSP: # Ignore if already filled
            setattr(main, field, getattr(merged, field))

def merge_two(main, merged):
    """ Merge 'merged' sujet into 'main' one """

    # Merge statistics and informations
    merge_stats(main, merged)

    # Move all notes
    for note in merged.sujet.notes.all():
        note.sujet = main.sujet
        note.save()

    # Save main and delete the other one
    print('ACTIONS: merged %s into %s' % (main, merged))
    main.save()
    merged.delete()
