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
#ifndef LOGIN_WIDGET_HPP
#define LOGIN_WIDGET_HPP

#include "WidgetWithLoader.hpp"
#include "ConfigDefs.hpp"

class QLabel;
class QLineEdit;
class QCheckBox;

namespace UDJ{

class UDJServerConnection;

/** \brief Widget used to login to the UDJ server */
class LoginWidget : public WidgetWithLoader{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs a Login Widget
   */
  LoginWidget(QWidget *parent=0);

  //@}


public slots:
  
  /** @name Public slots */
  //@{

  /** \brief Perform actions necessary for loggin in */
  void doLogin();
  
  //@}


signals:

  void startedMainGUI();
  void loginFailed();


private:
  
  /** @name Private Memeber */
  //@{

  /** \brief Label used for displayling the UDJ logo. */
  QLabel *logo;

  /** \brief Lineedit used for entering the user name */
  QLineEdit *usernameBox;

  /** \brief lineedit used for entering the password. */
  QLineEdit *passwordBox;

  QCheckBox *saveCreds;


  /** \brief Actual display for the login widget. */
  QWidget *loginDisplay;

  /** \brief Connection to the server. */
  UDJServerConnection *serverConnection;

  QLabel *usernameLabel;
 
  QLabel *passwordLabel;


  //@}

  /** @name Private Functions */
  //@{

  /** \brief Initializes UI. */
  void setupUi();

  //@}

private slots:
  /** @name Private Slots */
  //@{

  /** 
   * \brief Once the user has succesfully authenitcated, this starts up the
   * main gui for udj.
   */
  void startMainGUI(const QByteArray& ticketHash, const user_id_t& userId);

  /**
   * \brief Displays a message informing the user that the attempt to login to
   * the UDJ server failed.
   *
   * @param errorMessage The error message describing the failure.
   */
  void displayLoginFailedMessage(const QString errorMessage);

  void saveCredsChanged(bool newSetting);

  //@}
};


} //end namespace UDJ


#endif //LOGIN_WIDGET_HPP


