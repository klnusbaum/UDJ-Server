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
#ifndef DATA_STORE_HPP
#define DATA_STORE_HPP
#include <QSqlDatabase>
#include <phonon/mediaobject.h>
#include <phonon/mediasource.h>
#include <QProgressDialog>
#include "UDJServerConnection.hpp"

class QTimer;

namespace UDJ{


/** 
 * \brief A class that provides access to all persisten storage used by UDJ.
 */
class DataStore : public QObject{
Q_OBJECT
public:

  /** @name Constructor(s) and Destructor */
  //@{

  /** \brief Constructs a DataStore
   *
   * @param serverConnection Connection to the UDJ server.
   * @param parent The parent widget.
   */
  DataStore(UDJServerConnection *serverConnection, QObject *parent=0);

  //@}

  /** @name Getters and Setters */
  //@{

  void addMusicToLibrary(
    QList<Phonon::MediaSource> songs, 
    QProgressDialog& progress);

  /**
   * \brief Adds a single song to the music library.
   *
   * @param song Song to be added to the library.
   */
  void addSongToLibrary(Phonon::MediaSource song);

  /**
   * \brief Given a media source, determines the song name from the current
   * model data.
   *
   * @param source Source whose song name is desired.
   * @return The name of the song contained in the given source according
   * to current model data. If the source could not be found in the model
   * and emptry string is returned.
   */
  QString getSongNameFromSource(const Phonon::MediaSource &source) const;

  QSqlDatabase getDatabaseConnection();

  inline const QString& getEventName() const{
    return eventName;
  }

  inline event_id_t getEventId() const{
    return serverConnection->getEventId();
  }

  inline bool isCurrentlyHosting() const{
    return serverConnection->getIsHosting();
  }

  Phonon::MediaSource getNextSongToPlay();
  
  Phonon::MediaSource takeNextSongToPlay();

  
  /** @name Public Constants */
  //@{

  /**
   * \brief Gets the name of the table in the musicdb that contains information
   * about the music library associated with the server conneciton.
   *
   * @return The name of the table in the musicdb that contains information
   * about the music library associated with the server connection.
   */
	static const QString& getLibraryTableName(){
    static const QString libraryTableName = "library";
    return libraryTableName;
	}

  /**
   * \brief Gets the name of the table in the musicdb that contains information
   * about the event goers associated with the server conneciton.
   *
   * @return The name of the table in the musicdb that contains information
   * about the event goesrs associated with the server connection.
   */
	static const QString& getEventGoersTableName(){
		static const QString eventGoersTableName = "my_event_goers";
    return eventGoersTableName;
	}
  
  static const QString& getActivePlaylistTableName(){
    static const QString activePlaylistTableName = "active_playlist";
    return activePlaylistTableName;
  }

  static const QString& getActivePlaylistViewName(){
    static const QString activePlaylistViewName = "active_playlist_view";
    return activePlaylistViewName;
  }

  static const QString& getActivePlaylistIdColName(){
    static const QString activePlaylistIdColName = "id";
    return activePlaylistIdColName;
  }

  static const QString& getActivePlaylistLibIdColName(){
    static const QString activePlaylistLibIdColName = "lib_id";
    return activePlaylistLibIdColName;
  }

  static const QString& getVoteCountColName(){
    static const QString voteCountColName = "vote_count";
    return voteCountColName;
  }

  static const QString& getTimeAddedColName(){
    static const QString timeAddedColName = "time_added";
    return timeAddedColName;
  }

  static const QString& getPriorityColName(){
    static const QString priorityColName = "priority";
    return priorityColName;
  }

  static const QString& getAdderIdColName(){
    static const QString adderIdColName = "adderId";
    return adderIdColName;
  }

  static const QString& getLibIdColName(){
    static const QString libIdColName = "id";
    return libIdColName;
  }

  static const QString& getUpVoteColName(){
    static const QString upVoteColName = "up_votes";
    return upVoteColName;
  }

  static const QString& getDownVoteColName(){
    static const QString downVoteColName = "down_votes";
    return downVoteColName;
  }

  static const QString& getLibSongColName(){
    static const QString libSongColName = "song";
    return libSongColName;
  }

  static const QString& getLibArtistColName(){
    static const QString libArtistColName = "artist";
    return libArtistColName;
  }
  
  static const QString& getLibAlbumColName(){
    static const QString libAlbumColName = "album";
    return libAlbumColName;
  }

  static const QString& getLibFileColName(){
    static const QString libFileColName = "file_path";
    return libFileColName;
  }

  static const QString& getLibDurationColName(){
    static const QString libDurationColName = "duration";
    return libDurationColName;
  }

