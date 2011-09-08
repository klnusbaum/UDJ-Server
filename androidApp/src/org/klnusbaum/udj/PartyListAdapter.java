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
package org.klnusbaum.udj;

import android.widget.ArrayAdapter;
import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.widget.TextView;
import android.content.Context;

import org.klnusbaum.udj.containers.Party;

public class PartyListAdapter extends ArrayAdapter<Party>{

  public PartyListAdapter(Context context){
    super(context, R.id.party_list_item);
  }

  public View getView(int position, View convertView, ViewGroup parent){
    TextView toReturn = (TextView)convertView;
    if(toReturn == null){
      LayoutInflater inflater = LayoutInflater.from(getContext());
      toReturn = (TextView)inflater.inflate(R.layout.party_list_item, null);
    }
    toReturn.setText(getItem(position).getName());
    return toReturn;
  }

  public long getPartyId(int position){
    return getItem(position).getPartyId();
  }

  public long getPartyName(int position){
    return getItem(position).getPartyName();
  }
}
