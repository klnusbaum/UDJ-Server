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
#include <QRegExp>
#include <QStringList>
#include "UDJServerConnection.hpp"
#include "JSONHelper.hpp"
#include "GeocoderApiKey.hpp"

Q_DECLARE_METATYPE(std::vector<UDJ::client_request_id_t>)
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

void UDJServerConnection::deleteLibSongOnServer(library_song_id_t toDeleteId){
  QNetworkRequest deleteSongRequest(getLibDeleteSongUrl(toDeleteId));
  deleteSongRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  QNetworkReply *reply = netAccessManager->deleteResource(deleteSongRequest);
}
 
void UDJServerConnection::createEvent(
  const QString& eventName,
  const QString& password)
{
  QNetworkRequest createEventRequest(getCreateEventUrl());
  prepareJSONRequest(createEventRequest);
  const QByteArray eventJSON = JSONHelper::getCreateEventJSON(
    eventName, password);
  netAccessManager->put(createEventRequest, eventJSON);
}

void UDJServerConnection::createEvent(
  const QString& eventName,
  const QString& password,
  const QString& streetAddress,
  const QString& city,
  const QString& state,
  const QString& zipcode)
{
  DEBUG_MESSAGE("Doing location request")
  QNetworkRequest locationRequest(
    getLocationUrl(streetAddress, city, state, zipcode));
  QNetworkReply *reply = netAccessManager->get(locationRequest);
  reply->setProperty(getEventNameProperty(), eventName);
  reply->setProperty(getEventPasswordProperty(), password);
}

void UDJServerConnection::endEvent(){
  QNetworkRequest endEventRequest(getEndEventUrl());
  endEventRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  netAccessManager->deleteResource(endEventRequest);
}

void UDJServerConnection::createEvent(
  const QString& eventName,
  const QString& password,
  const double &latitude,
  const double &longitude)
{
  QNetworkRequest createEventRequest(getCreateEventUrl());
  prepareJSONRequest(createEventRequest);
  const QByteArray eventJSON = JSONHelper::getCreateEventJSON(
    eventName, password, latitude, longitude);
  netAccessManager->put(createEventRequest, eventJSON);
}

void UDJServerConnection::addSongToAvailableSongs(library_song_id_t songToAdd){
  std::vector<library_song_id_t> toAddVector(1, songToAdd);
  addSongsToAvailableSongs(toAddVector);
}

void UDJServerConnection::addSongsToAvailableSongs(
  const std::vector<library_song_id_t>& songsToAdd)
{
  if(songsToAdd.size() <= 0){
    return;
  }
  QNetworkRequest addSongToAvailableRequest(getAddSongToAvailableUrl());
  prepareJSONRequest(addSongToAvailableRequest);
  const QByteArray songsAddJSON = JSONHelper::getAddToAvailableJSON(songsToAdd);
  netAccessManager->put(addSongToAvailableRequest, songsAddJSON);
}

void UDJServerConnection::removeSongsFromAvailableMusic(
  const std::vector<library_song_id_t>& songsToRemove)
{
  if(songsToRemove.size() <= 0){
    return;
  }
  for(
    std::vector<library_song_id_t>::const_iterator it = songsToRemove.begin();
    it != songsToRemove.end();
    ++it)
  {
    QNetworkRequest removeSongFromAvailableRequest(
      getAvailableMusicRemoveUrl(*it));
    removeSongFromAvailableRequest.setRawHeader(
      getTicketHeaderName(), ticket_hash);
    netAccessManager->deleteResource(removeSongFromAvailableRequest);
  }
}

void UDJServerConnection::getActivePlaylist(){
  QNetworkRequest getActivePlaylistRequest(getActivePlaylistUrl());
  getActivePlaylistRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  netAccessManager->get(getActivePlaylistRequest);
}

void UDJServerConnection::addSongToActivePlaylist(
  client_request_id_t requestId, 
  library_song_id_t songId)
{
  std::vector<client_request_id_t> requestIds(1, requestId);
  std::vector<library_song_id_t> songIds(1, songId);
  addSongsToActivePlaylist(requestIds, songIds);
}

