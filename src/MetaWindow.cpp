#include "MetaWindow.hpp"
#include <QGridLayout>
#include <QTabWidget>
#include <QPushButton>

MetaWindow::MetaWindow(){
  tabs = new QTabWidget(this);
  startPartyButton = new QPushButton(tr("Start The Party!"));
  endPartyButton = new QPushButton(tr("Call it a night."));

  QGridLayout *mainLayout = new QGridLayout; 
  mainLayout->addWidget(tabs,0,0,1,4);
  mainLayout->addWidget(startPartyButton,1,1);
  mainLayout->addWidget(endPartyButton,1,2);
}
