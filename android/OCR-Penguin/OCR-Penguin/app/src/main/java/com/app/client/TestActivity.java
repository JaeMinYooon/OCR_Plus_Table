package com.app.client;
import java.io.*;
import java.util.*;

import android.annotation.SuppressLint;
import android.app.*;
import android.content.*;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.graphics.drawable.BitmapDrawable;
import android.hardware.*;
import android.hardware.Camera.*;
import android.net.*;
import android.os.*;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.util.*;
import android.view.*;
import android.widget.*;

public class TestActivity extends AppCompatActivity {
    MyCameraSurface mSurface;
    ImageButton mShutter;

    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test); // 이거있는데?

        mSurface = (MyCameraSurface)findViewById(R.id.surfaceView);

        mSurface.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View view, MotionEvent motionEvent) {
                // 오토 포커스 시작
                mShutter.setEnabled(false);
                mSurface.mCamera.autoFocus(mAutoFocus);

                return true;
            }
        });


        // 사진 촬영
        mShutter = (ImageButton)findViewById(R.id.capture);
        mShutter.setOnClickListener(new Button.OnClickListener() {
            public void onClick(View v) {
                mSurface.mCamera.takePicture(null, null, mPicture);
            }
        });
    }
    // 포커싱 성공하면 촬영 허가
    AutoFocusCallback mAutoFocus = new AutoFocusCallback() {
        public void onAutoFocus(boolean success, Camera camera) {
            mShutter.setEnabled(success);
        }
    };
    // 사진 저장.
    PictureCallback mPicture = new PictureCallback() {
        @SuppressLint("WrongConstant")
        public void onPictureTaken(byte[] data, Camera camera) { //이게 사진 만들어주누ㅡㄴ거? 사진찍는거지
            String sd = Environment.getExternalStorageDirectory().getAbsolutePath();
            String path = sd + "/cameratest.jpg";
            File file = new File(path);
            final int CAMERA_REQUEST_CODE = 1;

            try {
                FileOutputStream fos = new FileOutputStream(file);
                fos.write(data);
                fos.flush();
                fos.close();
            } catch (Exception e) {
                Toast.makeText(TestActivity.this, "파일 저장 중 에러 발생 : " +
                        e.getMessage(), 0).show();
                return;
            }


           Intent intent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
            Uri uri = Uri.parse("file://" + path);
            intent.setData(uri);
            sendBroadcast(intent);

            Toast.makeText(TestActivity.this, "사진 저장 완료 : " + path, 0).show();


            Intent imageIntent = new Intent(getApplicationContext(), CameraOverView.class);
            //Bitmap sendBitmap = BitmapFactory.decodeByteArray(data, 0, data.length);
//            Bitmap sendBitmap = BitmapFactory.decodeResource(getResources(),file);
//            ByteArrayOutputStream stream = new ByteArrayOutputStream();
//            sendBitmap.compress(Bitmap.CompressFormat.JPEG, 100, stream);
//            byte[] byteArray = stream.toByteArray();
            intent.putExtra("imageUri",uri);
            startActivity(imageIntent);



        }
    };
}
