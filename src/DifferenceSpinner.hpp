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


class DifferenceSpinner : public QSpinBox{
Q_OBJECT
public:
  DifferenceSpinner(QWidget* parent=0):
		QSpinBox(parent),
		savedValue(-1){}

	inline void saveCurrentValue(){
		savedValue = value();
	}

	inline int getSavedValue(){
		return savedValue;
	}

	inline int getCurrentValueSavedValueDiff(){
		return value()-getSavedValue();
	}

private:
	int savedValue;
};


} //end namespace
#endif //DIFFERENCE_SPINNER_HPP

