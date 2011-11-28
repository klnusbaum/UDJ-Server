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
  setContextMenuPolicy(Qt::CustomContextMenu);
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
}

void LibraryView::handleContextMenuRequest(const QPoint &pos){
  QMenu contextMenu(this);
  contextMenu.addAction(getDeleteContextMenuItemName());
  QAction *returnedHaction = contextMenu.exec(QCursor::pos());


}


}//end namespace
