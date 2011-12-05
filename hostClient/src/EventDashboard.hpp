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
#ifndef EVENT_DASHBOARD_HPP
#define EVENT_DASHBOARD_HPP
#include "WidgetWithLoader.hpp"

class QLabel;

namespace UDJ{

class DataStore;

class EventDashboard : public WidgetWithLoader{
Q_OBJECT
public:
  EventDashboard(DataStore *dataStore, QWidget *parent=0);
signals:
  void eventEnded();
private:
  void setupUi();
  DataStore *dataStore;
  QLabel *eventName;
  QWidget *mainContent;

private slots:
  void updateEventName();
  void endEvent();
  void handleEventEnded();
  void handleEventEndingFailed(const QString errMessage);
};


}//end namespace UDJ

#endif //EVENT_DASHBOARD_HPP
