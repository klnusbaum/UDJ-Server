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
#ifndef UDJ_SERVER_CONNECTION_HPP
#define UDJ_SERVER_CONNECTION_HPP

#include "ConfigDefs.hpp"
#include <QSqlDatabase>
#include <QObject>

namespace UDJ{


class UDJServerConnection : public QObject{
Q_OBJECT
public:
	UDJServerConnection();
	~UDJServerConnection();
	void startConnection();
	inline QSqlDatabase getMusicDB(){
		return musicdb;
	}	
	inline int getPartyId(){
		return partyId;
	}

	inline QString getLibraryTableName(){
		return "library";
	}

	inline QString getMainPlaylistTableName(){
		return "main_playlist_view";
	}

	inline QString getPartiersTableName(){
		return "my_partiers";
	}

	bool addSongToLibrary(
		const QString& songName,
		const QString& artistName,
		const QString& ablumName,
		const QString& filePath);
	
	bool clearMyLibrary();
	
	bool incrementVoteCount(int plId, int difference);

	bool addSongToPlaylist(int libraryId);

	bool removeSongFromPlaylist(int plId);

signals:
	void partierLeft(int partierId);
	void partierJoined(int partierId);
	void songAddedToMainPlaylist(int libraryId);
	void voteCountChanged(int playlistId);
private:
	QSqlDatabase musicdb;
  static const QString& getMusicDBConnectionName(){
    static const QString musicDBConnectionName("musicdbConn");
    return musicDBConnectionName;
  }

  static const QString& getMusicDBName(){
    static const QString musicDBName("musicdb");
    return musicDBName;
  }
	int partyId;
};


} //end namespace
#endif //UDJ_SERVER_CONNECTION_HPP
