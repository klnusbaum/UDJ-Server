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

import android.net.Uri;

public class Constants{
  /** Constants used for storing account info */
  public static final String ACCOUNT_TYPE = "org.klnusbaum.udj";
  public static final String AUTHORITY = "org.klnusbaum.udj";
  public static final String USER_ID_DATA = "org.klnusbaum.udj.userid";
  public static final String LAST_EVENT_ID_DATA = "org.klnusbaum.udj.EventId";
  public static final String EVENT_NAME_DATA = "org.klnusbaum.udj.EventName";
  public static final String EVENT_HOSTNAME_DATA = 
    "org.klnusbaum.udj.EventHostName";
  public static final String EVENT_LAT_DATA = "org.klnusbaum.udj.EventLat";
  public static final String EVENT_LONG_DATA = "org.klnusbaum.udj.EventLong";
  public static final String EVENT_JOIN_ERROR = "org.klnusbaum.udj.EventJoinError";


  public static final String EVENT_HOST_ID_DATA = "org.klnusbaum.udj.EventHostId";
  public static final long NO_EVENT_ID = -1;

  public static final String EVENT_STATE_DATA = "org.klusbaum.udj.EventState";
  public static final int EVENT_JOIN_FAILED = -1;
  public static final int NOT_IN_EVENT = 0;
  public static final int JOINING_EVENT = 1;
  public static final int IN_EVENT = 2;
  public static final int LEAVING_EVENT = 3;
  public static final int EVENT_ENDED = 4;


  /** Constants use for passing account related info in intents */
  public static final String ACCOUNT_EXTRA = "org.klnusbaum.udj.account";
  public static final String EVENT_ID_EXTRA = "org.klnusbaum.udj.EventId";
  public static final String VOTE_TYPE_EXTRA = "org.klnusbaum.udj.VoteType";
  public static final String PLAYLIST_ID_EXTRA = "org.klnusbaum.udj.PlaylistId";
  public static final String LIB_ID_EXTRA = "org.klnusbaum.udj.LibId";
  public static final String EVENT_NAME_EXTRA = "org.klnusbaum.udj.EventName";
  public static final String EVENT_HOSTNAME_EXTRA = 
    "org.klnusbaum.udj.EventHostName";
  public static final String EVENT_HOST_ID_EXTRA = "org.klnusbaum.udj.EventHostId";
  public static final String EVENT_LAT_EXTRA = "org.klnusbaum.udj.EventLat";
  public static final String EVENT_LONG_EXTRA = "org.klnusbaum.udj.EventLong";


  /** Constants for actions used throughout */
  public static final String ADD_REQUESTS_SYNCED = 
    "org.klnusbaum.udj.addRequestsSynced";
  public static final String LEFT_EVENT_ACTION = "org.klnusbaum.udj.LeftEvent";
  public static final String EVENT_ENDED_ACTION = 
    "org.klnusbaum.udj.EventEnded";
  public static final String JOINED_EVENT_ACTION = 
    "org.klnusbaum.udj.JoinedEvent";
  public static final String EVENT_JOIN_FAILED_ACTION = 
    "org.klnusbaum.udj.EventJoinFailed";
  public static final String SHOW_TOAST_ACTION = "org.klnusbaum.udj.ShowToast";

  /** URI constants */
  public static final Uri EVENT_URI = new Uri.Builder().
    authority(Constants.AUTHORITY).appendPath("event").build();

  /** Error constants */

}