void UDJServerConnection::addSongsToActivePlaylist(
  const std::vector<client_request_id_t>& requestIds, 
  const std::vector<library_song_id_t>& songIds)
{
  QNetworkRequest add2ActivePlaylistRequest(getActivePlaylistAddUrl());
  prepareJSONRequest(add2ActivePlaylistRequest);
  bool success;
  const QByteArray songsAddJSON = JSONHelper::getAddToActiveJSON(
    requestIds,
    songIds,
    success);
  if(!success){
    //TODO handle error
    DEBUG_MESSAGE("Error serializing active playlist addition reuqest")
    return;
  }
  QNetworkReply *reply = 
    netAccessManager->put(add2ActivePlaylistRequest, songsAddJSON);
  reply->setProperty(getActivePlaylistRequestIdsPropertyName(),
    QVariant::fromValue<std::vector<client_request_id_t> >(requestIds));
}

void UDJServerConnection::removeSongsFromActivePlaylist(
  const std::vector<playlist_song_id_t>& playlistIds)
{
  if(playlistIds.size() <= 0){
    return;
  }
  for(
    std::vector<playlist_song_id_t>::const_iterator it = playlistIds.begin();
    it != playlistIds.end();
    ++it)
  {
    QNetworkRequest removeSongFromActiveRequest(
      getActivePlaylistRemoveUrl(*it));
    removeSongFromActiveRequest.setRawHeader(
      getTicketHeaderName(), ticket_hash);
    netAccessManager->deleteResource(removeSongFromActiveRequest);
  }
}


void UDJServerConnection::setCurrentSong(playlist_song_id_t currentSong){
  QNetworkRequest setCurrentSongRequest(getCurrentSongUrl());
  setCurrentSongRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  QString params = "playlist_entry_id="+QString::number(currentSong);
  netAccessManager->post(setCurrentSongRequest, params.toUtf8());
}

void UDJServerConnection::getEventGoers(){
  QNetworkRequest getEventGoersRequest(getUsersUrl());
  getEventGoersRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  netAccessManager->get(getEventGoersRequest);
}

