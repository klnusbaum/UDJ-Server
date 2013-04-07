from udj.resolvers.query import getBannedIds
from udj.models import LibraryEntry
from django.db.models import Q

def search(query, library, player):
  bannedIds = library.getBannedIds(player)
  return (LibraryEntry.objects.filter(library=library)
                              .filter(Q(title__icontains=query) |
                                      Q(artist__icontains=query) |
                                      Q(album__icontains=query))
                              .exclude(id__in=bannedIds))
