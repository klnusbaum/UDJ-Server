from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER, FORBIDDEN_REASON_HEADER

from udj.views.views06.decorators import PlayerExists, PlayerIsActive, AcceptsMethods
from udj.views.views06.authdecorators import NeedsAuth
from udj.views.views06.auth import getUserForTicket

from django.http import HttpResponseForbidden

@csrf_exempt
@AcceptsMethods(['PUT'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
def participateWithPlayer(request, player_id, activePlayer):


  def onSuccessfulPlayerAuth(activePlayer, user):
    #very important to check if they're banned or player is full first.
    #otherwise we might might mark them as actually participating
    if activePlayer.isUserBanned(user):
      toReturn = HttpResponseForbidden()
      toReturn['FORBIDDEN_REASON_HEADER'] = 'banned'
    if activePlayer.isFull():
      toReturn = HttpResponseForbidden()
      toReturn['FORBIDDEN_REASON_HEADER'] = 'player-full'

    obj, created = Participant.objects.get_or_create(player=activePlayer, user=user)
    if not created:
      obj.time_last_interation = datetime.now()
      obj.kick_flag = False
      obj.save()

    return HttpResponse(status=201)


  user = getUserForTicket(request)
  playerPassword = PlayerPassword.objects.filter(player=activePlayer)
  if playerPassword.exists():
    if DJANGO_PLAYER_PASSWORD_HEADER in request.META:
      hashedPassword = hashPlayerPassword(request.META[DJANGO_PLAYER_PASSWORD_HEADER])
      if hashedPassword == playerPassword[0].password_hash:
        return onSuccessfulPlayerAuth(activePlayer, user)

    toReturn = HttpResponse(status=401)
    toReturn['WWW-Authenticate'] = 'player-password'
    return toReturn
  else:
    return onSuccessfulPlayerAuth(activePlayer, user)