  static const QString& getLibIsDeletedColName(){
    static const QString libIsDeletedColName = "is_deleted";
    return libIsDeletedColName;
  }

  static const QString& getLibSyncStatusColName(){
    static const QString libSyncStatusColName = "sync_status";
    return libSyncStatusColName;
  }

  static const lib_sync_status_t& getLibNeedsAddSyncStatus(){
    static const lib_sync_status_t libNeedsAddSyncStatus = 1;
    return libNeedsAddSyncStatus;
  }

  static const lib_sync_status_t& getLibNeedsDeleteSyncStatus(){
    static const lib_sync_status_t libNeedsDeleteSyncStatus = 2;
    return libNeedsDeleteSyncStatus;
  }

  static const lib_sync_status_t& getLibIsSyncedStatus(){
    static const lib_sync_status_t libIsSyncedStatus = 0;
    return libIsSyncedStatus;
  }
  
  static const QString& getPlaylistTableName(){
    static const QString playlistTableName = "playlist";
    return playlistTableName;
  }

  static const QString& getPlaylistIdColName(){
    static const QString playlistIdColName = "id";
    return playlistIdColName;
  }

  static const QString& getPlaylistNameColName(){
    static const QString playlistNameColName = "name";
    return playlistNameColName;
  }

  static const QString& getPlaylistEntryIdColName(){
    static const QString playlistEntryIdColName = "id";
    return playlistEntryIdColName;
  }

  static const QString& getPlaylistEntrySongIdColName(){
    static const QString playlistEntrySongIdColName = "lib_id";
    return playlistEntrySongIdColName;
  }
  
  static const QString& getPlaylistEntryNumberColName(){
    static const QString playlistEntryNumberColName = "entry_number";
    return playlistEntryNumberColName;
  }

  static const QString& getPlaylistEntryTableName(){
    static const QString playlistEntryTableName = "playlist_entry";
    return playlistEntryTableName;
  }

  static const QString& getAvailableMusicTableName(){
    static const QString availableMusicTableName = "available_music";
    return availableMusicTableName;
  }

  static const QString& getAvailableEntryLibIdColName(){
    static const QString availableEntryLibIdColName = "lib_id";
    return availableEntryLibIdColName;
  }

  static const QString& getAvailableEntryIsDeletedColName(){
    static const QString availEntryIsDeletedColName = "is_deleted";
    return availEntryIsDeletedColName;
  }

  static const QString& getAvailableEntrySyncStatusColName(){
    static const QString availEntrySyncStatusColName = "sync_status";
    return availEntrySyncStatusColName;
  }

  static const avail_music_sync_status_t& getAvailableEntryNeedsAddSyncStatus(){
    static const avail_music_sync_status_t availEntryNeedsAddSyncStatus = 1;
    return availEntryNeedsAddSyncStatus;
  }

  static const avail_music_sync_status_t& 
    getAvailableEntryNeedsDeleteSyncStatus()
  {
    static const avail_music_sync_status_t availEntryNeedsDeleteSyncStatus = 2;
    return availEntryNeedsDeleteSyncStatus;
  }

  static const avail_music_sync_status_t& getAvailableEntryIsSyncedStatus(){
    static const avail_music_sync_status_t availEntryIsSyncedStatus = 0;
    return availEntryIsSyncedStatus;
  }

  static const QString& getAvailableMusicViewName(){
    static const QString availableMusicViewName ="available_music_view";
    return availableMusicViewName;
  }

  static const QString& getPlaylistAddRequestsTableName(){
    static const QString playlistAddRequestsTableName = "playlist_add_requests";
    return playlistAddRequestsTableName;
  }

  static const QString& getPlaylistAddIdColName(){
    static const QString playlistAddIdColName = "addId";
    return playlistAddIdColName;
  }

  static const QString& getPlaylistAddLibIdColName(){
    static const QString playlistAddLibIdColName = "libId";
    return playlistAddLibIdColName;
  }

  static const QString& getPlaylistAddSycnStatusColName(){
    static const QString playlistAddSyncStatusColName = "sync_status";
    return playlistAddSyncStatusColName;
  }

  static const playlist_add_sync_status_t& getPlaylistAddNeedsSync(){
    static const playlist_add_sync_status_t needsSyncStatus=1;
    return needsSyncStatus;
  }

  static const playlist_add_sync_status_t& getPlaylistAddIsSynced(){
    static const playlist_add_sync_status_t isSynced=0;
    return isSynced;
  }


 //@}

/** @name Public slots */
//@{
public slots:

  void addSongToAvailableSongs(library_song_id_t song_id);

  void addSongsToAvailableSongs(const std::vector<library_song_id_t>& song_ids);

  void refreshActivePlaylist();

