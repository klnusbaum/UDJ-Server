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
#ifndef MUSIC_LIBRARY_HPP
#define MUSIC_LIBRARY_HPP
#include <QSqlDatabase>
#include <phonon/mediaobject.h>
#include <phonon/mediasource.h>
#include <QProgressDialog>
#include "ConfigDefs.hpp"
#include "UDJServerConnection.hpp"

namespace UDJ{


/** \brief A model representing the Hosts Music Library */
class MusicLibrary : public QObject{
Q_OBJECT
public:

  /** @name Constructor(s) and Destructor */
  //@{

  /** \brief Constructs a MusicLibrary
   *
   * @param serverConnection Connection to the UDJ server.
   * @param parent The parent widget.
   */
  MusicLibrary(UDJServerConnection *serverConnection, QObject *parent=0);

  //@}

  /** @name Getters and Setters */
  //@{


  /**
   * \brief Sets the contents of the music library.
   *
   * Sets the hosts music library to a set of given songs. While doing this
   * a progress bar is updated in order to keep the user informed.
   *
   * @param songs Songs which the hosts library should contain.
   * @param progress A progress dialog to be updated as the music library
   * is updated.
   */
  void setMusicLibrary(
    QList<Phonon::MediaSource> songs, 
    QProgressDialog& progress);

  /**
   * \brief Adds a single song to the music library.
   *
   * @param song Song to be added to the library.
   */
  void addSong(Phonon::MediaSource song);

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
	bool addSongToPlaylist(playlist_song_id_t libraryId);

  /**
   * \brief Removes the specified song from the playlist.
   *
   * @param libraryId Id of the song to remove the playlist.
   * @return True if the removal of the song was sucessful, false otherwise.
   */
	bool removeSongFromPlaylist(playlist_song_id_t plId);

  void clearMyLibrary();

  Phonon::MediaSource getNextSongToPlay();
  
  Phonon::MediaSource takeNextSongToPlay();
  
  //@}

  /** @name Public Constants */
  //@{

  static const library_song_id_t& getInvalidHostId(){
    static const library_song_id_t invalidHostId = -1; 
    return invalidHostId;
  }

  static const library_song_id_t& getInvalidServerId(){
    static const library_song_id_t invalidServerId = -1; 
    return invalidServerId;
  }

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
   * about the partiers associated with the server conneciton.
   *
   * @return The name of the table in the musicdb that contains information
   * about the partiers associated with the server connection.
   */
	static const QString& getPartiersTableName(){
		static const QString partiersTableName = "my_partiers";
    return partiersTableName;
	}
  
  static const QString& getPlaylistTableName(){
    static const QString playlistTableName = "playlist";
    return playlistTableName;
  }

  static const QString& getPlaylistViewName(){
    static const QString playlistViewName = "playlist_view";
    return playlistViewName;
  }

  static const QString& getPlaylistIdColName(){
    static const QString playlistIdColName = "id";
    return playlistIdColName;
  }

  static const QString& getPlaylistLibIdColName(){
    static const QString playlistLibIdColName = "lib_id";
    return playlistLibIdColName;
  }

  static const QString& getVoteCountColName(){
    static const QString playlistVoteCountColName = "vote_count";
    return playlistVoteCountColName;
  }

  static const QString& getTimeAddedColName(){
    static const QString playlistTimeAddedColName = "time_added";
    return playlistTimeAddedColName;
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

  static const QString& getServerLibIdColName(){
    static const QString serverLibIdColName = "server_lib_id";
    return serverLibIdColName;
  }

  static const QString getLibSongColName(){
    static const QString libSongColName = "song";
    return libSongColName;
  }

  static const QString getLibArtistColName(){
    static const QString libArtistColName = "artist";
    return libArtistColName;
  }
  
  static const QString getLibAlbumColName(){
    static const QString libAlbumColName = "album";
    return libAlbumColName;
  }

  static const QString getLibFileColName(){
    static const QString libFileColName = "file_path";
    return libFileColName;
  }


 //@}

/** @name Signals */
//@{
signals:
  void songsAdded();
//@}

private:
  
  /** @name Private Members */
  //@{

  /** \brief Connection to the UDJ server */
  UDJServerConnection *serverConnection;
  /** \brief Object used to determine metadata of MediaSources. */
  Phonon::MediaObject* metaDataGetter;
  /** \brief Actual database connection */
  QSqlDatabase database;

  
  //@}

  /** @name Private Functions */
  //@{

  /**
   * \brief Determines the name of a song contained in a given MediaSource.
   *
   * Given a media source, this funciton uses a MediaObject to determine
   * the name of the song in the media source.
   *
   * @param song Song for which the name is desired.
   * @return Name of the given song.
   */
  QString getSongName(Phonon::MediaSource song) const;

  /**
   * \brief Determines the artist of a song contained in a given MediaSource.
   *
   * Given a media source, this funciton uses a MediaObject to determine
   * the artist of the song in the media source.
   *
   * @param song Song for which the artist is desired.
   * @return Artist of the given song.
   */
  QString getArtistName(Phonon::MediaSource song) const;

  /**
   * \brief Determines the album of a song contained in a given MediaSource.
   *
   * Given a media source, this funciton uses a MediaObject to determine
   * the album of the song in the media source.
   *
   * @param song Song for which the album is desired.
   * @return Album of the given song.
   */
  QString getAlbumName(Phonon::MediaSource song) const;

  void setupDB();

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

      getServerLibIdColName() + " INTEGER DEFAULT " + 
        getInvalidServerId() + ", " +

   	  getLibSongColName() + " TEXT NOT NULL, " +
      getLibArtistColName() + " TEXT, "+
      getLibAlbumColName() + " TEXT, " + 
      getLibFileColName() + " TEXT);";
    return createLibQuerey;
  }


