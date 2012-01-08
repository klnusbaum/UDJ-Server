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

  QSqlQuery getSongLists() const;

  void setSongListName(song_list_id_t id, const QString& name);

  song_list_id_t insertSongList(const QString& name);

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
		static const QString eventGoersTableName = "event_goers";
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

  static const QString& getAdderUsernameColName(){
    static const QString adderUsernameColName = "adder_username";
    return adderUsernameColName;
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
   * \brief Gets the name of the song list table.
   *
   * @return The name of the song list table.
   */
  static const QString& getSongListTableName(){
    static const QString songListTableName = "song_list";
    return songListTableName;
  }

  /** 
   * \brief Gets the name of the id column in the song list table.
   *
   * @return The name of the id column in the song list table.
   */
  static const QString& getSongListIdColName(){
    static const QString songListIdColName = "id";
    return songListIdColName;
  }

  /** 
   * \brief Gets the name of the name column in the song list table.
   *
   * @return The name of the name column in the song list table.
   */
  static const QString& getSongListNameColName(){
    static const QString songListNameColName = "name";
    return songListNameColName;
  }

  /** 
   * \brief Gets the name of the song list entry table.
   *
   * @return The name of the song list entry table.
   */
  static const QString& getSongListEntryTableName(){
    static const QString songListEntryTableName = "songlist_entry";
    return songListEntryTableName;
  }

  /** 
   * \brief Gets the name of the id column in the song list entry table.
   *
   * @return The name of the id column in the song list entry table.
   */
  static const QString& getSongListEntryIdColName(){
    static const QString songListEntryIdColName = "id";
    return songListEntryIdColName;
  }

  /** 
   * \brief Gets the name of the song id column (the column which refers to the
   * library entry this song list entry corresponds to) in the song list entry 
   * table.
   *
   * @return The name of the song id column in the song list entry table.
   */
  static const QString& getSongListEntrySongIdColName(){
    static const QString songListEntrySongIdColName = "lib_id";
    return songListEntrySongIdColName;
  }

  /** 
   * \brief Gets the name of the song list id column 
   * (the column which refers to the song list in which this entry belongs) 
   * in the song list entry table.
   *
   * @return The name of the song list id column in the song list entry table.
   */
  static const QString& getSongListEntrySongListIdColName(){
    static const QString songListEntrySongListIdColName = "songlist_id";
    return songListEntrySongListIdColName;
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

  static const QString& getEventGoersIdColName(){
    static const QString eventGoersIdColName = "id";
    return eventGoersIdColName;
  }

  static const QString& getEventGoerUsernameColName(){
    static const QString eventGoersUsernameColName = "username";
    return eventGoersUsernameColName;
  }

  static const QString& getEventGoerFirstNameColName(){
    static const QString eventGoerFirstNameColName = "first_name";
    return eventGoerFirstNameColName;
  }

  static const QString& getEventGoerLastNameColName(){
    static const QString eventGoerLastNameColName = "last_name";
    return eventGoerLastNameColName;
  }

  static const QString& getEventGoerStateColName(){
    static const QString eventGoerStateColName = "state";
    return eventGoerStateColName;
  }

  static const QString& getEventGoerInEventState(){
    static const QString inEventState = "IE";
    return inEventState;
  }

  static const QString& getEventGoerLeftEventState(){
    static const QString leftEventState = "LE";
    return leftEventState;
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

  void refreshEventGoers();

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

  void deleteSongList(song_list_id_t songListId);

  void addSongsToSongList(
    song_list_id_t songListId,
    const std::vector<library_song_id_t>& songsToAdd);

  void removeSongsFromSongList(
    const song_list_id_t &songListId,
    const std::vector<library_song_id_t>& songsToRemove);

  void addSongListToAvailableMusic(song_list_id_t songListId);

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

  void eventGoersModified();

  void songListModified(song_list_id_t songListId);

  void songListDeleted(song_list_id_t songListId);

//@}

private:
  
  /** @name Private Members */
  //@{

  /** \brief Connection to the UDJ server */
  UDJServerConnection *serverConnection;

  /** \brief Actual database connection */
  QSqlDatabase database;

  /** \brief Name of current event being hosted. */
  QString eventName;

  /** \brief Timer used to refresh the active playlist. */
  QTimer *activePlaylistRefreshTimer;
  
  QTimer *eventGoerRefreshTimer;
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

  /**
   * \brief Syncs the available music table with the server.
   */
  void syncAvailableMusic();

  /** 
   * \brief Deletes all the entries in the active playlist table.
   */
  void clearActivePlaylist();

  /** 
   * \brief Adds a song to the active playlist table.
   *
   * @param songToAdd A QVariantMap which represents the song to be added to
   * the active playlsit table.
   * @param pritority The priority of the song to be added to the active 
   * playlist. 
   */
  void addSong2ActivePlaylistFromQVariant(
    const QVariantMap &songToAdd, int priority);

  /** 
   * \brief Syncs all the requests for additions to the active playlst.
   */
  void syncPlaylistAddRequests();

  /** 
   * \brief Syncs all the requests for removals from the active playlst.
   */
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

  /** 
   * \brief Gets the query used to create the library table.
   *
   * @return The query used to create the library table.
   */
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

  /** 
   * \brief Gets the query used to create the song list table.
   *
   * @return The query used to create the song list table.
   */
  static const QString& getCreateSongListTableQuery(){
    static const QString createSongListTableQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getSongListTableName() + "(" +
      getSongListIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
      getSongListNameColName() + " TEXT NOT NULL UNIQUE);";
    return createSongListTableQuery;
  }

  /** 
   * \brief Gets the query used to create the song list entry table.
   *
   * @return The query used to create the song list entry table.
   */
  static const QString& getCreateSongListEntryTableQuery(){
    static const QString createSongListEntryTableQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getSongListEntryTableName() + "(" + 
      getSongListEntryIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
      getSongListEntrySongIdColName() + " INTEGER REFERENCES " +
        getLibraryTableName() +"(" + getLibIdColName()+ ") ON DELETE CASCADE, "+
      getSongListEntrySongListIdColName() + " INTEGER REFERENCES " +
        getSongListTableName() +"(" + getSongListIdColName()+ 
        ") ON DELETE CASCADE);";
    return createSongListEntryTableQuery;
  }

  /** 
   * \brief Gets the query used to create the available music table.
   *
   * @return The query used to create the available music table.
   */
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

  /** 
   * \brief Gets the query used to create the active playlist table.
   *
   * @return The query used to create the active playlist table.
   */
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
      getAdderUsernameColName() + " TEXT NOT NULL, " +
   	  getTimeAddedColName() + " TEXT DEFAULT CURRENT_TIMESTAMP);";
    return createActivePlaylistQuery;
  }

  /** 
   * \brief Gets the query used to create the active playlist view (
   * a join between the active playlist and the library table).
   *
   * @return The query used to create the active playlist view.
   */
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

  /** 
   * \brief Gets the query used to create the available music view (a join
   * between the available music table and the library table).
   *
   * @return The query used to create the available music view.
   */
  static const QString& getCreateAvailableMusicViewQuery(){
    static const QString createAvailableMusicViewQuery = 
      "CREATE VIEW IF NOT EXISTS "+getAvailableMusicViewName() + " " + 
      "AS SELECT * FROM " + getAvailableMusicTableName() + " INNER JOIN " +
      getLibraryTableName() + " ON " + getAvailableMusicTableName() + "." +
      getAvailableEntryLibIdColName() + "=" + getLibraryTableName() + "." +
      getLibIdColName() +";";
    return createAvailableMusicViewQuery;
  }

  /**
   * \brief Gets the query used to delete all entries in the available music
   * table.
   *
   * @return The query used to delete all entries in the available music
   * table.
   */
  static const QString& getDeleteAvailableMusicQuery(){
		static const QString deleteAvailableMusicQuery = 
      "DELETE FROM " + getAvailableMusicTableName() + ";";
    return deleteAvailableMusicQuery;
  }

  /**
   * \brief Gets the query used to delete all entries in the active playlist
   * table.
   *
   * @return The query used to delete all entries in the active playlist
   * table.
   */
  static const QString& getClearActivePlaylistQuery(){
    static const QString clearActivePlaylistQuery = 
      "DELETE FROM " + getActivePlaylistTableName() + ";";
    return clearActivePlaylistQuery;
  }

  /**
   * \brief Gets the query used to delete all entries in the active playlist
   * add requests table.
   *
   * @return The query used to delete all entries in the active playlist
   * add requests table.
   */
  static const QString& getDeleteAddRequestsQuery(){
    static const QString deleteAddRequestsQuery = 
      "DELETE FROM " + getPlaylistAddRequestsTableName() + ";";
    return deleteAddRequestsQuery;
  }

  /**
   * \brief Gets the query used to delete all entries in the active playlist
   * remove requests table.
   *
   * @return The query used to delete all entries in the active playlist
   * remove requests table.
   */
  static const QString& getDeleteRemoveRequestsQuery(){
    static const QString deleteRemoveRequestsQuery = 
      "DELETE FROM " + getPlaylistRemoveRequestsTableName() + ";";
    return deleteRemoveRequestsQuery;
  }

  static const QString& getDeleteEventGoersQuery(){
    static const QString deleteEventGoersQuery = 
      "DELETE FROM " + getEventGoersTableName() + ";";
    return deleteEventGoersQuery;
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

  /** 
   * \brief Get the name fo the id column in the playlist add request table.
   *
   * @return The name fo the id column in the playlist add request table.
   */
  static const QString& getPlaylistAddIdColName(){
    static const QString playlistAddIdColName = "addId";
    return playlistAddIdColName;
  }

  /** 
   * \brief Get the name for the lib id column in the playlist add request 
   * table.
   *
   * @return The name fo the lib id column in the playlist add request table.
   */
  static const QString& getPlaylistAddLibIdColName(){
    static const QString playlistAddLibIdColName = "libId";
    return playlistAddLibIdColName;
  }

  /** 
   * \brief Get the name fo the sync status column in the playlist add request 
   * table.
   *
   * @return The name fo the lib sync status column in the playlist add 
   * request table.
   */
  static const QString& getPlaylistAddSycnStatusColName(){
    static const QString playlistAddSyncStatusColName = "sync_status";
    return playlistAddSyncStatusColName;
  }

  /** 
   * \brief Gets the sync status used in the playlist add request table to 
   * indicate that an add needs to be synced.
   *
   * @return The sync status used in the playlist add request table to 
   * indicate that an add needs to be synced.
   */
  static const playlist_add_sync_status_t& getPlaylistAddNeedsSync(){
    static const playlist_add_sync_status_t needsSyncStatus=1;
    return needsSyncStatus;
  }

  /** 
   * \brief Gets the sync status used in the playlist add request table to 
   * indicate that an add is synced.
   *
   * @return The sync status used in the playlist add request table to 
   * indicate that an add is synced.
   */
  static const playlist_add_sync_status_t& getPlaylistAddIsSynced(){
    static const playlist_add_sync_status_t isSynced=0;
    return isSynced;
  }


  /**
   * \brief Gets the query used to create the playlist add request table.
   *
   * @return The query used to create the playlist add request table.
   */
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

  /**
   * Gets the name of the active playlist remove request table.
   *
   * @return the name of the active playlist remove request table.
   */
  static const QString& getPlaylistRemoveRequestsTableName(){
    static const QString playlistRemoveRequestsTableName = 
      "playlist_remove_requests";
    return playlistRemoveRequestsTableName;
  }
 
  /** 
   * \brief Get the name for the lib id column in the playlist remove request 
   * table.
   *
   * @return The name fo the lib id column in the playlist remove request table.
   */
  static const QString& getPlaylistRemoveIdColName(){
    static const QString playlistRemoveRequestIdColName = "id";
    return playlistRemoveRequestIdColName;
  }
  
  /** 
   * \brief Get the name for the lib id column in the playlist remove request 
   * table.
   *
   * @return The name fo the lib id column in the playlist remove request table.
   */
  static const QString& getPlaylistRemoveEntryIdColName(){
    static const QString playlistRemoveLibIdColName = "playlist_id";
    return playlistRemoveLibIdColName;
  }

  /** 
   * \brief Get the name fo the sync status column in the playlist remove 
   * request table.
   *
   * @return The name fo the lib sync status column in the playlist remove 
   * request table.
   */
  static const QString& getPlaylistRemoveSycnStatusColName(){
    static const QString playlistRemoveSycnStatusColName = "sync_status";
    return playlistRemoveSycnStatusColName;
  }

  /** 
   * \brief Gets the sync status used in the playlist edd request table to 
   * indicate that an remove is synced.
   *
   * @return The sync status used in the playlist remove request table to 
   * indicate that an remove is synced.
   */
  static const playlist_remove_sync_status_t& getPlaylistRemoveNeedsSync(){
    static const playlist_remove_sync_status_t needs_sync = 1;
    return needs_sync;
  }

  /** 
   * \brief Gets the sync status used in the playlist remove request table to 
   * indicate that an remove is synced.
   *
   * @return The sync status used in the playlist remove request table to 
   * indicate that an remove is synced.
   */
  static const playlist_remove_sync_status_t& getPlaylistRemoveIsSynced(){
    static const playlist_remove_sync_status_t isSynced = 0;
    return isSynced;
  }

  /**
   * \brief Gets the query used to create the playlist remove request table.
   *
   * @return The query used to create the playlist remove request table.
   */
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




  static const QString& getCreateEventGoersTableQuery(){
    static QString createEventGoersTableQuery = 
      "CREATE TABLE IF NOT EXISTS " + getEventGoersTableName() + 
      "(" + getEventGoersIdColName() + " INTEGER PRIMARY KEY, " + 
      getEventGoerUsernameColName() + " TEXT NOT NULL, " +
      getEventGoerFirstNameColName() + " TEXT, " +
      getEventGoerLastNameColName() + " TEXT, " +
      getEventGoerStateColName() + " TEXT NOT NULL " +
      "CHECK("+
        getEventGoerStateColName()+"=\""+
           getEventGoerInEventState() +"\" OR " +
        getEventGoerStateColName()+"=\""+
           getEventGoerLeftEventState() +"\"" +
      "));";
    return createEventGoersTableQuery;
  }

 //@}

/** @name Private Slots */
//@{
private slots:
  
  /**
   * \brief Sets the sync status of a library song to synced.
   *
   * @param song The id of the song whose sync status should be set to synced.
   */
  void setLibSongSynced(library_song_id_t song);
  
  /**
   * \brief Sets the sync status of the given library songs to synced.
   *
   * @param songs The ids of the songs whose sync status should be set 
   * to synced.
   */
  void setLibSongsSynced(const std::vector<library_song_id_t> songs);
  
  /**
   * \brief Sets the sync status of the given library songs to the given
   * given sync status.
   *
   * @param songs The ids of the songs whose sync status should be set.
   * @param syncStatus The sync status to which the given songs should be set. 
   */
  void setLibSongsSyncStatus(
    const std::vector<library_song_id_t> songs,
    const lib_sync_status_t syncStatus);
  
  /**
   * \brief Sets the sync status of an available song entry to synced.
   *
   * @param song The id of the song whose sync status should be set to synced.
   */
  void setAvailableSongSynced(const library_song_id_t songs);
  
  /**
   * \brief Sets the sync statuses of the give available song entries to synced.
   *
   * @param songs The ids of the songs whose sync status should be set to 
   * synced.
   */
  void setAvailableSongsSynced(const std::vector<library_song_id_t> songs);
  
  /**
   * \brief Sets the sync statuses of the give available song entries to the
   * given sync status.
   *
   * @param songs The ids of the songs whose sync status should be set.
   * @param syncStatus The sync status to which the songs should be set.
   */
  void setAvailableSongsSyncStatus(
    const std::vector<library_song_id_t> songs,
    const avail_music_sync_status_t syncStatus);
  
  /**
   * \brief Preforms certain cleanup operations once an event has ended.
   */
  void eventCleanUp();
  
  /**
   * \brief Sets the active playlist to the given songs.
   *
   * @param newSongs The new songs which should populate the active playlist.
   */
  void setActivePlaylist(const QVariantList newSongs);

  /**
   * \brief Sets the given playlist add request sync statuses' to sycned.
   *
   * @param toSetSynced The add request whose sync statuses' should be set
   * to synced.
   */
  void setPlaylistAddRequestsSynced(const std::vector<client_request_id_t> 
    toSetSynced);

  /**
   * \brief Sets the given playlist remove request sync statuses' to sycned.
   *
   * @param toSetSynced The remove request whose sync statuses' should be set
   * to synced.
   */
  void setPlaylistRemoveRequestSynced(const playlist_song_id_t id);

  void processNewEventGoers(QVariantList newEventGoers);

  void addOrInsertEventGoer(const QVariantMap& eventGoer);

  bool alreadyHaveEventGoer(user_id_t id);

  void updateEventGoer(const QVariantMap &eventGoer);

  void insertEventGoer(const QVariantMap &eventGoer);

  
//@}

};


} //end namespace
#endif //DATA_STORE_HPP