  /**
   * \brief Adds the specified song to the playlist.
   *
   * @param libraryId Id of the song to add to the playlist.
   */
	void addSongToActivePlaylist(library_song_id_t libraryId);

	void addSongsToActivePlaylist(
    const std::vector<library_song_id_t>& libraryId);

  /**
   * \brief Removes the specified song from the playlist.
   *
   * @param plId Id of the song to remove the playlist.
   */
	void removeSongFromActivePlaylist(playlist_song_id_t plId);

  void removeSongsFromActivePlaylist(
    const std::vector<playlist_song_id_t>& pl_ids);

  void clearMyLibrary();

  void createNewEvent(
    const QString& name, 
    const QString& password);

  void endEvent();

  

  //@}

/** @name Signals */
//@{
signals:
  void libSongsModified();

  void availableSongsModified();

  void eventCreated();

  void eventCreationFailed(const QString errMessage);

  void eventEnded();

  void eventEndingFailed(const QString errMessage);
 
  void activePlaylistModified();

  void playlistAddRequestsSynced();
//@}

private:
  
  /** @name Private Members */
  //@{

  /** \brief Connection to the UDJ server */
  UDJServerConnection *serverConnection;

  /** \brief Actual database connection */
  QSqlDatabase database;

  QString eventName;

  QTimer *activePlaylistRefreshTimer;
  
  //@}

  /** @name Private Functions */
  //@{

  /** \brief Does initiail database setup */
  void setupDB();

  /** 
   * \brief Adds any songs to the server for which the
   * host client doesn't have valid server_lib_song_id.
   */
  void syncLibrary();

  void syncAvailableMusic();

  void clearActivePlaylist();

  void addSong2ActivePlaylistFromQVariant(
    const QVariantMap &songToAdd, int priority);

  void syncPlaylistAddRequests();


  //@}

  /** @name Private Constants */
  //@{
  /**
   * \brief Retrieves the name of the connection to the musicdb.
   *
   * @return The name of the connection to the musicdb.
   */
  static const QString& getMusicDBConnectionName(){
    static const QString musicDBConnectionName("musicdbConn");
    return musicDBConnectionName;
  }

  /**
   * \brief Retrieves the name of the music database.
   *
   * @return The name of the the music database.
   */
  static const QString& getMusicDBName(){
    static const QString musicDBName("musicdb");
    return musicDBName;
  }



  static const QString& getCreateLibraryQuery(){
    static const QString createLibQuerey = 
      "CREATE TABLE IF NOT EXISTS " + 
      getLibraryTableName() +
      "(" + getLibIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
   	  getLibSongColName() + " TEXT NOT NULL, " +
      getLibArtistColName() + " TEXT NOT NULL, "+
      getLibAlbumColName() + " TEXT NOT NULL, " + 
      getLibFileColName() + " TEXT NOT NULL, " +
      getLibDurationColName() + " INTEGER NOT NULL, "+
      getLibIsDeletedColName() + " INTEGER DEFAULT 0, " + 
      getLibSyncStatusColName() + " INTEGER DEFAULT " +
        QString::number(getLibNeedsAddSyncStatus()) + " " +
      "CHECK("+
        getLibSyncStatusColName()+"="+
          QString::number(getLibIsSyncedStatus()) +" OR " +
        getLibSyncStatusColName()+"="+
          QString::number(getLibNeedsAddSyncStatus()) +" OR " +
        getLibSyncStatusColName()+"="+
          QString::number(getLibNeedsDeleteSyncStatus()) +
      "));";
        
    return createLibQuerey;
  }

  static const QString& getCreatePlaylistTableQuery(){
    static const QString createPlaylistTableQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getPlaylistTableName() + "(" +
      getPlaylistIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
      getPlaylistNameColName() + " TEXT NOT NULL);";
    return createPlaylistTableQuery;
  }

  static const QString& getCreatePlaylistEntryTableQuery(){
    static const QString createPlaylistEntryTableQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getPlaylistEntryTableName() + "(" + 
      getPlaylistEntryIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
      getPlaylistEntrySongIdColName() + " INTEGER REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ ") ON DELETE CASCADE, "+
      getPlaylistEntryNumberColName() + " INTEGER NOT NULL);";
    return createPlaylistEntryTableQuery;
  }

