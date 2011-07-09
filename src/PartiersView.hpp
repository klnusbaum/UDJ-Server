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
#ifndef PARTIERS_VIEW_HPP
#define PARTIERS_VIEW_HPP
#include <QTableView>
#include "ConfigDefs.hpp"

class QSqlRelationalTableModel;
class QAction;
class QContextMenuEvent;

namespace UDJ{

class UDJServerConnection;

/** \brief Class for displayins a list of partiers who are currently attending
 * the party.
 */
class PartiersView : public QTableView{
Q_OBJECT
public:
  /** @name Constructor(s) */
  //@{

  /** \brief Constructs a PartiersView.
   * 
   * @param serverConnection The connection to the UDJ server.
   * @param parent The parent widget.
   */
	PartiersView(UDJServerConnection* serverConnection, QWidget* parent=0);

  //@}

protected:

  /** @name Overriden from QWidget */
  //@{

  /** \brief . */
	void contextMenuEvent(QContextMenuEvent* e);

  //@}

private:

  /** @name Private Members */
  //@{

  /** \brief The connection to the UDJ server. */
	UDJServerConnection* serverConnection;

  /** \brief The model backing this view. */
	QSqlRelationalTableModel* partiersModel;

  //@}

  /** @name Private Functions */
  //@{

  /** \brief Retrieves the id of a partier given an index
   *
   * @param index The index corresponding to the partier whose id is desired.
   * @return The id of the desired partier.
   */
	partierid_t getPartierId(const QModelIndex& index) const;

  /**
   * \brief Retrives a list of actions to be displayed in the
   * context menu.
   *
   * @return  A list containing the actions to be displayed in the context 
   * menu.
   */
	QList<QAction*> getContextMenuActions();

  //@}

};

} //end namespace
#endif //PARTIERS_VIEW_HPP
