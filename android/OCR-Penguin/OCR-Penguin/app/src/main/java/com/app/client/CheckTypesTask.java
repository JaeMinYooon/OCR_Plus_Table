package com.app.client;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.AsyncTask;

public class CheckTypesTask extends AsyncTask<Void, Void, Void> {
    private Context context;
    private boolean taskflag;

    CheckTypesTask(Context context, boolean taskflag){
        this.context = context;
        this.taskflag = taskflag;
    }

    ProgressDialog asyncDialog = new ProgressDialog(context);

    @Override
    protected void onPreExecute() {
        asyncDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        asyncDialog.setMessage("로딩중입니다..");

        // show dialog
        asyncDialog.show();
        super.onPreExecute();
    }

    @Override
    protected Void doInBackground(Void... arg0) {
        try {
            while(taskflag == false){
                Thread.sleep(100);
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return null;
    }

    @Override
    protected void onPostExecute(Void result) {
        asyncDialog.dismiss();
        super.onPostExecute(result);
    }
}
