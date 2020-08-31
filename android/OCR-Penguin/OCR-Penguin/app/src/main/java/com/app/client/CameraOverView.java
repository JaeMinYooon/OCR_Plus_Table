package com.app.client;

import android.annotation.SuppressLint;
import android.app.AppComponentFactory;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.Image;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class CameraOverView extends AppCompatActivity {
    private static final int GALLERY_CODE = 0;
    private static final String TAG = "FirstPenguin";
    private boolean taskflag = false;
    ImageButton remakeBtn;
    ImageButton okBtn;
    ImageView overview;
    Intent intent;
    Bitmap bitmap = null;
    File root = Environment.getExternalStorageDirectory();
    String imagePath = root.getAbsolutePath() + "/cameratest.jpg";

    private TCPClient tcpClient = new TCPClient(imagePath, "223.194.131.27", 5801, taskflag, CameraOverView.this);
    private CheckTypesTask task;

    @SuppressLint("WrongThread")
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_overview);

        remakeBtn = (ImageButton) findViewById(R.id.remake);
        okBtn = (ImageButton)findViewById(R.id.ok);

        //찬혁
        /*Uri imageUri = (Uri)intent.getParcelableExtra("imageUri"); // 여기 에러남 확인 바람.
        Uri uri = Uri.parse("file://" + imageUri);

        try {
//                            uri 주소를 Bitmap으로 변환한다.
            bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(), uri);
            overview.setImageBitmap(bitmap);
            //overview.setImageURI(intent.getData());
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }*/

        overview = (ImageView)findViewById(R.id.overview);
        overview.setDrawingCacheEnabled(true);
        //File file = new File("/DCIM/Camera/image.jpg");
        File cachePath = new File(imagePath);

        //Bitmap bitmap = overview.getDrawingCache();
        Bitmap myBitmap = BitmapFactory.decodeFile(cachePath.getAbsolutePath());

        Log.d("",root.getAbsolutePath());
        try
        {
            cachePath.createNewFile();
            FileOutputStream ostream = new FileOutputStream(cachePath);
            //bitmap.compress(Bitmap.CompressFormat.JPEG, 100, ostream);
            overview.setImageBitmap(myBitmap); // 만드는게아니라 저건 가져오눈거 사진은 지금찍으면 갤러리에 있음? 있지
            overview.setRotation(90); // 90도
            ostream.close();
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }


        remakeBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(getApplicationContext(), TestActivity.class); //Test중
                startActivity(intent);
            }
        });

        okBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Thread thread = new Thread(tcpClient);
                //task = new CheckTypesTask(CameraOverView.this, taskflag);
                thread.start();
                //task.execute();

            }
        });

    }

    void pickUpPicture() { //갤러리에서 사진 선택
        Intent intent = new Intent(Intent.ACTION_PICK);
        intent.setType(MediaStore.Images.Media.CONTENT_TYPE);
        intent.setData(MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(intent, GALLERY_CODE);

    }
/*// 타임타임 지금 뭐하려는지 알겠는데 이 위함수 부르면 그냥 갤러리로 가버려 그건 알고있지??? ㅇㅇㄱㄷ
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == GALLERY_CODE && resultCode == RESULT_OK) {
            Log.e(TAG, imagePath);
            try {
                if(imagePath == null || imagePath == ""){
                    Toast.makeText(getApplicationContext(), "선택된 이미지가 없습니다.",Toast.LENGTH_SHORT).show();
                }else {
                    Thread thread = new Thread(tcpClient);
                    task = new CheckTypesTask(CameraOverView.this, taskflag);
                    thread.start();
                    task.execute();
                    Log.d("Send", "Success");
                }
            }catch (Exception e){
                e.printStackTrace();
            }
        }else{
            Toast.makeText(getApplicationContext(), "에러 ㅋㅋ", Toast.LENGTH_SHORT).show();
        }
    }

    public void ThreadToast(final String message){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(getApplicationContext(), message, Toast.LENGTH_SHORT)
                        .show();

            }

        });
    }*/
}
