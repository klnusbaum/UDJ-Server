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

import android.util.Log;

public class Event{
  public static final String ID_PARAM ="id";
  public static final String NAME_PARAM="name";
  public static final String HOST_NAME_PARAM="host_username";
  public static final String HOST_ID_PARAM="host_id";
  public static final String LATITUDE_PARAM="latitude";
  public static final String LONGITUDE_PARAM="longitude";

  private long eventId;
  private String name;
  private String hostName;
  private long hostId;
  private double latitude;
  private double longitude;


  public Event(
    long eventId, 
    String name, 
    String hostName,
    long hostId, 
    double latitude, 
    double longitude)
  {
    this.eventId = eventId;
    this.name = name;
    this.hostName = hostName;
    this.hostId = hostId;
    this.latitude = latitude;
    this.longitude = longitude;
  }

  public long getEventId(){
    return eventId;
  }

  public String getName(){
    return name;
  }

  public String getHostName(){
    return hostName;
  }

  public long getHostId(){
    return hostId;
  }

  public double getLatitude(){
    return latitude;
  }
  
  public double getLongitude(){
    return longitude;
  }

  public static Event valueOf(JSONObject jObj)
    throws JSONException 
  {
    return new Event(
      jObj.getLong(ID_PARAM),
      jObj.getString(NAME_PARAM),
      jObj.getString(HOST_NAME_PARAM),
      jObj.getLong(HOST_ID_PARAM),
      jObj.optDouble(LATITUDE_PARAM, -100.0),
      jObj.optDouble(LONGITUDE_PARAM, -100.0));
  }

  public static JSONObject getJSONObject(Event event)
    throws JSONException
  {
    JSONObject toReturn = new JSONObject();
    toReturn.put(ID_PARAM, event.getEventId());
    toReturn.put(NAME_PARAM, event.getName());
    toReturn.put(HOST_NAME_PARAM, event.getHostName());
    toReturn.put(HOST_ID_PARAM, event.getHostId());
    toReturn.put(LATITUDE_PARAM, event.getLatitude());
    toReturn.put(LONGITUDE_PARAM, event.getLongitude());
    return toReturn;
  }

  public static JSONArray getJSONArray(List<Event> events)
    throws JSONException
  {
    JSONArray toReturn = new JSONArray();
    for(Event event: events){
      toReturn.put(getJSONObject(event));
    }
    return toReturn;
  } 
  
  public static ArrayList<Event> fromJSONArray(JSONArray array)
    throws JSONException
  {
    ArrayList<Event> toReturn = new ArrayList<Event>();
    for(int i=0; i < array.length(); ++i){
      toReturn.add(Event.valueOf(array.getJSONObject(i)));
    }
    return toReturn;
  }

}
