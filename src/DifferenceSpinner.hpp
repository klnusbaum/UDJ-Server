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
#ifndef DIFFERENCE_SPINNER_HPP
#define DIFFERENCE_SPINNER_HPP

#include "ConfigDefs.hpp"
#include <QSpinBox>

namespace UDJ{

/**
 * \brief A DifferenceSpinner is a special impelmentation of a QSpinBox
 * that remembers a specific past value and can then calculate
 * the difference of the current value from that last saved value.
 */
class DifferenceSpinner : public QSpinBox{
Q_OBJECT
public:
	/** @name Constructors */
  //@{

	/** \brief Constructs a DifferenceSpinner 
	 *
	 * @param parent The parent widget of this DifferenceSpinner.
   */
  DifferenceSpinner(QWidget* parent=0):
		QSpinBox(parent),
		savedValue(-1){}

  //@}

  /** @name Getters and Setters */
  //@{

  /** \brief Saves the current value of the spinner.
   * This way the spinners current value can be compared to
   * a previous value.
   */
	inline void saveCurrentValue(){
		savedValue = value();
	}

  /** \brief Retrieves the last saved value.
   *
   * @return The last saved value.
   */
	inline int getSavedValue(){
		return savedValue;
	}

  /**
   * \brief retrieves the difference between the saved value and the current
   * value.
   *
   * @return The difference between the saved value and the current value.
   */
	inline int getCurrentValueSavedValueDiff(){
		return value()-getSavedValue();
	}

  //@}

private:
  /** @name Private Members */
  //@{
  
  /** \brief Saved value used for future comparison. */
	int savedValue;

  //@}
};


} //end namespace
#endif //DIFFERENCE_SPINNER_HPP

