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
#include <QLabel>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPushButton>

namespace UDJ{


EventDashboard::EventDashboard(DataStore *dataStore, QWidget *parent)
  :QWidget(parent),
  dataStore(dataStore)
{
  setupUi();
  connect(dataStore, SIGNAL(eventCreated()), this, SLOT(updateEventName()));
}


void EventDashboard::setupUi(){
  QVBoxLayout *layout = new QVBoxLayout;
  QHBoxLayout *header = new QHBoxLayout;

  eventName = new QLabel(tr("Event Name: ") + dataStore->getEventName());
  QPushButton *stopEventButton = new QPushButton(tr("Stop Event"));
  connect(stopEventButton, SIGNAL(clicked()), this, SIGNAL(endEvent()));
  header->addWidget(eventName);
  header->addStretch();
  header->addWidget(stopEventButton);
 
  layout->addLayout(header);
  setLayout(layout);
}

void EventDashboard::updateEventName(){
  eventName->setText(tr("Event Name: ") + dataStore->getEventName());
}

void EventDashboard::refreshDisplay(){

}


} //end namespace UDJ
