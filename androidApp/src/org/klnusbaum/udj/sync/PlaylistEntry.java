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
package org.klnusbaum.udj.sync;

import android.database.Cursor;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.List;

public class PlaylistEntry{

  public static PlaylistEntry valueOf(JSONObject jObj){
    //TODO implement
    return null;
  }

  public static PlaylistEntry valueOf(Cursor cur){
    //TODO implement
    return null;
  }

  public static JSONArray getJSONArray(List<PlaylistEntry> entries){
    //TODO impelment
    return null;
  } 

}
