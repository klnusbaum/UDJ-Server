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

namespace UDJ{


class MusicLibrary;

class LibraryView : public QTableView{
Q_OBJECT
public:
  LibraryView(MusicLibrary* musicLibrary, QWidget* parent=0);
signals:
  void songAddRequest(const QModelIndex& songToAdd); 
protected:
  void contextMenuEvent(QContextMenuEvent* e);
private:
  QList<QAction*> getContextMenuActions();
};


}//end namespace
#endif //LIBRARY_VIEW_HPP
