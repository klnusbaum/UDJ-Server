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

import android.support.v4.content.AsyncTaskLoader;

import android.content.Context;
import android.util.Log;

import java.util.List;
import java.io.IOException;

import org.json.JSONException;

import org.apache.http.auth.AuthenticationException;
import org.apache.http.ParseException;

import org.klnusbaum.udj.network.ServerConnection;
import org.klnusbaum.udj.containers.LibraryEntry;

public class LibrarySearchLoader 
  extends AsyncTaskLoader<List<LibraryEntry>>
{
  private String query;

  public LibrarySearchLoader(Context context, String query){
    super(context);
    this.query = query;
  }

  public List<LibraryEntry> loadInBackground(){
    Log.i("TAG", "IN LOAD IN BACKGROUND!");
    if(query != null){
      try{
        return ServerConnection.libraryQuery(query);
        //TODO do something to the potential errors
      }
      catch(JSONException e){

      }
      catch(ParseException e){

      }
      catch(IOException e){

      }
      catch(AuthenticationException e){

      }
      return null;
    }
    return null;
  }

  @Override
  protected void onStartLoading(){
    forceLoad();
  }
}
