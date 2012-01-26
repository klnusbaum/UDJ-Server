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
  establishAuthConnections();
  establishErrorConnections();
} 

void CommErrorHandler::establishAuthConnections(){
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
}

void CommErrorHandler::establishErrorConnections(){
  connect(
    serverConnection,
    SIGNAL(libSongAddFailed(CommErrorHandler::CommErrorType)),
    this,
    SLOT(handleLibSyncError(CommErrorHandler::CommErrorType)));

  connect(
    serverConnection,
    SIGNAL(libSongDeleteFailed(CommErrorHandler::CommErrorType)),
    this,
    SLOT(handleLibSyncError(CommErrorHandler::CommErrorType)));

  connect(
    serverConnection,
    SIGNAL(eventCreationFailed(
      CommErrorHandler::CommErrorType, const QByteArray&)),
    this,
    SLOT(handleCreateEventError(
      CommErrorHandler::CommErrorType, const QByteArray&)));

}

void CommErrorHandler::handleLibSyncError(
  CommErrorHandler::CommErrorType errorType)
{
  switch(errorType){
    case AUTH:
      syncLibOnReauth = true;
      requestReauth();
      break;
    case UNKNOWN_ERROR:
      //TODO handle this error
      break;
  }
}

void CommErrorHandler::handleCreateEventError(
  CommErrorHandler::CommErrorType errorType,
  const QByteArray& payload)
{
  switch(errorType){
    case AUTH:
      createEventOnReauth = true;
      createEventPayload = payload;
      requestReauth();
      break;
    case CONFLICT:
      //TODO handle this error
      break;
    case UNKNOWN_ERROR:
      emit eventCreationFailed(tr("We're currently experiencing technical "
        "difficulties. Please try again in a minute."));
      break;
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
  hasPendingReauthRequest = false;
  serverConnection->setTicket(ticket);
  serverConnection->setUserId(user_id);
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
}


}
