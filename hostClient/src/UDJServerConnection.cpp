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


namespace UDJ{


UDJServerConnection::UDJServerConnection(QObject *parent):QObject(parent),
  ticket_hash(""),
  user_id(-1),
  eventId(-1)
{
  netAccessManager = new QNetworkAccessManager(this);
  connect(netAccessManager, SIGNAL(finished(QNetworkReply*)),
    this, SLOT(recievedReply(QNetworkReply*)));
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
  DEBUG_MESSAGE("Adding song to library on server: " << songName.toStdString())
  bool success = true;

  lib_song_t songToAdd = {hostId, songName, artistName, albumName, duration};

  const QByteArray songJSON = JSONHelper::getJSONForLibAdd(
    songToAdd,
    success);
  QNetworkRequest addSongRequest(getLibAddSongUrl());
  prepareJSONRequest(addSongRequest);
  addSongRequest.setRawHeader(getMachineUUIDHeaderName(), machineUUID.toUtf8());
  QNetworkReply *reply = netAccessManager->put(addSongRequest, songJSON);
  reply->setProperty(getPayloadPropertyName(), songJSON);
}

void UDJServerConnection::deleteLibSongOnServer(library_song_id_t toDeleteId){
  QNetworkRequest deleteSongRequest(getLibDeleteSongUrl(toDeleteId));
  deleteSongRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  deleteSongRequest.setRawHeader(getMachineUUIDHeaderName(), machineUUID.toUtf8());
  QNetworkReply *reply = netAccessManager->deleteResource(deleteSongRequest);
}

void UDJServerConnection::createEvent(
  const QString& eventName,
  const QString& password)
{
  const QByteArray eventJSON = JSONHelper::getCreateEventJSON(
    eventName, password);
  createEvent(eventJSON);
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

void UDJServerConnection::createEvent(
  const QString& eventName,
  const QString& password,
  const double &latitude,
  const double &longitude)
{
  const QByteArray eventJSON = JSONHelper::getCreateEventJSON(
    eventName, password, latitude, longitude);
  createEvent(eventJSON);
}

void UDJServerConnection::createEvent(const QByteArray& payload){
  QNetworkRequest createEventRequest(getCreateEventUrl());
  prepareJSONRequest(createEventRequest);
  QNetworkReply *reply = netAccessManager->put(createEventRequest, payload);
  reply->setProperty(getPayloadPropertyName(), payload); 
}

void UDJServerConnection::endEvent(){
  QNetworkRequest endEventRequest(getEndEventUrl());
  endEventRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  netAccessManager->deleteResource(endEventRequest);
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
  addSongToAvailableRequest.setRawHeader(getMachineUUIDHeaderName(), machineUUID.toUtf8());
  const QByteArray songsAddJSON = JSONHelper::getAddToAvailableJSON(songsToAdd);
  QNetworkReply *reply =
    netAccessManager->put(addSongToAvailableRequest, songsAddJSON);
  reply->setProperty(getPayloadPropertyName(), songsAddJSON); 
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
  reply->setProperty(getPayloadPropertyName(), songsAddJSON); 
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
  QString params = "playlist_entry_id="+QString::number(currentSong);
  setCurrentSong(params.toUtf8());
}

void UDJServerConnection::setCurrentSong(const QByteArray& payload){
  QNetworkRequest setCurrentSongRequest(getCurrentSongUrl());
  setCurrentSongRequest.setRawHeader(getTicketHeaderName(), ticket_hash);
  QNetworkReply *reply =
    netAccessManager->post(setCurrentSongRequest, payload);
  reply->setProperty(getPayloadPropertyName(), payload);
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
    emit authenticated(
      reply->rawHeader(getTicketHeaderName()),
      QString(reply->rawHeader(getUserIdHeaderName())).toLong()
    );
  }
  else if(
    !reply->hasRawHeader(getTicketHeaderName()) ||
    !reply->hasRawHeader(getUserIdHeaderName()))
  {
    QByteArray responseData = reply->readAll();
    QString responseString = QString::fromUtf8(responseData);
    DEBUG_MESSAGE(responseString.toStdString())
    emit authFailed(
      tr("We're experiencing some techinical difficulties. "
      "We'll be back in a bit"));
  }
  else{
    QByteArray responseData = reply->readAll();
    QString responseString = QString::fromUtf8(responseData);
    DEBUG_MESSAGE(responseString.toStdString())
    QString error = tr("Unable to connect to server: error ") + 
     QString::number(reply->error());
    emit authFailed(error);
  }
}

bool UDJServerConnection::checkReplyAndFireErrors(
  QNetworkReply *reply,
  CommErrorHandler::OperationType opType
)
{
  QByteArray payload;
  QVariant potentialPayload = reply->property(getPayloadPropertyName());
  if(potentialPayload.isValid()){
    payload = potentialPayload.toByteArray();
  }

  if(reply->attribute(QNetworkRequest::HttpStatusCodeAttribute) == 403){
    emit commError(opType, CommErrorHandler::AUTH, payload);
    return true;
  }
  else if(reply->attribute(QNetworkRequest::HttpStatusCodeAttribute) == 409){
    emit commError(opType, CommErrorHandler::CONFLICT, payload);
    return true;
  }
  else if(reply->attribute(QNetworkRequest::HttpStatusCodeAttribute) == 500){
    QByteArray response = reply->readAll();
    QString resposneMessage = QString(response);
    DEBUG_MESSAGE(resposneMessage.toStdString())
    emit commError(opType, CommErrorHandler::SERVER_ERROR, payload);
    return true;
  }
  else if(reply->error() != QNetworkReply::NoError){
    emit commError(opType, CommErrorHandler::UNKNOWN_ERROR, payload);
    return true;
  }
  return false;
}


void UDJServerConnection::handleAddLibSongsReply(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::LIB_SONG_ADD)){
    const std::vector<library_song_id_t> updatedIds = JSONHelper::getUpdatedLibIds(reply);
    emit songsAddedToLibOnServer(updatedIds);
  }
}


