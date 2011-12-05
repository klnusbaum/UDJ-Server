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
#include "DataStore.hpp"
#include "CreateEventWidget.hpp"
#include "EventDashboard.hpp"
#include <QVBoxLayout>
#include <QStackedWidget>


namespace UDJ{

EventWidget::EventWidget(DataStore *dataStore, QWidget *parent)
  :QWidget(parent), dataStore(dataStore)
{
  setupUi();  
}

void EventWidget::setupUi(){
  creatorWidget = new CreateEventWidget(dataStore);
  creatorWidget->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
  eventDashboard = new EventDashboard(dataStore, this);
  mainContent = new QStackedWidget(this);
  mainContent->addWidget(creatorWidget);
  mainContent->addWidget(eventDashboard);
  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addWidget(mainContent);
  setLayout(mainLayout);

  connect(
    creatorWidget,
    SIGNAL(eventCreated()),
    this,
    SLOT(showEventDashboard()));
  connect(
    eventDashboard,
    SIGNAL(eventEnded()),
    this,
    SLOT(eventEnded()));
}

void EventWidget::showEventDashboard(){
  mainContent->setCurrentWidget(eventDashboard);
}


void EventWidget::eventEnded(){
  mainContent->setCurrentWidget(creatorWidget);
}



}//end UDJ namespace