void UDJServerConnection::recievedReply(QNetworkReply *reply){
  if(reply->request().url().path() == getAuthUrl().path()){
    handleAuthReply(reply);
  }
  else if(reply->request().url().path() == getLibAddSongUrl().path()){
    handleAddLibSongsReply(reply);
  }
  else if(reply->request().url().path() == getCreateEventUrl().path()){
    handleCreateEventReply(reply);
  }
  else if(reply->request().url().path() == getEndEventUrl().path()){
    handleEndEventReply(reply);
  }
  else if(reply->request().url().path() == getAddSongToAvailableUrl().path()){
    handleAddAvailableSongReply(reply);
  }
  else if(reply->request().url().path() == getActivePlaylistUrl().path()){
    handleRecievedActivePlaylist(reply);
  }
  else if(reply->request().url().path() == getActivePlaylistAddUrl().path()){
    handleRecievedActivePlaylistAdd(reply);
  }
  else if(reply->request().url().path() == getCurrentSongUrl().path()){
    handleRecievedCurrentSongSet(reply);
  }
  else if(isLibDeleteUrl(reply->request().url().path())){
    handleDeleteLibSongsReply(reply);
  }
  else if(isAvailableMusicDeleteUrl(reply->request().url().path())){
    handleDeleteAvailableMusicReply(reply);
  }
  else if(isActivePlaylistRemoveUrl(reply->request().url().path())){
    handleRecievedActivePlaylistRemove(reply);
  }
  else if(reply->request().url().path() == getUsersUrl().path()){
    handleRecievedNewEventGoers(reply);
  }
  else if(isLocationUrl(reply->request().url())){
    handleLocaitonResponse(reply);
  }
  else{
    DEBUG_MESSAGE("Recieved unknown response")
    DEBUG_MESSAGE(reply->request().url().path().toStdString())
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
    QByteArray responseData = reply->readAll();
    QString responseString = QString::fromUtf8(responseData);
    DEBUG_MESSAGE(responseString.toStdString())
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

void UDJServerConnection::handleAddLibSongsReply(QNetworkReply *reply){
  const std::vector<library_song_id_t> updatedIds =   
    JSONHelper::getUpdatedLibIds(reply);
  emit songsAddedToLibOnServer(updatedIds);
}

void UDJServerConnection::handleDeleteLibSongsReply(QNetworkReply *reply){
  if(reply->error() == QNetworkReply::NoError){
    QString path = reply->request().url().path();
    QRegExp rx("/udj/users/" + QString::number(user_id) + "/library/(\\d+)");
    rx.indexIn(path);
    library_song_id_t songDeleted = rx.cap(1).toLong();
    emit songDeletedFromLibOnServer(songDeleted);
  }
  else{
    DEBUG_MESSAGE("Error deleting lib song on server: " << 
      QString(reply->readAll()).toStdString())
  }
}

void UDJServerConnection::handleAddAvailableSongReply(QNetworkReply *reply){
  if(reply->error() == QNetworkReply::NoError){
    std::vector<library_song_id_t> addedIds = 
      JSONHelper::getAddedAvailableSongs(reply);
    emit songsAddedToAvailableMusic(addedIds); 
  }
  else{
    DEBUG_MESSAGE("Error adding available music" << std::endl <<
      QString(reply->readAll()).toStdString())
  }
}

void UDJServerConnection::handleDeleteAvailableMusicReply(
  QNetworkReply *reply)
{
  if(reply->error() == QNetworkReply::NoError){
    QString path = reply->request().url().path();
    QRegExp rx("/udj/events/" + QString::number(eventId) + 
      "/available_music/(\\d+)");
    rx.indexIn(path);
    library_song_id_t songDeleted = rx.cap(1).toLong();
    emit songRemovedFromAvailableMusicOnServer(songDeleted);
  }
}

void UDJServerConnection::handleCreateEventReply(QNetworkReply *reply){
  //TODO
  // Handle if a 409 response is returned
  if(reply->error() != QNetworkReply::NoError){
    emit eventCreationFailed("Failed to create event");
    QByteArray errormsg = reply->readAll();
    DEBUG_MESSAGE(QString(errormsg).toStdString())
    return;
  }
  //TODO handle bad json resturned from the server.
  isHostingEvent =true;
  eventId = JSONHelper::getEventId(reply);
  emit eventCreated();
}

void UDJServerConnection::handleEndEventReply(QNetworkReply *reply){
  if(reply->error() != QNetworkReply::NoError){
    emit eventEndingFailed(tr("Failed to end event") + 
      QString::number(reply->error()) );
    return;
  }
  emit eventEnded();
}

void UDJServerConnection::handleRecievedActivePlaylist(QNetworkReply *reply){
  if(reply->error() == QNetworkReply::NoError){
    emit newActivePlaylist(JSONHelper::getActivePlaylistFromJSON(reply));
  }
}

void UDJServerConnection::handleRecievedActivePlaylistAdd(QNetworkReply *reply){
  if(reply->error() == QNetworkReply::NoError){
    QVariant property = reply->property(
      getActivePlaylistRequestIdsPropertyName());
    std::vector<client_request_id_t> requestedIds = 
      property.value<std::vector<client_request_id_t> >();
    emit songsAddedToActivePlaylist(requestedIds);
  }
  else{
    QByteArray error = reply->readAll();
    DEBUG_MESSAGE(QString(error).toStdString())
  }
}

void UDJServerConnection::handleRecievedCurrentSongSet(QNetworkReply *reply){
  if(reply->error() == QNetworkReply::NoError){
    emit currentSongSet();
  }
  else{
    DEBUG_MESSAGE(QString(reply->readAll()).toStdString());
    emit currentSongSetError();
  }
}

void UDJServerConnection::handleRecievedActivePlaylistRemove(
  QNetworkReply *reply)
{
  if(reply->error() == QNetworkReply::NoError){
    QString path = reply->request().url().path();
    QRegExp rx("/udj/events/" + QString::number(eventId) + 
      "/active_playlist/(\\d+)");
    rx.indexIn(path);
    playlist_song_id_t songDeleted = rx.cap(1).toLong();
    emit songRemovedFromActivePlaylist(songDeleted);
  }
  else{
    DEBUG_MESSAGE("Error deleting song from active playlist " <<
      QString(reply->readAll()).toStdString())
  } 
}

void UDJServerConnection::handleRecievedNewEventGoers(QNetworkReply *reply){
  if(reply->error() == QNetworkReply::NoError){
    emit newEventGoers(JSONHelper::getEventGoersJSON(reply));
  }
  else{
    DEBUG_MESSAGE("Error retrieving event goer list" <<
      QString(reply->readAll()).toStdString())
  } 
}

void UDJServerConnection::handleLocaitonResponse(QNetworkReply *reply){
  DEBUG_MESSAGE("Handling location reply response");
  if(reply->error() == QNetworkReply::NoError){
    parseLocationResponse(reply);
  }
  else{
    QString locationError = QString(reply->readAll());
    DEBUG_MESSAGE("Error retreving location" << locationError.toStdString())
    emit eventCreationFailed("Failed to create event. There was an error" 
      "verifying your locaiton. Please change it and try again.");
  }

}

void UDJServerConnection::parseLocationResponse(QNetworkReply *reply){
  DEBUG_MESSAGE("Parsing location resposne");
  QString response(reply->readAll());
  QStringList outputValues = response.split(",");
  if(outputValues[2] != "200"){
    DEBUG_MESSAGE("Error retreving location" << outputValues[2].toStdString())
    emit eventCreationFailed("Failed to create event. There was an error " 
      "verifying your locaiton. Please change it and try again.");
  }
  else{
    QString eventName = reply->property(getEventNameProperty()).toString();
    QString eventPassword = reply->property(
      getEventPasswordProperty()).toString();
    createEvent(
      eventName,
      eventPassword,
      outputValues[3].toDouble(),
      outputValues[4].toDouble()); 
  }
}

QUrl UDJServerConnection::getLibAddSongUrl() const{
  return QUrl(getServerUrlPath() + "users/" + QString::number(user_id) +
    "/library/songs");
}

QUrl UDJServerConnection::getLibDeleteSongUrl(library_song_id_t toDelete) const{
  return QUrl(getServerUrlPath() + "users/" + QString::number(user_id) +
    "/library/" + QString::number(toDelete));
}

QUrl UDJServerConnection::getAvailableMusicRemoveUrl(
  library_song_id_t toDelete) const
{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId) +
    "/available_music/" + QString::number(toDelete));
}

