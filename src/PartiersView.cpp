#include "PartiersView.hpp"
#include "UDJServerConnection.hpp"
#include <QSqlRelationalTableModel>
#include <QHeaderView>

namespace UDJ{

PartiersView::PartiersView(
	UDJServerConnection* serverConnection,
	QWidget* parent):
	QTableView(parent),
	serverConnection(serverConnection)
{
	partiersModel = new QSqlRelationalTableModel(
		this, 
		serverConnection->getMusicDB());
	partiersModel->setTable(serverConnection->getPartiersTableName());
  partiersModel->select();
	//TODO make this more dependent on the data from the server connection
  partiersModel->setHeaderData(0, Qt::Horizontal, "id");
  partiersModel->setHeaderData(1, Qt::Horizontal, "First Name");
	setModel(partiersModel);

	setEditTriggers(QAbstractItemView::NoEditTriggers);
  setSelectionBehavior(QAbstractItemView::SelectRows);
  horizontalHeader()->setStretchLastSection(true);
	setColumnHidden(0,true);
}


} //end namepsace 