  static const QString& getCreateAvailableMusicQuery(){
    static const QString createAvailableMusicQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getAvailableMusicTableName() + "(" +
      getAvailableEntryLibIdColName() + " INTEGER PRIMARY KEY REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ ") ON DELETE CASCADE," +
      getAvailableEntryIsDeletedColName() + " INTEGER DEFAULT 0, " + 
      getAvailableEntrySyncStatusColName() + " INTEGER DEFAULT " +
        QString::number(getAvailableEntryNeedsAddSyncStatus()) + " " +
      "CHECK("+
        getAvailableEntrySyncStatusColName()+"="+
          QString::number(getAvailableEntryIsSyncedStatus()) +" OR " +
        getAvailableEntrySyncStatusColName()+"="+
          QString::number(getAvailableEntryNeedsAddSyncStatus()) +" OR " +
        getAvailableEntrySyncStatusColName()+"="+
          QString::number(getAvailableEntryNeedsDeleteSyncStatus()) +
      "));";
    return createAvailableMusicQuery;
  }

  static const QString& getCreateActivePlaylistQuery(){
    static const QString createActivePlaylistQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getActivePlaylistTableName() +  "(" +
   	  getActivePlaylistIdColName() + " INTEGER PRIMARY KEY, " +
   	  getActivePlaylistLibIdColName() + " INTEGER REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ ") ON DELETE CASCADE, "+
      getDownVoteColName() + " INTEGER NOT NULL, " +
      getUpVoteColName() + " INTEGER NOT NULL, " +
      getPriorityColName() + " INTEGER NOT NULL, " +
      getAdderIdColName() + " INTEGER NOT NULL, " +
   	  getTimeAddedColName() + " TEXT DEFAULT CURRENT_TIMESTAMP);";
    return createActivePlaylistQuery;
  }

  static const QString& getCreateActivePlaylistViewQuery(){
    static const QString createActivePlaylistViewQuery = 
      "CREATE VIEW IF NOT EXISTS "+getActivePlaylistViewName() + " " + 
      "AS SELECT * , (" + getUpVoteColName() + " - " + getDownVoteColName() +
      ") AS " + getVoteCountColName() + " FROM " + getActivePlaylistTableName()
       + " INNER JOIN " +
      getLibraryTableName() + " ON " + getActivePlaylistTableName() + "." +
      getActivePlaylistLibIdColName() + "=" + getLibraryTableName() + "." +
      getLibIdColName() +" "
      "ORDER BY " +getPriorityColName() + " ASC;";
    return createActivePlaylistViewQuery;
  }

  static const QString& getCreateAvailableMusicViewQuery(){
    static const QString createAvailableMusicViewQuery = 
      "CREATE VIEW IF NOT EXISTS "+getAvailableMusicViewName() + " " + 
      "AS SELECT * FROM " + getAvailableMusicTableName() + " INNER JOIN " +
      getLibraryTableName() + " ON " + getAvailableMusicTableName() + "." +
      getAvailableEntryLibIdColName() + "=" + getLibraryTableName() + "." +
      getLibIdColName() +";";
    return createAvailableMusicViewQuery;
  }

  static const QString& getDeleteAvailableMusicQuery(){
		static const QString deleteAvailableMusicQuery = 
      "DELETE FROM " + getAvailableMusicTableName() + ";";
    return deleteAvailableMusicQuery;
  }

  static const QString& getClearActivePlaylistQuery(){
    static const QString clearActivePlaylistQuery = 
      "DELETE FROM " + getActivePlaylistTableName() + ";";
    return clearActivePlaylistQuery;
  }

  static const QString& getDeleteAddRequestsQuery(){
    static const QString deleteAddRequestsQuery = 
      "DELETE FROM " + getPlaylistAddRequestsTableName() + ";";
    return deleteAddRequestsQuery;
  }


  static const QString& getCreatePlaylistAddRequestsTableQuery(){
    static const QString createPlaylistAddRequestsTableQuery =
      "CREATE TABLE IF NOT EXISTS " + getPlaylistAddRequestsTableName() +
      "(" + getPlaylistAddIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
   	  getPlaylistAddLibIdColName() + " INTEGER REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ 
        ") ON DELETE SET NULL, " +
      getPlaylistAddSycnStatusColName() + " INTEGER DEFAULT " +
        QString::number(getPlaylistAddNeedsSync()) + 
      ");";
    return createPlaylistAddRequestsTableQuery;
  }

 //@}

/** @name Private Slots */
//@{
private slots:
  void setLibSongsSynced(const std::vector<library_song_id_t> songs);
  void setLibSongsSyncStatus(
    const std::vector<library_song_id_t> songs,
    const lib_sync_status_t syncStatus);
  void setAvailableSongsSynced(const std::vector<library_song_id_t> songs);
  void setAvailableSongsSyncStatus(
    const std::vector<library_song_id_t> songs,
    const avail_music_sync_status_t syncStatus);
  void eventCleanUp();
  void setActivePlaylist(const QVariantList newSongs);
  void setPlaylistAddRequestsSynced(const std::vector<client_request_id_t> 
    toSetSynced);
//@}

};


} //end namespace
#endif //DATA_STORE_HPP
