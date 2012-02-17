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
#ifndef COMM_ERROR_HANDLER_HPP
#define COMM_ERROR_HANDLER_HPP

#include "ConfigDefs.hpp"
#include <QObject>
#include <QByteArray>

namespace UDJ{

class UDJServerConnection;
class DataStore;

class CommErrorHandler : public QObject{
Q_OBJECT
public:

  enum CommErrorType{
    AUTH,
    CONFLICT,
    SERVER_ERROR,
    UNKNOWN_ERROR
  };

  enum OperationType{
    LIB_SONG_ADD,
    LIB_SONG_DELETE,
    CREATE_EVENT,
    END_EVENT,
    AVAILABLE_SONG_ADD,
    AVAILABLE_SONG_DEL,
    PLAYLIST_UPDATE,
    PLAYLIST_ADD,
    PLAYLIST_REMOVE,
    SET_CURRENT_SONG,
    EVENT_GOERS_REFRESH
  };

  CommErrorHandler(DataStore *dataStore, UDJServerConnection *serverConnection);

signals:

  void hardAuthFailure(const QString errMessage);

  void eventCreationFailed(const QString errMessage);

  void eventEndingFailed(const QString errMessage);

  void libSyncError(const QString errMessage);

  void availableMusicSyncError(const QString errMessage);

  void refreshActivePlaylistError(const QString errMessage);

  void playlistAddRequestError(const QString errMessage);

  void playlistRemoveRequestError(const QString errMessage);

  void setCurrentSongError(const QString errMessage);

  void eventGoerRefreshError(const QString errMessage);

private slots:

  void handleCommError(
    CommErrorHandler::OperationType opType,
    CommErrorHandler::CommErrorType errorType,
    const QByteArray& payload);

  void onAuthenticated(const QByteArray& ticket, const user_id_t& user_id);

  void onHardAuthFailure(const QString errMessage);

private:

  DataStore *dataStore;

  UDJServerConnection *serverConnection;

  QByteArray createEventPayload;

  QByteArray setCurrentSongPayload;

  bool hasPendingReauthRequest;

  bool syncLibOnReauth;

  bool createEventOnReauth;

  bool endEventOnReauth;

  bool syncAvailableMusicOnReauth;

  bool refreshActivePlaylistOnReauth;

  bool syncPlaylistAddRequestsOnReauth;

  bool setCurrentSongOnReauth;

  bool syncPlaylistRemoveRequestsOnReauth;

  bool refreshEventGoersOnReauth;

  void clearOnReauthFlags();

  void requestReauth();
};


}
#endif //COMM_ERROR_HANDLER_HPP
