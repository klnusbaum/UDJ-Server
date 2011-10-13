#include "PartiersView.hpp"
#include "MusicLibrary.hpp"
#include <QSqlRelationalTableModel>
#include <QHeaderView>
#include <QAction>
#include <QContextMenuEvent>
#include <QMenu>

namespace UDJ{

PartiersView::PartiersView(
	MusicLibrary *musicLibrary,
	QWidget* parent):
	QTableView(parent),
	musicLibrary(musicLibrary)
{
	partiersModel = new QSqlRelationalTableModel(
		this, 
		musicLibrary->getDatabaseConnection());
	partiersModel->setTable(MusicLibrary::getPartiersTableName());
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

void PartiersView::contextMenuEvent(QContextMenuEvent* e){
  int contextRow = rowAt(e->y());
  if(contextRow == -1){
    return;
  }

  QAction* selected = 
    QMenu::exec(getContextMenuActions(), e->globalPos());
  if(selected->text() == "Kick Partier"){
    QModelIndex indexToBoot = indexAt(e->pos());
		partierid_t toBoot = getPartierId(indexToBoot);
		if(musicLibrary->kickUser(toBoot)){
			partiersModel->select();
		}
		else{
			//TODO
			//Tell host that there was a problem kicking ths user.
		}
  }
}

partierid_t PartiersView::getPartierId(const QModelIndex& index) const{
	return partiersModel->data(index.sibling(index.row(),0)).value<partierid_t>();
}

QList<QAction*> PartiersView::getContextMenuActions(){
  QList<QAction*> contextActions;
  contextActions.append(new QAction("Kick Partier", this));
  return contextActions;
}

} //end namepsace 
