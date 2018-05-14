# World Wide 3D Telepresence - Demo
This repository contains the avango-guacamole code to showcase the final results of the image & point cloud based pipelines for compressing 3D video avatars. It is part of the World Wide 3D Telepresence project at vrsys group 2018 (Bauhaus University Weimar)

## Contents
This demo application is the last instance in a setup distributed across several code bases. It serves as the client instance in a compression pipeline that supports both image based and point cloud based compression of 3D video avatars. Therefore, it handles receiving of compressed data streams, decoding them and displaying contained data. For compressed image streams, a 3D reconstruction will be performed after decoding received data, while compressed point cloud data is displayed right after decompression. Furthermore, the application is able to configure compression by prompting the respective compression server to update its compression settings. Available settings can be adjusted using the key inputs visualized in the application GUI. The GUI additionally shows diagnostic data of the compression process to monitor performance of the pipeline at various settings. Finally, the avatars reconstructed from point cloud & image based compression can be moved and rotated using a SpaceMouse device.

## Setup
This codebase heavily relies on multiple dependencies maintained by vrsys group, like the OpenSource VR render engine [guacamole](https://github.com/vrsys/guacamole) and it's scriptable python wrapping [avango](https://github.com/vrsys/avango). [libpcc](https://github.com/b00dle/libpcc) is used from inside the spoints-plugin of guacamole to decode incoming point cloud based compression messages. Decoding of compressed image streams is handled by the video3d-plugin of guacamole, which utilizes a library for [Hybrid Lossless-Lossy Compression for Real-Time Depth-Sensor Streams in 3D Telepresence Applications](https://www.uni-weimar.de/fileadmin/user/fak/medien/professuren/Virtual_Reality/documents/publications/rgbd-compression_final_preprint_2015.pdf). For detailed instructions on how to install the dependencies, please refer to the respective repositories, or contact the vrsys group at Bauhaus University Weimar. 

This demo will not present any meaningful output unless the respective compression server instances are running. The following sections will explain in detail how to configure each of these.

### RGBD Calib (Montag55) <rgbd-server> / <play-server>

This project is used as the server for image based compression (`<rgbd-server>`), but also provides an interface to produce raw image streams (`<play-server>`).
```
$ > git clone https://github.com/Montag55/rgbd-calib.git
$ > mkdir build
$ > ccmake ..
$ > make install
```

#### Start <play-server>
Use these commands to start playback of raw image streams:
```
$ > cd rgbd-calib/install/bin
$ > ./rgbd_node_player -f <path-to-stream> -k 4 -s <play-server>:7050
```
, where `<path-to-stream>` should hold the path to a valid .stream file (e.g. `/mnt/telepresence/kinect_recordings/christmas2017/stream_02.stream`) and `<play-server>` is the IP adress of the machine used to run the playback of raw image streams. 

#### Start <rgbd-server>
Use these commands to receive raw image streams from a `<play-server>` and start an `<rgbd-server>`, which is responsible for compressing received raw image streams and forwarding them to a `<client>`:
```
$ > ./rgbd_compression_node -f <path-to-stream> -k 4 -b <calib-files> -m -2.0 0.0 -1.0 2.5 1.9 1.0 -q 0.02 -a 10 -r 2 -s 
$ > <rgbd-server>:7000 -c <client>:7001 -p <play-server>:7050 -d <client>:7051
```
`<path-to-stream>` is expected as a cmd argument but will not be used at program execution. Yet, it might help to identify the `<calib-files>` listed after the *-b* tag. Some sample values for these parameters would be:
- `<path-to-stream>` : /mnt/telepresence/kinect_recordings/christmas2017/stream_02.stream
- `<calib-files>` : /mnt/telepresence/kinect_recordings/christmas2017/23.cv /mnt/telepresence/kinect_recordings/christmas2017/24.cv /mnt/telepresence/kinect_recordings/christmas2017/25.cv /mnt/telepresence/kinect_recordings/christmas2017/26.cv

For `<rgbd-server>` insert the IP address of the network interface which should host the image based compression service. For `<client>` insert the IP adress of the machine from which configuration feedback is to be expected. Most likely this is the machine running this demo. `<play-server>` will again have to conatin the IP of the playback server sending raw image data.

### RGBD Recon (b00dle) <pcc-server>
This project is used as the server for point cloud based compression (`<pcc-server>`).
```
$ > git clone https://github.com/b00dle/rgbd-libpcc-recon.git
$ > mkdir build
$ > ccmake ..
$ > make install
```

#### Start <pcc-server>
To trigger reconstruction of raw image streams, compression of the resulting point cloud, and forwarding the created data to a client, call:
```
$ > cd rgbd-libpcc-recon/install/bin
$ > ./remote_rendering_server <surface-config>.ks -u <pcc-server>:7060 -d 1920 1080 -f <client>:7061
```
, where `<surface-config>.ks` provides the surface file denoting calibration of the raw image streams. The contents of this file should look something like this:
```
serverport <play-server>:7050
kinect 23.yml
kinect 24.yml
kinect 25.yml
kinect 26.yml
bbx -1.0 0.05 -1.0 1.0 2.2 1.0
normal 0 0 0
```
Here `<play-server>` again refers to the server sending raw image data over the network. `<pcc-server>` should reflect the IP of the machine hosting the point cloud compression server. As in the call instanciating the image based compression server, `<client>` refers to the IP of a client machine, which opens a port for sending feedback to the compression server. 

### RUNNING THIS DEMO <client>
If all of the above server instances are running, you should be good to start this demo. As a last step, ensure that avango and guacamole support both image compression inside video3d-plugin and point cloud compression using spoints-plugin. Also ensure that surface_23_24_25_26_pan_l.ks & spoints_resource_file.sr reflect your configuration:
- surface_23_24_25_26_pan_l.ks
```
serverport <rgbd-server>:7000
kinect <path-to>/23.yml
kinect <path-to>/24.yml
kinect <path-to>/25.yml
kinect <path-to>/26.yml
bbx -1 0.05 -1 1.0 2.2 1.0
normal 0 0 0
```
, where `<rgbd-server>` denotes the IP of the machine hosting image compression and all .yml files should reflect whichever calibration files are necessary for the image streams your avatars are based on.  
- points_resource_file.sr:
```
serversocket <pcc-server>:7060
feedbacksocket <client>:7061
```
, where `<pcc-server>` denotes the IP of the machine hosting point cloud compression and `<client>` refers to the IP of the machine executing this demo. Finally, to start the demo call:
```
$ > ./start.sh
```
Currently, this demo is optimized to run on a projection wall setup, using a Spacemouse and a Keyboard. If multiple keyboards are connected you might have to modify the `KEYBOARD_DEVICE_NUM` in `app.py`. In case you want to use a different viewing setup, some geometry might have to be placed differently. It should be easy to identify the right entrypoint for this by looking at the `setup_scene(graph)` function in `app.py`.





