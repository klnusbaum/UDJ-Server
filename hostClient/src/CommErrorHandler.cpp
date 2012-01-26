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
    SIGNAL(libSongAddFailed(CommErrorType)),
    this,
    SLOT(handleLibSongAddError(CommErrorType)));
} 

void CommErrorHandler::handleLibSongAddError(CommErrorType errorType){
  if(errorType == AUTH){
    syncLibOnReauth = true;
    requestReauth();
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
}


}
