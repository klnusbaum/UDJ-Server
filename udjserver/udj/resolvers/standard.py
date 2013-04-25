from udj.models import LibraryEntry
from django.db.models import Q

def search(query, library, player):
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library)
                              .filter(Q(title__icontains=query) |
                                      Q(artist__icontains=query) |
                                      Q(album__icontains=query))
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True))

def artists(library, player):
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library)
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True)
                              .distinct('artist')
                              .order_by('artist')
                              .values_list('artist', flat=True))

def getSongsForArtist(artist, library, player):
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library, artist__iexact=artist)
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True))

def randoms(library, player):
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library)
                              .exclude(id__in=bannedIds)
                              .exclude(is_deleted=True)
                              .order_by('?'))

