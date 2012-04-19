from django.db.models import Sum

def totalVotes(queuedEntries):
  return queuedEntries.annotate(totalvotes=Sum('vote__weight')).order_by('-totalvotes','time_added')
