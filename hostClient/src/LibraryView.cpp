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
#include "MusicLibrary.hpp"
#include "LibraryView.hpp"
#include <QHeaderView>
#include <QContextMenuEvent>
#include <QMenu>
#include "LibraryModel.hpp"
	

namespace UDJ{


LibraryView::LibraryView(LibraryModel *model, QWidget* parent):QTableView(parent){
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  verticalHeader()->hide();
  horizontalHeader()->setStretchLastSection(true);
  setModel(model);
  setSelectionBehavior(QAbstractItemView::SelectRows);
}

void LibraryView::contextMenuEvent(QContextMenuEvent* e){
  int contextRow = rowAt(e->y());
  if(contextRow == -1){
    return;
  }

  QAction* selected = 
    QMenu::exec(getContextMenuActions(), e->globalPos());
  if(selected->text() == getAddToPlaylistText()){
    QModelIndex indexToAdd = indexAt(e->pos());
    emit songAddRequest(indexToAdd);
  }

}

QList<QAction*> LibraryView::getContextMenuActions(){
  QList<QAction*> contextActions;
  contextActions.append(new QAction(getAddToPlaylistText(), this));
  return contextActions;
}


}//end namespace
