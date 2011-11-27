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
#include "CreateEventWidget.hpp"
#include "DataStore.hpp"
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QVBoxLayout>
#include <QProgressDialog>
#include <QMessageBox>


namespace UDJ{


CreateEventWidget::CreateEventWidget(
  DataStore *dataStore, 
  QWidget *parent):
  QWidget(parent),
  dataStore(dataStore)
{
  setupUi();
  connect(
    createEventButton,
    SIGNAL(clicked(bool)),
    this,
    SLOT(doLogin()));
  connect(
    dataStore,
    SIGNAL(eventCreated()),
    this,
    SLOT(eventCreateSuccess()));
  connect(
    dataStore,
    SIGNAL(eventCreationFailed()),
    this,
    SLOT(eventCreateFail()));
}


void CreateEventWidget::setupUi(){
  nameEdit = new QLineEdit(tr("Name of event"));
  passwordEdit = new QLineEdit(tr("Password (optional)"));
  locationEdit = new QLineEdit(tr("Location (optional)"));
  createEventButton = new QPushButton(tr("Create Event"));
  createEventButton->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
  createLabel = new QLabel(tr("Create a New Event"));

  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addWidget(createLabel, Qt::AlignCenter);
  mainLayout->addWidget(nameEdit);
  mainLayout->addWidget(passwordEdit);
  mainLayout->addWidget(locationEdit);
  mainLayout->addWidget(createEventButton);

  setLayout(mainLayout);
}

void CreateEventWidget::doLogin(){
  createProgress = new QProgressDialog(
    tr("Creating event..."),
    tr("Cancel"),
    0,
    1,
    this);
  dataStore->createNewEvent(
    nameEdit->text(),
    passwordEdit->text(),
    locationEdit->text());
}

void CreateEventWidget::eventCreateSuccess(){
  createProgress->setValue(1);
  emit eventCreated();
}

void CreateEventWidget::eventCreateFail(){
  createProgress->setValue(1);
  QMessageBox::critical(
    this,
    tr("Event Creation Failed"),
    tr("Failed to create event"));
}


}//end namespace UDJ
