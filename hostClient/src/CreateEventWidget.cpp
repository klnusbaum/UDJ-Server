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
#include <QHBoxLayout>
#include <QProgressDialog>
#include <QMessageBox>
#include <QCheckBox>
#include <QFormLayout>
#include <QComboBox>


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
  passwordEdit = new QLineEdit();
  streetAddress = new QLineEdit();
  city = new QLineEdit();
  setupStateCombo();
  zipcode = new QLineEdit();
  useAddress = new QCheckBox(tr("Provide Address")); 
  createEventButton = new QPushButton(tr("Create Event"));

  QFormLayout *layout = new QFormLayout;
  layout->addRow(tr("Name of event"), nameEdit);
  layout->addRow(tr("Password (optional)"), passwordEdit);
  layout->addRow(useAddress);
  layout->addRow(tr("Address:"), streetAddress);
  layout->addRow(tr("City:"), city);
  layout->addRow(tr("State:"), state);
  layout->addRow(tr("Zipcode:"), zipcode);
  layout->addRow(createEventButton);
  
  connect(
    useAddress,
    SIGNAL(toggled(bool)),
    this,
    SLOT(enableAddressInputs(bool)));
  enableAddressInputs(false);
  

  eventForm->setLayout(layout);
  setMainWidget(eventForm);
  showMainWidget();
}

void CreateEventWidget::enableAddressInputs(bool enable){
  streetAddress->setEnabled(enable);
  city->setEnabled(enable);
  state->setEnabled(enable);
  zipcode->setEnabled(enable);
}

void CreateEventWidget::doCreation(){
  showLoadingText();
  if(nameEdit->text() == ""){
    eventCreateFail("You must provide a name for your event." );
    return;
  }
    
  if(useAddress->isChecked()){
    QString badInputs = getAddressBadInputs();
    if(badInputs == ""){
      dataStore->createNewEvent(
        nameEdit->text(),
        passwordEdit->text(),
        streetAddress->text(),
        city->text(),
        state->currentText(),
        zipcode->text());
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

QString CreateEventWidget::getAddressBadInputs() const{
  QString toReturn ="";
  int errorCounter = 1;
  if(streetAddress->text() == ""){
    toReturn += QString::number(errorCounter++) + 
      ". You did not enter a street address.\n";
  }
  if(!getZipcodeRegex().exactMatch(zipcode->text())){
    toReturn += QString::number(errorCounter++) + 
      ". Zipcode invalid.";
  }
  return toReturn;
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


void CreateEventWidget::setupStateCombo(){
  state = new QComboBox();
  state->addItem("AL");
  state->addItem("AK");
  state->addItem("AZ");
  state->addItem("AR");
  state->addItem("CA");
  state->addItem("CO");
  state->addItem("CT");
  state->addItem("DE");
  state->addItem("DC");
  state->addItem("FL");
  state->addItem("GA");
  state->addItem("HI");
  state->addItem("ID");
  state->addItem("IL");
  state->addItem("IN");
  state->addItem("IA");
  state->addItem("KS");
  state->addItem("KY");
  state->addItem("LA");
  state->addItem("ME");
  state->addItem("MT");
  state->addItem("NE");
  state->addItem("NV");
  state->addItem("NH");
  state->addItem("NJ");
  state->addItem("NM");
  state->addItem("NY");
  state->addItem("NC");
  state->addItem("ND");
  state->addItem("OH");
  state->addItem("OK");
  state->addItem("OR");
  state->addItem("MD");
  state->addItem("MA");
  state->addItem("MI");
  state->addItem("MN");
  state->addItem("MS");
  state->addItem("MO");
  state->addItem("PA");
  state->addItem("RI");
  state->addItem("SC");
  state->addItem("SD");
  state->addItem("TN");
  state->addItem("TX");
  state->addItem("UT");
  state->addItem("VT");
  state->addItem("VA");
  state->addItem("WA");
  state->addItem("WV");
  state->addItem("WI");
  state->addItem("WY");
}

}//end namespace UDJ
