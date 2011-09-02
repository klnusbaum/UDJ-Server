package org.klnusbaum.udj.containers;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

import java.util.ArrayList;
import java.util.List;

public class AcousticsInfo{
  private static final String PARTIES_PARAM = "players";
  public static List<Party> getParties(JSONObject info) throws JSONException{
    JSONArray parties = info.getJSONArray(PARTIES_PARAM);
    ArrayList<Party> toReturn = new ArrayList<Party>(parties.length());
    for(int i = 0; i < parties.length(); ++i){
      toReturn.add(new Party(parties.getString(i), Party.INVALID_PARTY_ID));
    }
    return toReturn;
  }

  public static List<PlaylistEntry> getPlaylistEntries(JSONObject info)
    throws JSONException
  {
    JSONArray 
  }
}
