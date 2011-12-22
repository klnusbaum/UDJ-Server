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
   * \brief Removes the given songs from the music library. 
   *
   * @param toRemove The list of songs to be removed from the library.
   */
  void removeSongsFromLibrary(std::vector<library_song_id_t> toRemove);

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

  /**
   * \brief Gets the raw connection to the actual database that the DataStore
   * uses.
   *
   * @return The connection to the database backing the DataStore.
   */
  QSqlDatabase getDatabaseConnection();

  /** 
   * \brief Gets the name of the current event.
   *
   * @return The name of the current event.
   */
  inline const QString& getEventName() const{
    return eventName;
  }

  /** 
   * \brief Gets the id of the current event.
   *
   * @return The id of the current event.
   */
  inline event_id_t getEventId() const{
    return serverConnection->getEventId();
  }

  /** 
   * \brief Gets whether or not this instance of UDJ is currently hosting an
   * event.
   *
   * @return True if this instance of UDJ is currently hosting an event. 
   * False otherwise.
   */
  inline bool isCurrentlyHosting() const{
    return serverConnection->getIsHosting();
  }

  /** 
   * \brief Retrieves the next song should be played but does not
   * remove it from the active playlist.
   *
   * @return The next song that is going to be played.
   */
  Phonon::MediaSource getNextSongToPlay();
  
  /** 
   * \brief Retrieves the next song that should be played and removes it
   * from the active playlist.
   *
   * @return The next song that should be played.
   */
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
  
  /** 
   * \brief Gets name of the table storing the active playlist.
   *
   * @return The name of the table containing the active playlist.
   */
  static const QString& getActivePlaylistTableName(){
    static const QString activePlaylistTableName = "active_playlist";
    return activePlaylistTableName;
  }

  /** 
   * \brief Gets name of the view containing the active playlist joined with
   * the library table.
   *
   * @return The view containing the active playlist joined with the library
   * table.
   */
  static const QString& getActivePlaylistViewName(){
    static const QString activePlaylistViewName = "active_playlist_view";
    return activePlaylistViewName;
  }

  /**
   * \brief Gets the name of the id column in the active playlist table.
   *
   * @return The name of the id colum in the active playlist table.
   */
  static const QString& getActivePlaylistIdColName(){
    static const QString activePlaylistIdColName = "id";
    return activePlaylistIdColName;
  }

  /** 
   * \brief Gets the name of the library id column (the column that specifies
   * which library entry this playlist entry corresponds with) in the active
   * playlist table.
   *
   * @return The name of the library id column  in the active playlist table.
   */
  static const QString& getActivePlaylistLibIdColName(){
    static const QString activePlaylistLibIdColName = "lib_id";
    return activePlaylistLibIdColName;
  }

  /** 
   * \brief Gets the name of the column in the active playlist view that 
   * contains the vote count.
   *
   * @return The name of the column in the active playlist view that 
   * contains the vote count.
   */
  static const QString& getVoteCountColName(){
    static const QString voteCountColName = "vote_count";
    return voteCountColName;
  }

  /** 
   * \brief Gets the name of the time added column in the active playlist table.
   *
   * @return The name of the time added column in the active playlist table.
   */
  static const QString& getTimeAddedColName(){
    static const QString timeAddedColName = "time_added";
    return timeAddedColName;
  }

  /** 
   * \brief Gets the name of the priority column in the active playlist table.
   *
   * @return The name of the priority column in the active playlist table.
   */
  static const QString& getPriorityColName(){
    static const QString priorityColName = "priority";
    return priorityColName;
  }

  /** 
   * \brief Gets the name of the adder id column in the active playlist table.
   *
   * @return The name of the adder id column in the active playlist table.
   */
  static const QString& getAdderIdColName(){
    static const QString adderIdColName = "adderId";
    return adderIdColName;
  }

  /** 
   * \brief Gets the name of the upvote column in the active playlist table.
   *
   * @return The name of the upvote column in the active playlist table.
   */
  static const QString& getUpVoteColName(){
    static const QString upVoteColName = "up_votes";
    return upVoteColName;
  }

  /** 
   * \brief Gets the name of the downvote column in the active playlist table.
   *
   * @return The name of the downvote column in the active playlist table.
   */
  static const QString& getDownVoteColName(){
    static const QString downVoteColName = "down_votes";
    return downVoteColName;
  }

  /** 
   * \brief Gets the id column in the library table table.
   *
   * @return The name of the id column in the library table.
   */
  static const QString& getLibIdColName(){
    static const QString libIdColName = "id";
    return libIdColName;
  }

  /** 
   * \brief Gets the song column in the library table table.
   *
   * @return The name of the song column in the library table.
   */
  static const QString& getLibSongColName(){
    static const QString libSongColName = "song";
    return libSongColName;
  }

  /** 
   * \brief Gets the artist column in the library table table.
   *
   * @return The name of the artist column in the library table.
   */
  static const QString& getLibArtistColName(){
    static const QString libArtistColName = "artist";
    return libArtistColName;
  }
  
  /** 
   * \brief Gets the album column in the library table table.
   *
   * @return The name of the album column in the library table.
   */
  static const QString& getLibAlbumColName(){
    static const QString libAlbumColName = "album";
    return libAlbumColName;
  }

  /** 
   * \brief Gets the file column in the library table table.
   *
   * @return The name of the file column in the library table.
   */
  static const QString& getLibFileColName(){
    static const QString libFileColName = "file_path";
    return libFileColName;
  }

  /** 
   * \brief Gets the duration column in the library table table.
   *
   * @return The name of the duration column in the library table.
   */
  static const QString& getLibDurationColName(){
    static const QString libDurationColName = "duration";
    return libDurationColName;
  }

  /** 
   * \brief Gets the is deleted column in the library table table.
   *
   * @return The name of the is deleted column in the library table.
   */
  static const QString& getLibIsDeletedColName(){
    static const QString libIsDeletedColName = "is_deleted";
    return libIsDeletedColName;
  }

  /** 
   * \brief Gets the sycn status column in the library table table.
   *
   * @return The name of the sycn status column in the library table.
   */
  static const QString& getLibSyncStatusColName(){
    static const QString libSyncStatusColName = "sync_status";
    return libSyncStatusColName;
  }

  /** 
   * \brief Gets the value for the "needs add" sync status used in the library
   * table.
   *
   * @return The value for the "needs add" sync status used in the library
   * table.
   */
  static const lib_sync_status_t& getLibNeedsAddSyncStatus(){
    static const lib_sync_status_t libNeedsAddSyncStatus = 1;
    return libNeedsAddSyncStatus;
  }

  /** 
   * \brief Gets the value for the "needs delete" sync status used in the 
   * library table.
   *
   * @return The value for the "needs delete" sync status used in the library
   * table.
   */
  static const lib_sync_status_t& getLibNeedsDeleteSyncStatus(){
    static const lib_sync_status_t libNeedsDeleteSyncStatus = 2;
    return libNeedsDeleteSyncStatus;
  }

  /** 
   * \brief Gets the value for the "is synced" sync status used in the library
   * table.
   *
   * @return The value for the "is synced" sync status used in the library
   * table.
   */
  static const lib_sync_status_t& getLibIsSyncedStatus(){
    static const lib_sync_status_t libIsSyncedStatus = 0;
    return libIsSyncedStatus;
  }
  
  /** 
   * \brief Gets the name of the playlist table.
   *
   * @return The name of the playlist table.
   */
  static const QString& getPlaylistTableName(){
    static const QString playlistTableName = "playlist";
    return playlistTableName;
  }

  /** 
   * \brief Gets the name of the id column in the playlist table.
   *
   * @return The name of the id column in the playlist table.
   */
  static const QString& getPlaylistIdColName(){
    static const QString playlistIdColName = "id";
    return playlistIdColName;
  }

  /** 
   * \brief Gets the name of the name column in the playlist table.
   *
   * @return The name of the name column in the playlist table.
   */
  static const QString& getPlaylistNameColName(){
    static const QString playlistNameColName = "name";
    return playlistNameColName;
  }

  /** 
   * \brief Gets the name of the playlist entry table.
   *
   * @return The name of the playlist entry table.
   */
  static const QString& getPlaylistEntryTableName(){
    static const QString playlistEntryTableName = "playlist_entry";
    return playlistEntryTableName;
  }

  /** 
   * \brief Gets the name of the id column in the playlist entry table.
   *
   * @return The name of the id column in the playlist entry table.
   */
  static const QString& getPlaylistEntryIdColName(){
    static const QString playlistEntryIdColName = "id";
    return playlistEntryIdColName;
  }

  /** 
   * \brief Gets the name of the song id column (the column which refers to the
   * library entry this playlist entry corresponds to) in the playlist entry 
   * table.
   *
   * @return The name of the song id column in the playlist entry table.
   */
  static const QString& getPlaylistEntrySongIdColName(){
    static const QString playlistEntrySongIdColName = "lib_id";
    return playlistEntrySongIdColName;
  }

  /** 
   * \brief Gets the name of the playlist id column 
   * (the column which refers to the playlist in which this entry belongs) 
   * in the playlist entry table.
   *
   * @return The name of the playlist id column in the playlist entry table.
   */
  static const QString& getPlaylistEntryPlaylistIdColName(){
    static const QString playlistEntryPlaylistIdColName = "playlist_id";
    return playlistEntryPlaylistIdColName;
  }

  /** 
   * \brief Gets the name of the entry number column (effectively the column
   * which determines order in a give playlist) in the playlist entry 
   * table.
   *
   * @return The name of the entry number column in the playlist entry table.
   */
  static const QString& getPlaylistEntryNumberColName(){
    static const QString playlistEntryNumberColName = "entry_number";
    return playlistEntryNumberColName;
  }

  /** 
   * \brief Get the name of the available music table.
   *
   * \brief The name of the available music table.
   */
  static const QString& getAvailableMusicTableName(){
    static const QString availableMusicTableName = "available_music";
    return availableMusicTableName;
  }

  /** 
   * \brief Get the name of the library id column. This is the column which 
   * connects * a particular record in the available entry table to the 
   * corresponding entry in the library table.
   *
   * @return The name of the library id column.
   */
  static const QString& getAvailableEntryLibIdColName(){
    static const QString availableEntryLibIdColName = "lib_id";
    return availableEntryLibIdColName;
  }

  /** 
   * \brief Get the name of the "is deleted" column.
   *
   * @return The name of the "is deleted" column.
   */
  static const QString& getAvailableEntryIsDeletedColName(){
    static const QString availEntryIsDeletedColName = "is_deleted";
    return availEntryIsDeletedColName;
  }

  /** 
   * \brief Get the name of the sync status column.
   *
   * @return The name of the sync status column.
   */
  static const QString& getAvailableEntrySyncStatusColName(){
    static const QString availEntrySyncStatusColName = "sync_status";
    return availEntrySyncStatusColName;
  }

  /**
   * \brief Gets the availabe music entry "needs add" sync status.
   *
   * @return The availabe music entry "needs add" sync status.
   */
  static const avail_music_sync_status_t& getAvailableEntryNeedsAddSyncStatus(){
    static const avail_music_sync_status_t availEntryNeedsAddSyncStatus = 1;
    return availEntryNeedsAddSyncStatus;
  }

  /**
   * \brief Gets the availabe music entry "needs delete" sync status.
   *
   * @return The availabe music entry "needs delete" sync status.
   */
  static const avail_music_sync_status_t& 
    getAvailableEntryNeedsDeleteSyncStatus()
  {
    static const avail_music_sync_status_t availEntryNeedsDeleteSyncStatus = 2;
    return availEntryNeedsDeleteSyncStatus;
  }

  /**
   * \brief Gets the availabe music entry "is sycned" sync status.
   *
   * @return The availabe music entry "is sycned" sync status.
   */
  static const avail_music_sync_status_t& getAvailableEntryIsSyncedStatus(){
    static const avail_music_sync_status_t availEntryIsSyncedStatus = 0;
    return availEntryIsSyncedStatus;
  }

  /**
   * \brief Gets the name of the available music view. This is a view which is a
   * join between the available music table and the library table.
   *
   * @return The name of the available music view.
   */
  static const QString& getAvailableMusicViewName(){
    static const QString availableMusicViewName ="available_music_view";
    return availableMusicViewName;
  }


 //@}

