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

namespace UDJ{

UDJServerConnection::UDJServerConnection(QObject *parent):QObject(parent),
  isLoggedIn(false)
{
  netAccessManager = new QNetworkAccessManager(this);
  cookieJar = netAccessManager->cookieJar();
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
	const libraryid_t hostId)
{
  if(!isLoggedIn){
    return;
  }
  bool success = true;

  const QByteArray songJSON = JSONHelper::getLibraryEntryJSON(
    songName, 
    artistName,
    albumName,
    hostId,
    false, 
    success);
  const QByteArray finalData = "to_add="+songJSON;
  QNetworkRequest addSongRequest(getLibAddSongUrl());
  netAccessManager->post(addSongRequest, finalData);
}

void UDJServerConnection::authenticate(
  const QString& username, 
  const QString& password)
{
  QNetworkRequest authRequest(getAuthUrl());
  QString data("username="+username+"&password="+password);
  QBuffer *dataBuffer = new QBuffer();
  dataBuffer->setData(data.toUtf8());
  QNetworkReply *reply = netAccessManager->post(authRequest, dataBuffer);
  dataBuffer->setParent(reply);
}
 
void UDJServerConnection::recievedReply(QNetworkReply *reply){
  if(reply->request().url().path() == getAuthUrl().path()){
    handleAuthReply(reply);
  }
  else if(reply->request().url().path() == getLibAddSongUrl().path()){
    handleAddSongReply(reply);
  }
  reply->deleteLater();
}

void UDJServerConnection::handleAuthReply(QNetworkReply* reply){
  QString stringreply(reply->readAll());
  //std::cout << stringreply.toStdString() << std::endl;
  if(haveValidLoginCookie()){
    isLoggedIn = true;
    emit connectionEstablished();
  }
  else{
    emit unableToConnect("Bad username and password");
  }
}

bool UDJServerConnection::haveValidLoginCookie(){
  QList<QNetworkCookie> authCookies = cookieJar->cookiesForUrl(getAuthUrl());
  for(int i =0; i<authCookies.size(); ++i){
    if(authCookies.at(i).name() == getLoginCookieName()){
      return true;
    }
  }
  return false;
}

void UDJServerConnection::handleAddSongReply(QNetworkReply *reply){
  std::map<libraryid_t, libraryid_t> hostToServerIdMap =
    JSONHelper::getHostToServerLibIdMap(reply);
  emit serverIdsUpdate(hostToServerIdMap); 
}


}//end namespace
