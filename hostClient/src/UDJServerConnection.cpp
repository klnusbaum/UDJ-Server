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
#include <QNetworkAccessManager>
#include <QNetworkCookieJar>
#include <QNetworkReply>
#include <QBuffer>
#include "UDJServerConnection.hpp"
#include "JSONHelper.hpp"

namespace UDJ{

UDJServerConnection::UDJServerConnection(QObject *parent):QObject(parent),
  isLoggedIn(false)
{
  netAccessManager = new QNetworkAccessManager(this);
  connect(netAccessManager, SIGNAL(finished(QNetworkReply*)),
    this, SLOT(recievedReply(QNetworkReply*)));
}

void UDJServerConnection::startConnection(
  const QString& username,
  const QString& password
)
{
  authenticate(username, password);
}

void UDJServerConnection::prepareJSONRequest(QNetworkRequest &request){
  request.setHeader(QNetworkRequest::ContentTypeHeader, "text/json");
  request.setRawHeader(getTicketHeaderName(), ticket_hash);
  
}

void UDJServerConnection::addLibSongOnServer(
	const QString& songName,
	const QString& artistName,
	const QString& albumName,
  const int duration,
	const library_song_id_t hostId)
{
  if(!isLoggedIn){
    return;
  }
  bool success = true;

  lib_song_t songToAdd = {hostId, songName, artistName, albumName, duration};

  const QByteArray songJSON = JSONHelper::getJSONForLibAdd(
    songToAdd,
    success);
  QNetworkRequest addSongRequest(getLibAddSongUrl());
  prepareJSONRequest(addSongRequest);
  netAccessManager->put(addSongRequest, songJSON);
}

void UDJServerConnection::authenticate(
  const QString& username, 
  const QString& password)
{
  QNetworkRequest authRequest(getAuthUrl());
  authRequest.setRawHeader(
    getAPIVersionHeaderName(),
    getAPIVersion());
  QString data("username="+username+"&password="+password);
  QBuffer *dataBuffer = new QBuffer();
  dataBuffer->setData(data.toUtf8());
  QNetworkReply *reply = netAccessManager->post(authRequest, dataBuffer);
  dataBuffer->setParent(reply);
}
 
void UDJServerConnection::createEvent(
  const QString& partyName,
  const QString& password)
{
  QNetworkRequest createEventRequest(getCreateEventUrl());
  prepareJSONRequest(createEventRequest);
  const QByteArray partyJSON = JSONHelper::getCreateEventJSON(
    partyName, password);
  netAccessManager->put(createEventRequest, partyJSON);
}


void UDJServerConnection::recievedReply(QNetworkReply *reply){
  if(reply->request().url().path() == getAuthUrl().path()){
    handleAuthReply(reply);
  }
  else if(reply->request().url().path() == getLibAddSongUrl().path()){
    handleAddSongReply(reply);
  }
  else if(reply->request().url().path() == getCreateEventUrl().path()){
    handleCreateEventReply(reply);
  }
  reply->deleteLater();
}

void UDJServerConnection::handleAuthReply(QNetworkReply* reply){
  if(
    reply->error() == QNetworkReply::NoError &&
    reply->hasRawHeader(getTicketHeaderName()) &&
    reply->hasRawHeader(getUserIdHeaderName()))
  {
    setLoggedIn(
      reply->rawHeader(getTicketHeaderName()),
      reply->rawHeader(getUserIdHeaderName())
    );
    emit connectionEstablished();
  }
  else{
    QString error = tr("Unable to connect to server: error ") + 
     QString::number(reply->error());
    emit unableToConnect(error);
  }
}

void UDJServerConnection::setLoggedIn(QByteArray ticket, QByteArray userId){
  ticket_hash = ticket;
  user_id = QString(userId).toLong();
  timeTicketIssued = QDateTime::currentDateTime();
  isLoggedIn = true;
}

void UDJServerConnection::handleAddSongReply(QNetworkReply *reply){
  std::vector<library_song_id_t> updatedIds =   
    JSONHelper::getUpdatedLibIds(reply);
  emit songsAddedOnServer(updatedIds);
}

void UDJServerConnection::handleCreateEventReply(QNetworkReply *reply){
  if(reply->error() != QNetworkReply::NoError){
    emit eventCreationFailed("Failed to create event");
    return;
  }
  //TODO handle bad json resturned from the server.
  isHostingEvent =true;
  eventId = JSONHelper::getEventId(reply);
  emit eventCreated();
}

QUrl UDJServerConnection::getLibAddSongUrl() const{
  return QUrl(getServerUrlPath() + "users/" + QString::number(user_id) +
    "/library/songs");
}

QUrl UDJServerConnection::getLibDeleteAllUrl() const{
  return QUrl(getServerUrlPath() + "users/" + QString::number(user_id) +
    "/library");
}

void UDJServerConnection::clearMyLibrary(){


}


}//end namespace