/** @name Public slots */
//@{
public slots:

  /**
   * \brief Add the given song to the list of available songs.
   *
   * @param song_id The id of the song to be added to the list of available 
   * songs.
   */
  void addSongToAvailableSongs(library_song_id_t song_id);

  /**
   * \brief Add a list of songs to the list of available songs.
   *
   * @param song_ids The ids of the songs to be added to the list of available 
   * songs.
   */
  void addSongsToAvailableSongs(const std::vector<library_song_id_t>& song_ids);

  /**
   * \brief Refresh the active playlist table.
   */
  void refreshActivePlaylist();

  /**
   * \brief Adds the specified song to the playlist.
   *
   * @param libraryId Id of the song to add to the playlist.
   */
	void addSongToActivePlaylist(library_song_id_t libraryId);

  /** 
   * \brief Add the given songs to the active playlist.
   *
   * @param libraryIds The ids of the songs to be added to the active playlist.
   */
	void addSongsToActivePlaylist(
    const std::vector<library_song_id_t>& libraryIds);

  /** 
   * \brief Remove the given songs to the list of available songs.
   *
   * @param libraryIds The ids of the songs to be removed to the 
   * the list of available songs.
   */
  void removeSongsFromAvailableMusic(
    const std::vector<library_song_id_t>& libraryIds);

  /**
   * \brief Removes the specified song from the active playlist.
   *
   * @param plId Id of the song to remove from the active playlist.
   */
	void removeSongFromActivePlaylist(playlist_song_id_t plId);

  /**
   * \brief Removes the specified songs from the active playlist.
   *
   * @param pl_ids Ids of the songs to be removed from the active playlist.
   */
  void removeSongsFromActivePlaylist(
    const std::vector<playlist_song_id_t>& pl_ids);

  /** 
   * \brief Creates a new event with the given name and password.
   *
   * @param name The name of the event.
   * @param password The password for the event (maybe empty).
   */
  void createNewEvent(
    const QString& name, 
    const QString& password);

  /** 
   * \brief Ends the current event.
   */
  void endEvent();

  /** 
   * \brief Sets the current song to the speicified song.
   *
   * @param songToPlay The playlist id of the song to be played.
   */
  void setCurrentSong(playlist_song_id_t songToPlay);

  //@}

