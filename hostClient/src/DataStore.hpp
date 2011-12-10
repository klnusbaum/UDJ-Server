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

  const QString& getEventName(){
    return eventName;
  }

  event_id_t getEventId(){
    return serverConnection->getEventId();
  }
  
public slots:
  /**
   * \brief Alters the vote count associated with a specific song.
   *
   * @param plId Id of the song whose vote count is to be altered.
   * @param difference The amount by which the vote count should be altered.
   * @return True if the altering was sucessful, false otherwise.
   */
	bool alterVoteCount(playlist_song_id_t plId, int difference);

  /**
   * \brief Adds the specified song to the playlist.
   *
   * @param libraryId Id of the song to add to the playlist.
   * @return True if the addition of the song was sucessful, false otherwise.
   */
	bool addSongToActivePlaylist(playlist_song_id_t libraryId);

  /**
   * \brief Removes the specified song from the playlist.
   *
   * @param libraryId Id of the song to remove the playlist.
   * @return True if the removal of the song was sucessful, false otherwise.
   */
	bool removeSongFromActivePlaylist(playlist_song_id_t plId);

  void clearMyLibrary();

  void createNewEvent(
    const QString& name, 
    const QString& password);

  void endEvent();

  Phonon::MediaSource getNextSongToPlay();
  
  Phonon::MediaSource takeNextSongToPlay();

  //@}

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

  static const QString& getDefaultVoteCount(){
    static const QString defaultVoteCount = "1";
    return defaultVoteCount;
  }

  static const QString& getDefaultPriority(){
    static const QString defaultPriority = "1";
    return defaultPriority;
  }

  static const QString& getLibIdColName(){
    static const QString libIdColName = "id";
    return libIdColName;
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

 //@}

/** @name Signals */
//@{
signals:
  void songsAdded();

  void songsModified();

  void eventCreated();

  void eventCreationFailed(const QString errMessage);

  void eventEnded();

  void eventEndingFailed(const QString errMessage);
//@}

private:
  
  /** @name Private Members */
  //@{

  /** \brief Connection to the UDJ server */
  UDJServerConnection *serverConnection;

  /** \brief Actual database connection */
  QSqlDatabase database;

  QString eventName;

  
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
      getPlaylistEntryIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
      getPlaylistEntrySongIdColName() + " INTEGER REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ ") ON DELETE CASCADE, "+
      getPlaylistEntryNumberColName() + " INTEGER NOT NULL);";
    return createPlaylistEntryTableQuery;
  }

  static const QString& getCreateActivePlaylistQuery(){
    static const QString createActivePlaylistQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getActivePlaylistTableName() +  "(" +
   	  getActivePlaylistIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
   	  getActivePlaylistLibIdColName() + " INTEGER REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ ") ON DELETE CASCADE, "+
   	  getVoteCountColName() + " INTEGER DEFAULT " +getDefaultVoteCount() + "," +
      getPriorityColName() + " INTEGER DEFAULT " +getDefaultPriority() + "," +
   	  getTimeAddedColName() + " TEXT DEFAULT CURRENT_TIMESTAMP);";
    return createActivePlaylistQuery;
  }

  static const QString& getCreateActivePlaylistViewQuery(){
    static const QString createActivePlaylistViewQuery = 
      "CREATE VIEW IF NOT EXISTS "+getActivePlaylistViewName() + " " + 
      "AS SELECT * FROM " + getActivePlaylistTableName() + " INNER JOIN " +
      getLibraryTableName() + " ON " + getActivePlaylistTableName() + "." +
      getActivePlaylistLibIdColName() + "=" + getLibraryTableName() + "." +
      getLibIdColName() +" " 
      "ORDER BY " +getPriorityColName() + " DESC, " +
      getTimeAddedColName() +" DESC;";
    return createActivePlaylistViewQuery;
  }

  static const QString& getActivePlaylistUpdateTriggerName(){
    static const QString activePlaylistUpdateTriggerName = "updateVotes";
    return activePlaylistUpdateTriggerName;
  }

  static const QString& getActivePlaylistUpdateTriggerQuery(){
    static const QString activePlaylistUpdateTriggerQuery =
  	"CREATE TRIGGER IF NOT EXISTS " +getActivePlaylistUpdateTriggerName() + " "
    "INSTEAD OF "
    "UPDATE ON " + getActivePlaylistViewName() + " BEGIN "
    "UPDATE " + getActivePlaylistTableName() + " SET " + getVoteCountColName() +
    "=new."+getVoteCountColName() + " "
    "WHERE  " + getActivePlaylistIdColName() + 
    "=old."+ getActivePlaylistIdColName() + ";"
    "END;";
    return activePlaylistUpdateTriggerQuery;
  }

  static const QString& getActivePlaylistDeleteTriggerName(){
    static const QString activePlaylistDeleteTriggerName = 
      "deleteSongFromActivePlaylist";
    return activePlaylistDeleteTriggerName;
  }

  static const QString& getActivePlaylistDeleteTriggerQuery(){
    static const QString activePlaylistDeleteTriggerQuery =
		  "CREATE TRIGGER IF NOT EXISTS "+ getActivePlaylistDeleteTriggerName()+ " "
		  "INSTEAD OF DELETE ON " +getActivePlaylistViewName() +  " "
		  "BEGIN "
		  "DELETE FROM " + getActivePlaylistTableName() + " "
		  "where " + getActivePlaylistIdColName() +  " "
      "= old." + getActivePlaylistIdColName() +";"
		  "END;";
    return activePlaylistDeleteTriggerQuery;
  }

  static const QString& getActivePlaylistInsertTriggerName(){
    static const QString activePlaylistInsertTriggerName = 
      "insertSongInActivePlaylist";
    return activePlaylistInsertTriggerName;
  }

  static const QString& getActivePlaylistInsertTriggerQuery(){
    static const QString activePlaylistInsertTriggerQuery = 
  	"CREATE TRIGGER IF NOT EXISTS " + getActivePlaylistInsertTriggerName() + " "
    "INSTEAD OF "
    "INSERT ON " + getActivePlaylistViewName() + " BEGIN "
    "INSERT INTO " + getActivePlaylistTableName() + " "
    "(" + getActivePlaylistLibIdColName() + ") VALUES (new." +
    getActivePlaylistLibIdColName() + ");"
    "END;";
    return activePlaylistInsertTriggerQuery;
  }

 //@}

/** @name Private Slots */
//@{
private slots:
  void setLibSongsSynced(const std::vector<library_song_id_t> songs);
  void setLibSongsSyncStatus(
    const std::vector<library_song_id_t> songs,
    const lib_sync_status_t syncStatus);
//@}

};


} //end namespace
#endif //DATA_STORE_HPP
