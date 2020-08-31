package com.app.client;

import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.ResolveInfo;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.hardware.Camera;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

public class CameraActivity extends AppCompatActivity {
    private ImageView imageView;
    private File file;
    private CameraSurfaceView surfaceView;
    private CameraSurfaceView cameraView;
    int usingCamera = Camera.CameraInfo.CAMERA_FACING_BACK;
    String img_name;
    private Uri photoUri;
    boolean crop;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_camera);
        //supportRequestWindowFeature(Window.FEATURE_NO_TITLE);
        //getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
        //        WindowManager.LayoutParams.FLAG_FULLSCREEN);
        //capture();
    }

    private void capture() {
        surfaceView.capture(new Camera.PictureCallback() {
            @Override
            public void onPictureTaken(byte[] data, Camera camera) {
                BitmapFactory.Options options = new BitmapFactory.Options();
                options.inSampleSize = 8;
                Bitmap bitmap = BitmapFactory.decodeByteArray(data, 0, data.length);
                imageView.setImageBitmap(bitmap);
                // 사진을 찍게 되면 미리보기가 중지된다. 다시 미리보기를 시작하려면...
                camera.startPreview();
            }
        });
    }

    private void takePhoto() {
        cameraView.capture(new Camera.PictureCallback() {   //캡쳐 이벤트의 콜백함수
            public void onPictureTaken(byte[] data, Camera camera) {//사진 데이터와 카메라 객체
                try {
                    Bitmap bitmaporigin = BitmapFactory.decodeByteArray(data, 0, data.length);//원본 비트맵 파일. 왠지 90도 돌아가 있다

                    //왠지 90도 돌아가서 찍힘. 되돌려놓기. 전면 카메라의 경우 좌우반전(진짜 왤까)
                    Matrix matrix = new Matrix();
                    if (usingCamera == Camera.CameraInfo.CAMERA_FACING_FRONT) {
                        float[] mirrorY = {
                                -1, 0, 0,
                                0, 1, 0,
                                0, 0, 1
                        };
                        matrix.setValues(mirrorY);
                    }
                    matrix.postRotate(90);

                    Bitmap bitmap = Bitmap.createBitmap(bitmaporigin, 0, 0,
                            bitmaporigin.getWidth(), bitmaporigin.getHeight(), matrix, true);

                    //사진 원본 파일. 갤러리에서 보이며 /내장메모리/Pictures 에 저장.
                    img_name = new SimpleDateFormat("yyyyMMddhhmmss").format(new Date());   //이미지의 이름을 설정
                    String outUriStr = MediaStore.Images.Media.insertImage(getContentResolver(),//이미지 파일 생성
                            bitmap, img_name, "Captured Image using Camera.");

                    if (outUriStr == null) {
                        Log.d("SampleCapture", "Image insert failed.");
                        return;
                    } else {
                        photoUri = Uri.parse(outUriStr);//찍은 사진 경로를 photoUri에 저장
                        sendBroadcast(new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, photoUri));
                    }
                    Toast.makeText(getApplicationContext(), "찍은 사진을 앨범에 저장했습니다.", Toast.LENGTH_LONG).show();

                    //cropImage();//이미지 크롭
                    MediaScannerConnection.scanFile(getApplicationContext(),//앨범에 사진을 보여주기 위해 스캔
                            new String[]{photoUri.getPath()}, null,
                            new MediaScannerConnection.OnScanCompletedListener() {
                                public void onScanCompleted(String path, Uri uri) {
                                }
                            });

                    //프레임 뷰에 보여지는 화면 바꾸기
                    imageView.setVisibility(View.VISIBLE);
                    cameraView.setVisibility(View.INVISIBLE);

                    // 아래 부분 주석을 풀 경우 사진 촬영 후에도 다시 프리뷰를 돌릴수 있음
                    //camera.startPreview();
                } catch (Exception e) {
                    Log.e("SampleCapture", "Failed to insert image.", e);
                }
            }
        });
    }

//    public void cropImage() {
//
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
//            this.grantUriPermission("com.android.camera", photoUri,
//                    Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
//        }
//        Intent intent = new Intent("com.android.camera.action.CROP");
//        intent.setDataAndType(photoUri, "image/*");
//
//        List<ResolveInfo> list = getPackageManager().queryIntentActivities(intent, 0);
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
//            grantUriPermission(list.get(0).activityInfo.packageName, photoUri,
//                    Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
//        }
//        int size = list.size();
//        if (size == 0) {
//            Toast.makeText(this, "취소 되었습니다.", Toast.LENGTH_SHORT).show();
//            return;
//        } else {
//            Toast.makeText(this, "용량이 큰 사진의 경우 시간이 오래 걸릴 수 있습니다.", Toast.LENGTH_SHORT).show();
//
//            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
//                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
//                intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
//            }
//            intent.putExtra("crop", "true");
//            intent.putExtra("aspectX", 1);
//            intent.putExtra("aspectY", 1);
//            intent.putExtra("scale", true);
//            File croppedFileName = null;
//            try {
//                croppedFileName = createImageFile();
//            } catch (IOException e) {
//                e.printStackTrace();
//            }
//
//            File folder = new File(Environment.getExternalStorageDirectory() + cropImageDiretory);
//            File tempFile = new File(folder.toString(), croppedFileName.getName());
//
//
//            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {//sdk 24 이상, 누가(7.0)
//                photoUri = FileProvider.getUriForFile(getApplicationContext(),// 7.0에서 바뀐 부분은 여기다.
//                        BuildConfig.APPLICATION_ID + ".provider", tempFile);
//            } else {//sdk 23 이하, 7.0 미만
//                photoUri = Uri.fromFile(tempFile);
//            }
//
//            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
//                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
//                intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
//            }
//
//            intent.putExtra("return-data", false);
//            intent.putExtra(MediaStore.EXTRA_OUTPUT, photoUri);
//            intent.putExtra("outputFormat", Bitmap.CompressFormat.JPEG.toString());
//
//            Intent i = new Intent(intent);
//            ResolveInfo res = list.get(0);
//            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
//                i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
//                i.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
//
//                grantUriPermission(res.activityInfo.packageName, photoUri,
//                        Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
//            }
//            i.setComponent(new ComponentName(res.activityInfo.packageName, res.activityInfo.name));
//            startActivityForResult(i, CROP_FROM_IMAGE);
//        }
//    }
}