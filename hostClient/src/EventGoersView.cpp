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
#include "EventGoersView.hpp"
#include "DataStore.hpp"
#include <QSqlQueryModel>
#include <QAction>
#include <QMenu>
#include <QModelIndex>
#include <QSqlRecord>
#include <QHeaderView>


namespace UDJ{


EventGoersView::EventGoersView(DataStore *dataStore, QWidget *parent):
  QTableView(parent),
  dataStore(dataStore)
{
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  eventGoersModel = new QSqlQueryModel(this);
  setModel(eventGoersModel);
  verticalHeader()->hide();
  horizontalHeader()->setStretchLastSection(true);
  setSelectionBehavior(QAbstractItemView::SelectRows);
  setContextMenuPolicy(Qt::CustomContextMenu);
  connect(dataStore, SIGNAL(eventGoersModified()), this, SLOT(refresh()));
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
  refresh();
  configHeaders();
}

void EventGoersView::configHeaders(){
  QSqlRecord record = eventGoersModel->record();
  int usernameIndex = record.indexOf(DataStore::getEventGoerUsernameColName());
  int idIndex = record.indexOf(DataStore::getEventGoersIdColName());
  setColumnHidden(idIndex, true);
  eventGoersModel->setHeaderData(
    usernameIndex, Qt::Horizontal, tr("User"), Qt::DisplayRole);
}

void EventGoersView::handleContextMenuRequest(const QPoint &pos){
  /*QMenu contextMenu(this);
  contextMenu.addAction(addToActivePlaylist);
  contextMenu.addAction(removeFromAvailableMusic);
  contextMenu.exec(QCursor::pos());*/
}

void EventGoersView::refresh(){
  eventGoersModel->setQuery(
    "SELECT " + 
    DataStore::getEventGoerUsernameColName() + ", " +
    DataStore::getEventGoersIdColName() +
    " FROM " + DataStore::getEventGoersTableName() + 
    " WHERE " + DataStore::getEventGoerStateColName() + 
    "=\"" + DataStore::getEventGoerInEventState() + "\";",
    dataStore->getDatabaseConnection());
  if(eventGoersModel->lastError().type() != QSqlError::NoError){
    DEBUG_MESSAGE("Event goeres error: " <<eventGoersModel->lastError().text().toStdString())
  }
}

} //end namespace