signals:

/** @name Signals */
//@{

  /**
   * \brief Emitted when the library table is modified.
   */
  void libSongsModified();

  /**
   * \brief Emitted when the list of available songs is modified.
   */
  void availableSongsModified();

  /**
   * \brief Emitted when an event is created.
   */
  void eventCreated();

  /**
   * \brief Emitted when the creation of an event fails.
   *
   * @param errMessage Error message describing what happened.
   */
  void eventCreationFailed(const QString errMessage);

  /**
   * \brief Emitted when the event ends.
   */
  void eventEnded();

  /**
   * \brief Emitted when ending an event fails.
   */
  void eventEndingFailed(const QString errMessage);
 
  /**
   * \brief Emitted when the active playlist is modified.
   */
  void activePlaylistModified();

  /**
   * \brief Emitted when the current song is manually changed.
   *
   * @param newSong The song that should be set as the current song.
   */
  void manualSongChange(Phonon::MediaSource newSong);

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

  void syncPlaylistRemoveRequests();


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
      getPlaylistEntryPlaylistIdColName() + " INTEGER REFERENCES " +
        getPlaylistTableName() +"(" + getPlaylistIdColName()+ 
        ") ON DELETE CASCADE, "+
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

  /**
   * Gets the name of the active playlist add request table.
   *
   * @return the name of the active playlist add request table.
   */
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


  static const QString& getCreatePlaylistAddRequestsTableQuery(){
    static const QString createPlaylistAddRequestsTableQuery =
      "CREATE TABLE IF NOT EXISTS " + getPlaylistAddRequestsTableName() +
      "(" + getPlaylistAddIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
   	  getPlaylistAddLibIdColName() + " INTEGER REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ 
        ") ON DELETE SET NULL , " +
      getPlaylistAddSycnStatusColName() + " INTEGER DEFAULT " +
        QString::number(getPlaylistAddNeedsSync()) + 
      ");";
    return createPlaylistAddRequestsTableQuery;
  }

  static const QString& getPlaylistRemoveRequestsTableName(){
    static const QString playlistRemoveRequestsTableName = 
      "playlist_remove_requests";
    return playlistRemoveRequestsTableName;
  }
 
  static const QString& getPlaylistRemoveIdColName(){
    static const QString playlistRemoveRequestIdColName = "id";
    return playlistRemoveRequestIdColName;
  }
  
  static const QString& getPlaylistRemoveEntryIdColName(){
    static const QString playlistRemoveLibIdColName = "playlist_id";
    return playlistRemoveLibIdColName;
  }

  static const QString& getPlaylistRemoveSycnStatusColName(){
    static const QString playlistRemoveSycnStatusColName = "sync_status";
    return playlistRemoveSycnStatusColName;
  }

  static const playlist_remove_sync_status_t& getPlaylistRemoveNeedsSync(){
    static const playlist_remove_sync_status_t needs_sync = 1;
    return needs_sync;
  }

  static const playlist_remove_sync_status_t& getPlaylistRemoveIsSynced(){
    static const playlist_remove_sync_status_t isSynced = 0;
    return isSynced;
  }

  static const QString& getCreatePlaylistRemoveRequestsTableQuery(){
    static const QString createPlaylistRemoveRequestsTableQuery =
      "CREATE TABLE IF NOT EXISTS " + getPlaylistRemoveRequestsTableName() +
      "(" + getPlaylistRemoveIdColName() + 
         " INTEGER PRIMARY KEY AUTOINCREMENT, " +
   	  getPlaylistRemoveEntryIdColName() + " INTEGER UNIQUE, " +
      getPlaylistRemoveSycnStatusColName() + " INTEGER DEFAULT " +
        QString::number(getPlaylistRemoveNeedsSync()) + 
      ");";
    return createPlaylistRemoveRequestsTableQuery;
  }

 //@}

/** @name Private Slots */
//@{
private slots:
  void setLibSongSynced(library_song_id_t song);
  void setLibSongsSynced(const std::vector<library_song_id_t> songs);
  void setLibSongsSyncStatus(
    const std::vector<library_song_id_t> songs,
    const lib_sync_status_t syncStatus);
  void setAvailableSongSynced(const library_song_id_t songs);
  void setAvailableSongsSynced(const std::vector<library_song_id_t> songs);
  void setAvailableSongsSyncStatus(
    const std::vector<library_song_id_t> songs,
    const avail_music_sync_status_t syncStatus);
  void eventCleanUp();
  void setActivePlaylist(const QVariantList newSongs);
  void setPlaylistAddRequestsSynced(const std::vector<client_request_id_t> 
    toSetSynced);
  void setPlaylistRemoveRequestSynced(const playlist_song_id_t id);
//@}

};


} //end namespace
#endif //DATA_STORE_HPP
