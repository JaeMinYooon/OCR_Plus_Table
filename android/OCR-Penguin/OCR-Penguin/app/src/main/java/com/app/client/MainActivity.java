package com.app.client;

import android.Manifest;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.database.Cursor;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.annotation.RequiresApi;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "FirstPenguin";
    private static final int CAMERA_CODE = 10;
    private static final int GALLERY_CODE = 0;
    private TCPClient tcpClient;
    private String mCurrentPhotoPath;
    private String imagePath = "";
    private ProgressDialog progressDialog;
    private CheckTypesTask task;
    private boolean taskflag = false;
    private CameraSurfaceView surfaceView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        requirePermission();
        ImageView gallery = (ImageView) findViewById(R.id.gallery);
        gallery.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

            }
        });

        ImageView camera = (ImageView) findViewById(R.id.camera);
        camera.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(getApplicationContext(), CameraActivity.class);
                startActivity(intent);
            }
        });
        ImageView question = (ImageView) findViewById(R.id.question);
        question.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(MainActivity.this, QuestionActivity.class);
                startActivity(intent);
            }
        });
        ImageView folder = (ImageView)findViewById(R.id.folder);
        folder.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                openApp();
            }
        });
    }

    @RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN)
    void requirePermission() { //권한 허가 요청
        String[] permissions = new String[]{Manifest.permission.CAMERA,
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.INTERNET,
                Manifest.permission.READ_EXTERNAL_STORAGE};
        ArrayList<String> listPermissionsNeeded = new ArrayList<>();
        for (String permission : permissions) {
            if (ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_DENIED) {
                //권한이 허가가 안됬을 경우 요청할 권한을 모집하는 부분
                listPermissionsNeeded.add(permission);
            }
        }
        if (!listPermissionsNeeded.isEmpty()) {
            //권한 요청 하는 부분
            ActivityCompat.requestPermissions(this, listPermissionsNeeded.toArray(new String[0]), 1);
        }
    }

    void pickUpPicture() { //갤러리에서 사진 선택
        Intent intent = new Intent(Intent.ACTION_PICK);
        intent.setType(MediaStore.Images.Media.CONTENT_TYPE);
        intent.setData(MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(intent, GALLERY_CODE);

    }

    void takePicture() { // 사진 찍기
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        try {
            File phtoFile = createImageFile();
            Uri photoUri = FileProvider.getUriForFile(this, "com.app.client.fileprovider", phtoFile);
            intent.putExtra(MediaStore.EXTRA_OUTPUT, photoUri);
            startActivityForResult(intent, CAMERA_CODE);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private File createImageFile() throws IOException { // 찍은 사진을 파일 만들어주기
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "document" + timeStamp + "_";
        //File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        File storageDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM);
        File image = File.createTempFile(
                imageFileName,  /* prefix */
                ".jpg",         /* suffix */
                storageDir      /* directory */
        );
        // Save a file: path for use with ACTION_VIEW intents
        mCurrentPhotoPath = image.getAbsolutePath();
        return image;
    }

    private void galleryAddPic() { //갤러리에 사진 저장
        Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        File f = new File(mCurrentPhotoPath);
        Uri contentUri = Uri.fromFile(f);
        mediaScanIntent.setData(contentUri);
        this.sendBroadcast(mediaScanIntent);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == CAMERA_CODE) {
            galleryAddPic();
        }
        if (requestCode == GALLERY_CODE && resultCode == RESULT_OK) {
            imagePath = getRealPathFromURI(data.getData());
            Log.e(TAG, imagePath);
            try {
                if(imagePath == null || imagePath == ""){
                    Toast.makeText(getApplicationContext(), "선택된 이미지가 없습니다.",Toast.LENGTH_SHORT).show();
                }else {
                    tcpClient = new TCPClient(imagePath, "223.194.131.27", 5801);
                    Thread thread = new Thread(tcpClient);
                    task = new CheckTypesTask();
                    thread.start();
                    task.execute();
                    Log.d("Send", "Success");
                }
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }

    private String getRealPathFromURI(Uri contentUri){ //uri의 진짜 주소 찾기
        String [] proj = {MediaStore.Images.Media.DATA};
        Cursor cursor = getContentResolver().query(contentUri, proj, null, null, null);
        cursor.moveToFirst();
        int column_index = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);

        return cursor.getString(column_index);
    }

    class TCPClient implements Runnable { // 소켓 통신
        private String filePath;
        private String serverIP;
        private int serverPort;
        private String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        private String fileName = timeStamp+"result.xlsx";
        private String FileSize;

        public TCPClient(String filePath, String ip, int port) {
            super();
            this.serverIP = ip;
            this.serverPort = port;
            this.filePath = filePath;
        }

        public void ThreadToast(final String message){
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(getApplicationContext(), message, Toast.LENGTH_SHORT)
                            .show();

                }

            });
        }

        @Override
        public void run() {
            try {
                taskflag = false;
                Log.d("Wait", "대기중");
                Socket sock = new Socket(this.serverIP, this.serverPort);
                DataInputStream dis = new DataInputStream(new FileInputStream(new File(this.filePath)));
                Log.d(this.filePath, "파일 경로");
                DataOutputStream dos = new DataOutputStream(sock.getOutputStream());
                byte[] buf = new byte[1024];

                //while (true) {
                Log.d("connecting", "발신중...");
                try {
                    //loading();
                    while (dis.read(buf) > 0) {
                        dos.write(buf);
                        dos.flush();
                    }
                    Log.d("finish", "발신 완료!!!!.");
                    sock.shutdownOutput();
                } catch (Exception e) {
                    taskflag = true;
                    ThreadToast("문서 사진이 아닙니다");
                    Log.d("Error", "서버 에러!!");
                    e.printStackTrace();
                }
                try {
                    File root = android.os.Environment.getExternalStorageDirectory();
                    File dir = new File(root.getAbsolutePath() + "/pth/excel/");
                    if (dir.exists() == false) {
                        dir.mkdirs();
                    }
                    Log.d(TAG, fileName);
                    byte[] tmpByte = new byte[1024];
                    dis = new DataInputStream(sock.getInputStream()); //InputStream 확장
                    File file = new File(dir, fileName);
                    FileOutputStream fos = new FileOutputStream(file);
                    int Read;
                    for (; ; ) {
                        Read = dis.read(tmpByte);
                        if (Read <= 0) {
                            break;
                        }
                        fos.write(tmpByte, 0, Read);
                    }
                    taskflag = true;
                    dis.close();
                    fos.close();
                    sock.close();
                    long lFileSize = file.length();
                    FileSize = Long.toString(lFileSize);
                    int numFS = Integer.parseInt(FileSize);
                    Log.d(TAG,FileSize);
                    if(numFS > 10) {
                        ThreadToast("엑셀로 변환 완료!");
                    }else{
                        file.delete();
                        ThreadToast("문서 사진으로 인식 되지 않습니다");
                    }
                } catch (Exception e) {
                    taskflag = true;
                    ThreadToast("문서 사진이 아닙니다");
                    Log.d("Error", "서버서버서버 에러!!");
                    e.printStackTrace();
                }
            } catch (Exception e) {
                taskflag = true;
                ThreadToast("문서 사진이 아닙니다");
                e.printStackTrace();
            }
        }
    }

    public void openApp () {
        boolean isExist = false;
        Context mContext = getApplicationContext();
        PackageManager packageManager = mContext.getPackageManager();
        List<ResolveInfo> mApps;
        Intent mIntent = new Intent(Intent.ACTION_MAIN, null);
        mIntent.addCategory(Intent.CATEGORY_LAUNCHER);
        mApps = packageManager.queryIntentActivities(mIntent, 0);

        try {
            for (int i = 0; i < mApps.size(); i++) {
                if(mApps.get(i).activityInfo.packageName.startsWith("com.microsoft.office.excel")){
                    isExist = true;
                    break;
                }
            }
        } catch (Exception e) {
            isExist = false;
        }

        // 설치되어 있으면
        if(isExist){
            Intent intent = mContext.getPackageManager().getLaunchIntentForPackage("com.microsoft.office.excel");
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            mContext.startActivity(intent);
        }else{
            Intent marketLaunch = new Intent(Intent.ACTION_VIEW);
            marketLaunch.setData(Uri.parse("https://play.google.com/store/apps/details?id=com.microsoft.office.excel"));
            startActivity(marketLaunch);
        }

    }

    private class CheckTypesTask extends AsyncTask<Void, Void, Void> {

        ProgressDialog asyncDialog = new ProgressDialog(
                MainActivity.this);

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
}





