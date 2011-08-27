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
package org.klnusbaum.udj.containers;

import java.util.ArrayList;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

import java.util.List;
import java.util.ArrayList;

public class Party{
  public static final String PARTY_ID_EXTRA = "org.klnusbaum.udj.party";
  public static final String NAME_PARAM = "name";
  public static final String ID_PARAM = "id";
  public static final long INVALID_PARTY_ID = -1;
  private String name;
  private long partyId;

  public Party(String name, long partyId){
    this.name = name;
    this.partyId  = partyId;
  }

  public String getName(){
    return this.name;
  }

  public long getPartyId(){
    return this.partyId;
  }


  public static Party valueOf(JSONObject jObj)
    throws JSONException 
  {
    return new Party(
      jObj.getString(NAME_PARAM),
      jObj.getLong(ID_PARAM));
  }

  public static JSONObject getJSONObject(Party party)
    throws JSONException
  {
    JSONObject toReturn = new JSONObject();
    toReturn.put(NAME_PARAM, party.getName());
    toReturn.put(ID_PARAM, party.getPartyId());
    return toReturn;
  }


  public static JSONArray getJSONArray(List<Party> parties)
    throws JSONException
  {
    JSONArray toReturn = new JSONArray();
    for(Party party: parties){
      toReturn.put(getJSONObject(party));
    }
    return toReturn;
  } 
  
  public static ArrayList<Party> fromJSONArray(JSONArray array)
    throws JSONException
  {
    ArrayList<Party> toReturn = new ArrayList<Party>();
    for(int i=0; i < array.length(); ++i){
      toReturn.add(Party.valueOf(array.getJSONObject(i)));
    }
    return toReturn;
  }

}
