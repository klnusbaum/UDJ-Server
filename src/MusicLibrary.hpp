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
#include <QSqlTableModel>
#include <QSqlDatabase>
#include <phonon/mediaobject.h>
#include <phonon/mediasource.h>
#include <QProgressDialog>
#include "ConfigDefs.hpp"
#include "UDJServerConnection.hpp"

namespace UDJ{


class MusicLibrary : public QSqlTableModel{
Q_OBJECT
public:
  MusicLibrary(QSqlDatabase musicdb, UDJServerConnection* serverConnection, QWidget* parent=0);
  ~MusicLibrary();

  void setMusicLibrary(QList<Phonon::MediaSource> songs, QProgressDialog& progress);

  void addSong(Phonon::MediaSource song);

private:
  Phonon::MediaObject* metaDataGetter;
	UDJServerConnection* serverConnection;
  
  QString getSongName(Phonon::MediaSource song) const;
  QString getArtistName(Phonon::MediaSource song) const;
  QString getAlbumName(Phonon::MediaSource song) const;
};


} //end namespace
#endif //MUSIC_LIBRARY_HPP
