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
#include "AddressWidget.hpp"
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QGridLayout>
#include <QProgressDialog>
#include <QMessageBox>
#include <QCheckBox>


namespace UDJ{


CreateEventWidget::CreateEventWidget(
  DataStore *dataStore, 
  QWidget *parent):
  WidgetWithLoader(tr("Creating Event..."), parent),
  dataStore(dataStore)
{
  setupUi();
  connect(
    createEventButton,
    SIGNAL(clicked(bool)),
    this,
    SLOT(doCreation()));
  connect(
    dataStore,
    SIGNAL(eventCreated()),
    this,
    SLOT(eventCreateSuccess()));
  connect(
    dataStore,
    SIGNAL(eventCreationFailed(const QString&)),
    this,
    SLOT(eventCreateFail(const QString&)));
}


void CreateEventWidget::setupUi(){
  eventForm = new QWidget(this);
  nameEdit = new QLineEdit();
  QLabel *nameLabel = new QLabel(tr("Name of event"));
  nameLabel->setBuddy(nameEdit);
  passwordEdit = new QLineEdit();
  QLabel *passwordLabel = new QLabel(tr("Password (optional)"));
  passwordLabel->setBuddy(passwordEdit);
  
  useAddress = new QCheckBox(tr("Provide Address")); 
  addressWidget = new AddressWidget(this);
  addressWidget->setEnabled(false);
  connect(
    useAddress,
    SIGNAL(toggled(bool)),
    addressWidget,
    SLOT(setEnabled(bool)));
  createEventButton = new QPushButton(tr("Create Event"));
  createEventButton->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
  createLabel = new QLabel(tr("Create a New Event"));

  QGridLayout *mainLayout = new QGridLayout;
  mainLayout->addWidget(createLabel, 0,0, Qt::AlignCenter);
  mainLayout->addWidget(nameLabel, 1,0);
  mainLayout->addWidget(nameEdit, 1,1);
  mainLayout->addWidget(passwordLabel, 2,0);
  mainLayout->addWidget(passwordEdit, 2,1);
  mainLayout->addWidget(useAddress, 3, 0, 1,2);
  mainLayout->addWidget(addressWidget, 4, 0,1,2);
  mainLayout->addWidget(createEventButton, 5,0,1,2);

  eventForm->setLayout(mainLayout);
  setMainWidget(eventForm);
  showMainWidget();
}

void CreateEventWidget::doCreation(){
  showLoadingText();
  if(nameEdit->text() == ""){
    eventCreateFail("You must provide a name for your event." );
    return;
  }
    
  if(useAddress->isChecked()){
    QString badInputs = addressWidget->getBadInputs();
    if(badInputs == ""){
      dataStore->createNewEvent(
        nameEdit->text(),
        passwordEdit->text(),
        addressWidget->getAddress(),
        addressWidget->getCity(),
        addressWidget->getState(),
        addressWidget->getZipcode());
    }
    else{
      eventCreateFail("The address you supplied is invalid. Please correct " 
        "the following errors:\n\n" + badInputs);
    }
  }
  else{
    dataStore->createNewEvent(nameEdit->text(), passwordEdit->text());
  }
}

void CreateEventWidget::eventCreateSuccess(){
  showMainWidget();
  emit eventCreated();
}

void CreateEventWidget::eventCreateFail(const QString& errMessage){
  showMainWidget();
  QMessageBox::critical(
    this,
    tr("Event Creation Failed"),
    errMessage);
}


}//end namespace UDJ
