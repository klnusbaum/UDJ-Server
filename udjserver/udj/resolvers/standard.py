def search(query, library, player):
  lib = Library.objects.get(pk=library_id)
    banned_entries = (BannedLibraryEntry.objects.filter(player=self)
                      .values_list('song__id', flat=True))
