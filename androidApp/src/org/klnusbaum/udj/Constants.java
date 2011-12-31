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
  public static final String ACCOUNT_TYPE = "org.klnusbaum.udj";
  public static final String AUTHORITY = "org.klnusbaum.udj";
  public static final String USER_ID_DATA = "org.klnusbaum.udj.userid";
  public static final String EVENT_ID_DATA = "org.klnusbaum.udj.EventId";
  public static final String ACCOUNT_EXTRA = "org.klnusbaum.udj.account";
  public static final String EVENT_ID_EXTRA = "org.klnusbaum.udj.EventId";
  public static final long NO_EVENT_ID = -1;
  public static final String ADD_REQUESTS_SYNCED = 
    "org.klnusbaum.udj.addRequestsSynced";
  public static final String LEFT_EVENT_ACTION = "org.klnusbaum.udj.LeftEvent";
  public static final String JOINED_EVENT_ACTION = 
    "org.klnusbaum.udj.JoinedEvent";
  public static final String EVENT_JOIN_FAILED_ACTION = 
    "org.klnusbaum.udj.EventJoinFailed";

  public static final Uri EVENT_URI = new Uri.Builder().
    authority(Constants.AUTHORITY).appendPath("event").build();
}
