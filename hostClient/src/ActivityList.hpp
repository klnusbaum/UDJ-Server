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
#ifndef ACTIVITY_LIST_HPP
#define ACTIVITY_LIST_HPP
#include <QTreeView>
#include "ConfigDefs.hpp"

class QStandardItemModel;

namespace UDJ{


class MusicLibrary;

class ActivityList : public QTreeView{
Q_OBJECT
public:
  ActivityList(MusicLibrary *library, QWidget *parent=0);

signals:
  void libraryClicked();
  void eventClicked();
  void playlistClicked(playlistid_t playlistId);

private:
  static const QString& getLibraryTitle(){
    static const QString libraryTitle(tr("Library"));
    return libraryTitle;
  }

  static const QString& getEventTitle(){
    static const QString eventTitle(tr("Event"));
    return eventTitle;
  }

  static const QString& getPlaylistTitle(){
    static const QString playlistTitle(tr("Playlist"));
    return playlistTitle;
  }

  MusicLibrary *library;
  QStandardItemModel *model;
  void setupUi();
private slots:
  void itemClicked(const QModelIndex& index);
};


}//end namespace UDJ
#endif //ACTIVITY_LIST_HPP
