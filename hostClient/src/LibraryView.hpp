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
#ifndef LIBRARY_VIEW_HPP
#define LIBRARY_VIEW_HPP
#include <QTableView>

class QContextMenuEvent;
class QSqlRelationalTableModel;

namespace UDJ{

class DataStore;

/** \brief A class for viewing the current contents of the users music library.
*/
class LibraryView : public QTableView{
Q_OBJECT
public:
	/** @name Constructors */
  //@{

  /** \brief Constructs a LibraryView
   *
   * @param dataStore The data store being used by the applicaiton.
   * @param parent The parent widget
   */
  LibraryView(DataStore *dataStore, QWidget* parent=0);

  //@}
private slots:
  void handleContextMenuRequest(const QPoint &pos);

private:

  DataStore *dataStore;
  QSqlRelationalTableModel *libraryModel;
  QAction *deleteSongAction;
  QAction *addToPlaylistAction;
  QAction *addToAvailableMusicAction;

  void createActions();

  static const QString& getDeleteContextMenuItemName(){
    static const QString deleteContextMenuItemName = tr("Delete");
    return deleteContextMenuItemName;
  }

  static const QString& getAddToPlaylistContextMenuItemName(){
    static const QString addToPlaylistContextMenuItemName = 
      tr("Add to playlist");
    return addToPlaylistContextMenuItemName;
  }

  static const QString& getAddToAvailableContextMenuItemName(){
    static const QString addToAvailableContextMenuItemName = 
      tr("Add to Available Music");
    return addToAvailableContextMenuItemName;
  }

private slots:
  void addSongToAvailableMusic();
  void refresh();
};


}//end namespace
#endif //LIBRARY_VIEW_HPP
