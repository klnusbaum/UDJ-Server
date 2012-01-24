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
#include "EventWidget.hpp"
#include "EventDashboard.hpp"
#include "DataStore.hpp"
#include "ActivePlaylistView.hpp"
#include "AvailableMusicView.hpp"
#include "EventGoersView.hpp"
#include <QLabel>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>
#include <QMessageBox>
#include <QTabWidget>

namespace UDJ{


EventDashboard::EventDashboard(DataStore *dataStore, QWidget *parent)
  :WidgetWithLoader(tr("Ending event..."),parent),
  dataStore(dataStore)
{
  setupUi();
  connect(dataStore, SIGNAL(eventCreated()), this, SLOT(updateEventInfo()));
}


void EventDashboard::setupUi(){
  mainContent = new QWidget(this);
  QVBoxLayout *layout = new QVBoxLayout;
  QHBoxLayout *header = new QHBoxLayout;
  QVBoxLayout *eventInfo = new QVBoxLayout;


  eventName = new QLabel();
  eventId = new QLabel();

  if(dataStore->isCurrentlyHosting()){
    eventName->setText(dataStore->getEventName());
    eventId->setText(QString::number(dataStore->getEventId()));
  }

  eventInfo->addWidget(eventName);
  eventInfo->addWidget(eventId);
  
  QPushButton *stopEventButton = new QPushButton(tr("Stop Event"));
  QPushButton *refreshPlaylist = new QPushButton(tr("Playist Refresh"));
  connect(stopEventButton, SIGNAL(clicked()), this, SLOT(endEvent()));
  connect(
    refreshPlaylist, 
    SIGNAL(clicked()), 
    dataStore, 
    SLOT(refreshActivePlaylist())
  );
  header->addLayout(eventInfo);
  header->addStretch();
  header->addWidget(stopEventButton);
  header->addWidget(refreshPlaylist);


  eventControls = new QTabWidget;
  eventControls->addTab(
    new ActivePlaylistView(dataStore, this), tr("Playlist"));
  eventControls->addTab(
    new AvailableMusicView(dataStore, this), tr("Available Music"));
  eventControls->addTab(new EventGoersView(dataStore, this), tr("Users"));
 
  layout->addLayout(header);
  layout->addWidget(eventControls);
  mainContent->setLayout(layout);
  setMainWidget(mainContent);
  connect(dataStore, SIGNAL(eventEnded()), this, SLOT(handleEventEnded()));
  connect(
    dataStore, 
    SIGNAL(eventEndingFailed(const QString)), 
    this, 
    SLOT(handleEventEndingFailed(const QString)));
  showMainWidget();
}

void EventDashboard::updateEventInfo(){
  eventName->setText(tr("Event Name: ") + dataStore->getEventName());
  eventId->setText(tr("Event Id: ") + 
    QString::number(dataStore->getEventId()));
}

void EventDashboard::endEvent(){
  showLoadingText();
  dataStore->endEvent();
}

void EventDashboard::handleEventEnded(){
  showMainWidget(); 
  emit eventEnded();
}

void EventDashboard::handleEventEndingFailed(const QString errMessage){
  showMainWidget(); 
  QMessageBox::critical(
    this,
    tr("Ending Event Failed"),
    errMessage);
}


} //end namespace UDJ