void UDJServerConnection::handleDeleteLibSongsReply(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::LIB_SONG_DELETE)){
    QString path = reply->request().url().path();
    QRegExp rx("/udj/users/" + QString::number(user_id) + "/library/(\\d+)");
    rx.indexIn(path);
    library_song_id_t songDeleted = rx.cap(1).toLong();
    emit songDeletedFromLibOnServer(songDeleted);
  }
}

void UDJServerConnection::handleAddAvailableSongReply(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::AVAILABLE_SONG_ADD)){
    std::vector<library_song_id_t> addedIds = 
      JSONHelper::getAddedAvailableSongs(reply);
    emit songsAddedToAvailableMusic(addedIds); 
  }
}

void UDJServerConnection::handleDeleteAvailableMusicReply(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::AVAILABLE_SONG_DEL)){
    QString path = reply->request().url().path();
    QRegExp rx("/udj/events/" + QString::number(eventId) + 
      "/available_music/(\\d+)");
    rx.indexIn(path);
    library_song_id_t songDeleted = rx.cap(1).toLong();
    emit songRemovedFromAvailableMusicOnServer(songDeleted);
  }
}

void UDJServerConnection::handleCreateEventReply(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::CREATE_EVENT)){
    //TODO handle bad json resturned from the server.
    event_id_t issuedId = JSONHelper::getEventId(reply);
    emit eventCreated(issuedId);
  }
}

void UDJServerConnection::handleEndEventReply(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::END_EVENT)){
    emit eventEnded();
  }
}

void UDJServerConnection::handleRecievedActivePlaylist(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::PLAYLIST_UPDATE)){
    emit newActivePlaylist(JSONHelper::getActivePlaylistFromJSON(reply));
  }
}

void UDJServerConnection::handleRecievedActivePlaylistAdd(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::PLAYLIST_ADD)){
    QVariant payload = reply->property(getPayloadPropertyName());
    emit songsAddedToActivePlaylist(JSONHelper::extractAddRequestIds(payload.toByteArray()));
  }
}

void UDJServerConnection::handleRecievedCurrentSongSet(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::SET_CURRENT_SONG)){
    emit currentSongSet();
  }
}

void UDJServerConnection::handleRecievedActivePlaylistRemove(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::PLAYLIST_REMOVE)){
    QString path = reply->request().url().path();
    QRegExp rx("/udj/events/" + QString::number(eventId) + "/active_playlist/(\\d+)");
    rx.indexIn(path);
    playlist_song_id_t songDeleted = rx.cap(1).toLong();
    emit songRemovedFromActivePlaylist(songDeleted);
  }
}

void UDJServerConnection::handleRecievedNewEventGoers(QNetworkReply *reply){
  if(!checkReplyAndFireErrors(reply, CommErrorHandler::EVENT_GOERS_REFRESH)){
    emit newEventGoers(JSONHelper::getEventGoersJSON(reply));
  }
}

void UDJServerConnection::handleLocaitonResponse(QNetworkReply *reply){
  DEBUG_MESSAGE("Handling location reply response")
  if(reply->error() == QNetworkReply::NoError){
    parseLocationResponse(reply);
  }
  else{
    //TODO redo this in light of the new error handler
    /*QString locationError = QString(reply->readAll());
    DEBUG_MESSAGE("Error retreving location" << locationError.toStdString())
    emit eventCreationFailed("Failed to create event. There was an error" 
      "verifying your locaiton. Please change it and try again.");
    */
  }
}

void UDJServerConnection::parseLocationResponse(QNetworkReply *reply){
  DEBUG_MESSAGE("Parsing location resposne");
  QString response(reply->readAll());
  QStringList outputValues = response.split(",");
  if(outputValues[2] != "200"){
    //TODO redo this in light of the new error handler
    /*
    DEBUG_MESSAGE("Error retreving location" << outputValues[2].toStdString())
    emit eventCreationFailed("Failed to create event. There was an error " 
      "verifying your locaiton. Please change it and try again.");
    */
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
  toReturn.addQueryItem("apiKey", UDJ_GEOCODER_API_KEY);
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
