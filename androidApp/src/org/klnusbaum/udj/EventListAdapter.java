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
import android.view.ViewGroup;
import android.content.Context;
import android.widget.TextView;
import android.widget.ImageButton;
import android.database.DataSetObserver;
import android.view.LayoutInflater;

import java.util.List;

import org.klnusbaum.udj.containers.Event;

public class EventListAdapter implements ListAdapter{

  private List<Event> events;
  private Context context;
  private View.OnClickListener addClickListener;
  public static final int EVENT_ENTRY_VIEW_TYPE = 0;

  public EventListAdapter(Context context){
    this.events = null;
    this.addClickListener = null;
    this.context = context;
  }

  public EventListAdapter(
    Context context, 
    List<Event> events,
    View.OnClickListener addClickListener
  )
  {
    this.events = events;
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
    if(events != null){
      return events.size();
    }
    return 0;
  }

  public Object getItem(int position){
    if(events != null){
      return events.get(position);
    }
    return null;
  }

  public Event getEvent(int position){
    if(events != null){
      return events.get(position);
    }
    return null;
  }

  public long getItemId(int position){
    if(events != null){
      return events.get(position).getEventId();
    }
    return 0; 
  }

  public int getItemViewType(int position){
    return EVENT_ENTRY_VIEW_TYPE;
  }

  public View getView(int position, View convertView, ViewGroup parent){
    //TODO should probably enforce view type
    Event event = getEvent(position);
    View toReturn = convertView;
    if(toReturn == null){
      //toReturn = View.inflate(context, R.layout.library_list_item, null);
      LayoutInflater inflater = (LayoutInflater)context.getSystemService(
        Context.LAYOUT_INFLATER_SERVICE);
      toReturn = inflater.inflate(R.layout.event_list_item, null);
    }

    TextView eventName = (TextView)toReturn.findViewById(R.id.event_item_name);
    TextView hostName = 
      (TextView)toReturn.findViewById(R.id.event_host_name);
    eventName.setText(event.getName());
    hostName.setText(event.getHostName());
    return toReturn;
  }

  public int getViewTypeCount(){
    return 1; 
  }

  public boolean hasStableIds(){
    return true;
  }

  public boolean isEmpty(){
    if(events != null){
      return events.isEmpty();
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
