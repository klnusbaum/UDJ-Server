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
#ifndef EVENT_GOERS_VIEW_HPP
#define EVENT_GOERS_VIEW_HPP
#include <QTableView>
#include "ConfigDefs.hpp"

class QSqlQueryModel;
class QAction;

namespace UDJ{

class DataStore;

/**
 * \brief Used to dislay the active playlist.
 */
class EventGoersView : public QTableView{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an EventGoersView.
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  EventGoersView(DataStore *dataStore, QWidget *parent=0);

  //@}

private:
  /** @name Private Memeber */
  //@{

  /**
   * \brief The data store containing music that could potentially be added
   * to the playlist.
   */
  DataStore *dataStore;
 
  /** \brief The model backing this view. */
  QSqlQueryModel *eventGoersModel;  

  //@}

  /** @name Private Functions */
  //@{
 
private slots:
  /** @name Private Slots */
  //@{

  /** 
   * \brief Updates the data being displayed in the view.
   */
  void refresh();

  /**
   * \brief Displays context menus when requested.
   *
   * @param pos The position where the context menu should be displayed.
   */ 
  void handleContextMenuRequest(const QPoint &pos);

  void configHeaders();

  //@}
};


} //end namespace
#endif // EVENT_GOERS_VIEW_HPP