  static const QString& getCreatePlaylistQuery(){
    static const QString createPlaylistQuery = 
      "CREATE TABLE IF NOT EXISTS " +
      getPlaylistTableName() +  "(" +
   	  getPlaylistIdColName() + " INTEGER PRIMARY KEY AUTOINCREMENT, " +
   	  getPlaylistLibIdColName() + " INTEGER REFERENCES library(" + 
        getLibIdColName()+ ") ON DELETE CASCADE, " +
   	  getVoteCountColName() + " INTEGER DEFAULT " +getDefaultVoteCount() + "," +
      getPriorityColName() + " INTEGER DEFAULT " +getDefaultPriority() + "," +
   	  getTimeAddedColName() + " TEXT DEFAULT CURRENT_TIMESTAMP);";
    return createPlaylistQuery;
  }

  static const QString& getCreatePlaylistViewQuery(){
    static const QString createPlaylistViewQuery = 
      "CREATE VIEW IF NOT EXISTS "+getPlaylistViewName() + " " + 
      "AS SELECT * FROM " + getPlaylistTableName() + " INNER JOIN " +
      getLibraryTableName() + " ON " + getPlaylistTableName() + "." +
      getPlaylistLibIdColName() + "=" + getLibraryTableName() + "." +
      getLibIdColName() +" " 
      "ORDER BY " +getPriorityColName() + " DESC, " +
      getTimeAddedColName() +" DESC;";
    return createPlaylistViewQuery;
  }

  static const QString& getPlaylistUpdateTriggerName(){
    static const QString playlistUpdateTriggerName = "updateVotes";
    return playlistUpdateTriggerName;
  }

  static const QString& getPlaylistUpdateTriggerQuery(){
    static const QString playlistUpdateTriggerQuery =
  	"CREATE TRIGGER IF NOT EXISTS " +getPlaylistUpdateTriggerName() + " "
    "INSTEAD OF "
    "UPDATE ON " + getPlaylistViewName() + " BEGIN "
    "UPDATE " + getPlaylistTableName() + " SET " + getVoteCountColName() + 
    "=new."+getVoteCountColName() + " "
    "WHERE  " + getPlaylistIdColName() + "=old." + getPlaylistIdColName() +";"
    "END;";
    return playlistUpdateTriggerQuery;
  }

  static const QString& getPlaylistDeleteTriggerName(){
    static const QString playlistDeleteTriggerName = "deleteSongFromPlaylist";
    return playlistDeleteTriggerName;
  }

  static const QString& getPlaylistDeleteTriggerQuery(){
    static const QString playlistDeleteTriggerQuery =
		  "CREATE TRIGGER IF NOT EXISTS " + getPlaylistDeleteTriggerName() + " "
		  "INSTEAD OF DELETE ON " +getPlaylistViewName() +  " "
		  "BEGIN "
		  "DELETE FROM " + getPlaylistTableName() + " "
		  "where " + getPlaylistIdColName() +  " "
      "= old." + getPlaylistIdColName() +";"
		  "END;";
    return playlistDeleteTriggerQuery;
  }

  static const QString& getPlaylistInsertTriggerName(){
    static const QString playlistInsertTriggerName = "insertSongInPlaylist";
    return playlistInsertTriggerName;
  }

  static const QString& getPlaylistInsertTriggerQuery(){
    static const QString playlistInsertTriggerQuery = 
  	"CREATE TRIGGER IF NOT EXISTS " + getPlaylistInsertTriggerName() + " "
    "INSTEAD OF "
    "INSERT ON " + getPlaylistViewName() + " BEGIN "
    "INSERT INTO " + getPlaylistTableName() + " "
    "(" + getPlaylistLibIdColName() + ") VALUES (new." +
    getPlaylistLibIdColName() + ");"
    "END;";
    return playlistInsertTriggerQuery;
  }

 //@}

/** @name Private Slots */
//@{
private slots:
  void updateServerIds(const std::map<library_song_id_t, library_song_id_t> 
    hostToServerIdMap);
//@}
};


} //end namespace
#endif //MUSIC_LIBRARY_HPP
