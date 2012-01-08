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
#include "AddressWidget.hpp"
#include <QLineEdit>
#include <QComboBox>
#include <QGridLayout>
#include <QLabel>

namespace UDJ{

AddressWidget::AddressWidget(QWidget *parent):QWidget(parent){
  QLabel *streetAddressLabel = new QLabel(tr("Address:"));
  streetAddress = new QLineEdit();
  streetAddressLabel->setBuddy(streetAddress);
  
  QLabel *cityLabel = new QLabel(tr("City:"));
  city = new QLineEdit();
  cityLabel->setBuddy(city);

  QLabel *stateLabel = new QLabel(tr("State:"));
  setupStateCombo();
  stateLabel->setBuddy(state);

  QLabel *zipcodeLabel = new QLabel(tr("Zipcode:"));
  zipcode = new QLineEdit();
  zipcodeLabel->setBuddy(zipcode);
  
  QGridLayout *layout = new QGridLayout(this);
  layout->addWidget(streetAddressLabel, 0,0);
  layout->addWidget(streetAddress, 0,1);
  layout->addWidget(cityLabel, 1,0);
  layout->addWidget(city, 1,1);
  layout->addWidget(stateLabel, 2,0);
  layout->addWidget(state, 2,1);
  layout->addWidget(zipcodeLabel, 3,0);
  layout->addWidget(zipcode, 3,1);
  setLayout(layout);

}

QString AddressWidget::getBadInputs() const{
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

void AddressWidget::setupStateCombo(){
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



}//end namespace