QUrl UDJServerConnection::getEndEventUrl() const{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId));
}

QUrl UDJServerConnection::getAddSongToAvailableUrl() const{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId) +
    "/available_music");
}

QUrl UDJServerConnection::getActivePlaylistUrl() const{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId) +
    "/active_playlist");
}

QUrl UDJServerConnection::getActivePlaylistAddUrl() const{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId) +
    "/active_playlist/songs");
}

QUrl UDJServerConnection::getActivePlaylistRemoveUrl(
  playlist_song_id_t toDelete) const
{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId) +
    "/active_playlist/songs/" + QString::number(toDelete));
}


QUrl UDJServerConnection::getCurrentSongUrl() const{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId) +
    "/current_song");
}

QUrl UDJServerConnection::getUsersUrl() const{
  return QUrl(getServerUrlPath() + "events/" + QString::number(eventId) +
    "/users");
}

bool UDJServerConnection::isLibDeleteUrl(const QString& path) const{
  QRegExp rx("^/udj/users/" + QString::number(user_id) + "/library/\\d+$");
  return rx.exactMatch(path);
}

bool UDJServerConnection::isAvailableMusicDeleteUrl(const QString& path) const{
  QRegExp rx("^/udj/events/" + QString::number(eventId) + 
    "/available_music/\\d+$");
  return rx.exactMatch(path);
}

bool UDJServerConnection::isActivePlaylistRemoveUrl(const QString& path) const{
  QRegExp rx("^/udj/events/" + QString::number(eventId) + 
    "/active_playlist/songs/\\d+$");
  return rx.exactMatch(path);
}

QUrl UDJServerConnection::getLocationUrl(
  const QString& streetAddress,
  const QString& city,
  const QString& state,
  const QString& zipcode) const
{
  QUrl toReturn("https://webgis.usc.edu/Services/"
    "Geocode/WebService/GeocoderWebServiceHttpNonParsed_V02_96.aspx");
  toReturn.addQueryItem("apiKey", GEOCODER_API_KEY);
  toReturn.addQueryItem("version" , "2.96");
  toReturn.addQueryItem("streetAddress" , streetAddress);
  toReturn.addQueryItem("state",state);
  toReturn.addQueryItem("zipcode",zipcode);
  toReturn.addQueryItem("format", "csv");
  if(city != ""){
    toReturn.addQueryItem("city", city);
  }
  return toReturn;
}

}//end namespace
