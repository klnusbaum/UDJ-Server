/**
 * Copyright 2011 Kurtis L. Nusbaum
 *
 * This file is part of UDJ.
 *
 * UDJ is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * UDJ is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with UDJ.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "CommErrorHandler.hpp"
#include "DataStore.hpp"
#include "UDJServerConnection.hpp"

namespace UDJ{

CommErrorHandler::CommErrorHandler(
  DataStore *dataStore, 
  UDJServerConnection *serverConnection)
  :QObject(dataStore),
  dataStore(dataStore),
  serverConnection(serverConnection),
  syncLibOnReauth(false)
{
  connect(
    serverConnection,
    SIGNAL(authenticated(const QByteArray&, const user_id_t&)),
    this,
    SLOT(onAuthenticated(const QByteArray&, const user_id_t&)));

  connect(
    serverConnection,
    SIGNAL(authFailed(const QString)),
    this,
    SIGNAL(hardAuthFailure(const QString)));

  connect(
    serverConnection,
    SIGNAL(commError(
      CommErrorHandler::OperationType,
      CommErrorHandler::CommErrorType,
      const QByteArray&)),
    this,
    SLOT(handleCommError(
      CommErrorHandler::OperationType,
      CommErrorHandler::CommErrorType,
      const QByteArray&)));
} 

void CommErrorHandler::handleCommError(
  CommErrorHandler::OperationType opType,
  CommErrorHandler::CommErrorType errorType,
  const QByteArray& payload)
{
  DEBUG_MESSAGE("Handling error of type " << errorType << " for op type " <<
    opType);
  if(errorType == CommErrorHandler::AUTH){
    if(opType == LIB_SONG_ADD || opType == LIB_SONG_DELETE){
      syncLibOnReauth = true;
    }
    else if(opType == CREATE_EVENT){
      createEventPayload = payload;
      createEventOnReauth = true;
    }
    else if(opType == END_EVENT){
      endEventOnReauth = true;
    }
    else if(opType == AVAILABLE_SONG_ADD || opType == AVAILABLE_SONG_DEL){
      syncAvailableMusicOnReauth = true;
    }
    else if(opType == PLAYLIST_UPDATE){
      refreshActivePlaylistOnReauth = true;
    }
    else if(opType == PLAYLIST_ADD){
      syncPlaylistAddRequestsOnReauth = true;
    }
    else if(opType == SET_CURRENT_SONG){
      setCurrentSongPayload = payload;
      setCurrentSongOnReauth = true;
    }
    else if(opType == PLAYLIST_REMOVE){
      syncPlaylistRemoveRequestsOnReauth = true;
    }
    requestReauth();
  }
  else if(errorType == CONFLICT){
    if(opType == CREATE_EVENT){
      //TODO handle this error
    }
  }
  else if(errorType == UNKNOWN_ERROR || errorType == SERVER_ERROR){
    if(opType == CREATE_EVENT){
      emit eventCreationFailed(tr("We're currently experiencing technical "
        "difficulties. Please try again in a minute."));
    }
  }
}

void CommErrorHandler::requestReauth(){
  if(!hasPendingReauthRequest){
    hasPendingReauthRequest = true;
    serverConnection->authenticate(
      dataStore->getUsername(),
      dataStore->getPassword());
  }
}

void CommErrorHandler::onAuthenticated(
  const QByteArray& ticket,
  const user_id_t& user_id)
{
  serverConnection->setTicket(ticket);
  serverConnection->setUserId(user_id);
  hasPendingReauthRequest = false;
  clearOnReauthFlags();
}

void CommErrorHandler::clearOnReauthFlags(){
  if(syncLibOnReauth){
    dataStore->syncLibrary();
    syncLibOnReauth=false;
  }
  if(createEventOnReauth){
    serverConnection->createEvent(createEventPayload);
    createEventOnReauth=false;
  }
  if(endEventOnReauth){
    dataStore->endEvent();
    endEventOnReauth=false;
  }
  if(syncAvailableMusicOnReauth){
    dataStore->syncAvailableMusic();
    syncAvailableMusicOnReauth=false;
  }
  if(refreshActivePlaylistOnReauth){
    serverConnection->getActivePlaylist();
    refreshActivePlaylistOnReauth=false;
  }
  if(syncPlaylistAddRequestsOnReauth){
    dataStore->syncPlaylistAddRequests();
    syncPlaylistAddRequestsOnReauth=false;
  }
  if(setCurrentSongOnReauth){
    serverConnection->setCurrentSong(setCurrentSongPayload);
    setCurrentSongOnReauth=false;
  }
  if(syncPlaylistRemoveRequestsOnReauth){
    dataStore->syncPlaylistRemoveRequests();
    syncPlaylistRemoveRequestsOnReauth=false;
  }
  if(refreshActivePlaylistOnReauth){
    serverConnection->getEventGoers();
    refreshActivePlaylistOnReauth=false;
  }
}

void CommErrorHandler::onHardAuthFailure(const QString errMessage){
  emit hardAuthFailure(errMessage);

  if(syncLibOnReauth){
    emit libSyncError(errMessage);
  }
  if(createEventOnReauth){
    emit eventCreationFailed(errMessage);
  }
  if(endEventOnReauth){
    emit eventEndingFailed(errMessage);
  }
  if(syncAvailableMusicOnReauth){
    emit availableMusicSyncError(errMessage);
  }
  if(refreshActivePlaylistOnReauth){
    emit refreshActivePlaylistError(errMessage);
  }
  if(syncPlaylistAddRequestsOnReauth){
    emit playlistAddRequestError(errMessage);
  }
  if(setCurrentSongOnReauth){
    emit setCurrentSongError(errMessage);
  }
  if(syncPlaylistRemoveRequestsOnReauth){
    emit playlistRemoveRequestError(errMessage);
  }
}


}
