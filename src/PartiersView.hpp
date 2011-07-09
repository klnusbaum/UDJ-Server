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

class PartiersView : public QTableView{
Q_OBJECT
public:
	PartiersView(UDJServerConnection* serverConnection, QWidget* parent=0);
protected:
	void contextMenuEvent(QContextMenuEvent* e);
private:
	UDJServerConnection* serverConnection;
	QSqlRelationalTableModel* partiersModel;

	partierid_t getPartierId(const QModelIndex& index) const;
	QList<QAction*> getContextMenuActions();

};

} //end namespace
#endif //PARTIERS_VIEW_HPP
