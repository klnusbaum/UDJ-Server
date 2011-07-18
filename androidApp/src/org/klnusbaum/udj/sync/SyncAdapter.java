package org.klnusbaum.udj.sync;

import android.content.AbstractThreadedSyncAdapter;
import android.content.SyncResult;
import android.content.Context;
import android.os.Bundle;
import android.content.ContentProviderClient;
import android.accounts.Account;


public class SyncAdapter extends AbstractThreadedSyncAdapter{
  private final Context context;

  public SyncAdapter(Context context, boolean autoInitialize){
    super(context, autoInitialize);
    this.context=context;
  }

  public void onPerformSync(Account account, Bundle extras, String authority,
    ContentProviderClient provider, SyncResult syncResult)
  {

  }
}
