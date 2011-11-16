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
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QBuffer>
#include "UDJServerConnection.hpp"
#include "JSONHelper.hpp"
#include <QList>

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


void UDJServerConnection::addLibSongOnServer(
	const QString& songName,
	const QString& artistName,
	const QString& albumName,
	const library_song_id_t hostId)
{
  if(!isLoggedIn){
    return;
  }
  bool success = true;

  lib_song_t songToAdd = {songName, artistName, albumName};

  const QByteArray songJSON = JSONHelper::getJSONForLibAdd(
    songToAdd,
    hostId,
    success);
  QNetworkRequest addSongRequest(getLibAddSongUrl());
  addSongRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
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
 
void UDJServerConnection::recievedReply(QNetworkReply *reply){
  std::cout << QString(reply->readAll()).toStdString() << std::endl;
  if(reply->hasRawHeader("error")){
    std::cout << "Error: " << 
      QString(reply->rawHeader("error")).toStdString() << std::endl;
  }
  else if(reply->request().url().path() == getAuthUrl().path()){
    handleAuthReply(reply);
  }
  else if(reply->request().url().path() == getLibAddSongUrl().path()){
    handleAddSongReply(reply);
  }
  reply->deleteLater();
}

void UDJServerConnection::handleAuthReply(QNetworkReply* reply){
  if(
    reply->hasRawHeader(getTicketHeaderName()) &&
    reply->hasRawHeader(getUserIdHeaderName())
  ){
    setLoggedIn(
      reply->rawHeader(getTicketHeaderName()),
      reply->rawHeader(getUserIdHeaderName())
    );
    emit connectionEstablished();
  }
  else{
    emit unableToConnect("Bad username and password");
  }
}

void UDJServerConnection::setLoggedIn(QByteArray ticket, QByteArray userId){
  ticket_hash = ticket;
  user_id = QString(userId).toLong();
  timeTicketIssued = QDateTime::currentDateTime();
  isLoggedIn = true;
}

void UDJServerConnection::handleAddSongReply(QNetworkReply *reply){
  std::map<library_song_id_t, library_song_id_t> hostToServerIdMap =
    JSONHelper::getHostToServerLibIdMap(reply);
  emit serverIdsUpdate(hostToServerIdMap); 
}

void UDJServerConnection::createNewEvent(
  const QString& name,
  const QString& password,
  const QString& location)
{
  emit eventCreated();
}

QUrl UDJServerConnection::getLibAddSongUrl() const{
  return QUrl(getServerUrlPath() + "users/" + QString::number(user_id) +
    "/library/songs");
}


}//end namespace
