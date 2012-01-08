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
#ifndef ADRESS_WIDGET_HPP
#define ADRESS_WIDGET_HPP
#include <QWidget>
#include <QRegExp>

#include <QLineEdit>
#include <QComboBox>

namespace UDJ{


/**
 * \brief Used to dislay the active playlist.
 */
class AddressWidget : public QWidget{
Q_OBJECT
public:

  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an AddressWidget
   *
   * @param parent The parent widget.
   */
  AddressWidget(QWidget* parent=0);

  QString getBadInputs() const;

  inline QString getAddress() const{return streetAddress->text();}
  inline QString getCity() const{return city->text();}
  inline QString getState() const{return state->currentText();}
  inline QString getZipcode() const{return zipcode->text();}

  //@}

private:

  /** @name Private Functions */
  //@{
    void setupStateCombo();
    static const QRegExp& getZipcodeRegex(){
      static const QRegExp zipcodeRegex("^\\d{5}(-\\d{4})?$");
      return zipcodeRegex;
    }
  //@}

  QLineEdit *streetAddress;
  QLineEdit *city;
  QComboBox *state;
  QLineEdit *zipcode;

   /** @name Private Slots */
   //@{
private slots:

  
  //@}

};


} //end namespace
#endif //ADRESS_WIDGET_HPP

