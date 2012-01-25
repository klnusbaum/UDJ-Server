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
#ifndef LOGIN_DIALOG_HPP
#define LOGIN_DIALOG_HPP

#include <QDialog>

class QPushButton;
class QCheckBox;

namespace UDJ{

class LoginWidget;


/** \brief Widget used to login to the UDJ server */
class LoginDialog : public QDialog{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs a Login Widget
   */
  LoginDialog(QWidget *parent=0, Qt::WindowFlags f=0);

  //@}

public slots:
  virtual void accept();
  virtual void reject();

private:
  
  /** @name Private Memeber */
  //@{
  LoginWidget *loginWidget;

  /** \brief button used for initiating the login procedure. */
  QPushButton *loginButton;


  //@}

  /** @name Private Functions */
  //@{

  /** \brief Initializes UI. */
  void setupUi();


  //@}

private slots:
  /** @name Private Slots */
  //@{

  void closeDialog();

  //@}
};


} //end namespace UDJ


#endif //LOGIN_DIALOG_HPP



