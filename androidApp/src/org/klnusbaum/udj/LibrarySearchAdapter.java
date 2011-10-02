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

import android.widget.ListAdapter;
import android.view.View;
import android.content.Context;
import android.widget.TextView;
import android.widget.ImageButton;
import android.database.DataSetObserver;

public class LibrarySearchAdapter implements ListAdapter{

  private List<LibraryEntry> entries;
  private Context context;
  private View.OnClickListener addClickListener;
  public static final int LIB_ENTRY_VIEW_TYPE = 0;
  public static final int LIB_ID_TAG = 0;

  public LibrarySearchAdapter(Context context){
    this.entries = null;
    this.addClickListener = null;
    this.context = context;
  }

  public LibrarySearchAdapter(
    Context context, 
    List<LibraryEntry> entries,
    View.OnClickListener addClickListener
  )
  {
    this.entries = entries;
    this.context = context;
    this.addClickListener = addClickListener;
  }

  public boolean areAllItemsEnabled(){
    return true;
  }

  public boolean isEnabled(int position){
    return true;
  }

  public int getCount(){
    if(entries != null){
      return entries.size();
    }
    return 0;
  }

  public Object getItem(int position){
    if(entries != null){
      return entries.get(position);
    }
    return null;
  }

  public LibraryEntry getLibraryEntry(int position){
    if(entries != null){
      return entries.get(position);
    }
    return null;
  }

  public long getItemId(int position){
    if(entries != null){
      return entries.get(position).getServerId();
    }
    return LibraryEntry.INVALID_SERVER_LIB_ID; 
  }

  public int getItemViewType(int position){
    return LIB_ENTRY_VIEW_TYPE;
  }

  public View getView(int position, View convertView, ViewGroup parent){
    //TODO should probably enforce view type
    LibraryEntry libEntry = getLibraryEntry(position);
    View toReturn = convertView;
    if(toReturn == null){
      toReturn = View.inflate(context, R.layout.library_list_item, parent);
    }

    TextView songView = (TextView)toReturn.findViewById(R.id.librarySongName);
    TextView artistView = 
      (TextView)toReturn.findViewById(R.id.libraryArtistName);
    ImageButton addButton = 
      (ImageButton)toReturn.findViewById(R.id.lib_add_button);
    songView.setText(libEntry.getSong());
    artistView.setText(libEntry.getArtist());
    addButton.setOnClickListener(addClickListener);
    addButton.setTag(LIB_ID_TAG, libEntry.getServerId());
  }

  public int getViewTypeCount(){
    return 1; 
  }

  public boolean hasStableIds(){
    return true;
  }

  public boolean isEmptry(){
    if(entries != null){
      return entries.isEmpty();
    }
    return true;
  }

  public void registerDataSetObserver(DataSetObserver observer){
    //Unimplemented because this data can't change
    //If new results need to be displayed a new adpater should be created.
  }

  public void unregisterDataSetObserver(DataSetObserver observer){
    //Unimplemented because data represented by this adpater shouldn't change.
    //If new results need to be displayed a new adpater should be created.
  }

}
