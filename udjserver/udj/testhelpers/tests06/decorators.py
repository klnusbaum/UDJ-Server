from django.contrib.auth.models import User
from udj.models import Participant

def EnsureParticipationUpdated(user_id, player_id):
  def decorator(target):
    def wrapper(*args, **kwargs):
      participant = Participant.objects.get(user__id=user_id, player__id=player_id)
      oldTime = participant.time_last_interaction
      target(*args, **kwargs)
      newTime = Participant.objects.get(user__id=user_id, player__id=player_id).time_last_interaction
      (args[0]).assertTrue(newTime > oldTime)
    return wrapper
  return decorator


