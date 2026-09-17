# Intel RealSense ROS 2 Lyrical Setup

This file was created through human-in-the-loop claude

## Goal
Build the Intel RealSense ROS 2 driver (`realsense-ros`) for **ROS 2 Lyrical Luth** on **Ubuntu 26.04 (Resolute)**.

> **Note on `realsense2_camera` apt availability:** `realsense2_camera_msgs`
> and `realsense2_description` are already published for Lyrical
> (`apt search ros-lyrical-realsense2` will show them), but `realsense2_camera`
> itself is not yet, most likely because the ROS buildfarm hits the same
> `librealsense2` version gap this README works around below. So a source
> build of `realsense2_camera` is currently the way to go — there's no
> shortcut via `apt install ros-lyrical-realsense2-camera` yet. Worth
> re-checking `apt search` occasionally in case that changes.

---

## 0. Clean environment first

The build must use the **system Python** that matches your ROS 2 apt
packages, not Conda and not a pyenv shim — mixing interpreters can cause
subtle failures later even if early steps (like `import em`) appear to work.

```bash
conda deactivate 2>/dev/null
pyenv shell system 2>/dev/null   # or otherwise make sure no pyenv version is active

which python3        # should print /usr/bin/python3
python3 --version    # should match Ubuntu 26.04's system Python
python3 -c "import em; print(em.__file__)"   # should resolve under /usr/lib/python3/...
```

If `em` is missing on the system interpreter:
```bash
sudo apt install python3-empy
```

## 1. Create workspace

```bash
mkdir -p ~/realsense_ws/src
cd ~/realsense_ws/src
git clone -b ros2-master https://github.com/realsenseai/realsense-ros.git
```

(Pinning the branch explicitly avoids surprises if the repo's default
branch ever changes.)

## 2. Lyrical support in the driver

The cloned source already contains explicit Lyrical support in
`realsense2_camera/CMakeLists.txt`:

```cmake
elseif("$ENV{ROS_DISTRO}" STREQUAL "lyrical")
  message(STATUS "Build for ROS2 Lyrical")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DLYRICAL")
```

No modification needed here.

## 3. Install a matching RealSense SDK (librealsense2)

This is the step that was actually failing. The `ros2-master` branch's
`CMakeLists.txt` currently requires **librealsense2 ≥ 2.58.0**, but the
version shipped in the Lyrical ROS apt repo (`ros-lyrical-librealsense2`)
is **2.57.7** — it simply hasn't caught up yet. Don't try to fix this by
hunting for a newer `ros-lyrical-librealsense2`; install the standalone
SDK from RealSenseAI's own apt repo instead, which tracks newer releases
and (as of SDK v2.58.1) publishes packages for Ubuntu 26.04/Resolute.

> Note: the vendor recently renamed from Intel to RealSenseAI, and the apt
> repo/key moved from `librealsense.intel.com` to
> `librealsense.realsenseai.com`. Older tutorials referencing the `.intel.com`
> URL/key are stale.

```bash
sudo mkdir -p /etc/apt/keyrings
curl -sSf https://librealsense.realsenseai.com/Debian/librealsenseai.asc | \
  gpg --dearmor | sudo tee /etc/apt/keyrings/librealsenseai.gpg > /dev/null

sudo apt-get install -y apt-transport-https

echo "deb [signed-by=/etc/apt/keyrings/librealsenseai.gpg] https://librealsense.realsenseai.com/Debian/apt-repo $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/librealsense.list

sudo apt-get update
```

Check what's actually published for your codename before installing —
brand-new codenames (like `resolute`) may not have every package yet:
```bash
apt search librealsense2
```

On Resolute (26.04) at the time of writing, `librealsense2-dkms` is **not**
published — skip it. This is fine: `-dkms` exists to backport UVC metadata
support into older kernels, and Resolute's stock kernel (6.14+) already has
that support upstream. Install the rest:

```bash
sudo apt-get install -y librealsense2-utils librealsense2-dev librealsense2-dbg
```

If `apt-get install` still fails on a package name, re-run `apt search
librealsense2` and adjust the list to only packages actually shown — apt
aborts the *entire* install line if even one named package is missing, so a
single bad name silently prevents everything else (including
`librealsense2-dev`, which is the one you actually need) from installing.

Verify it actually installed:
```bash
apt-cache policy librealsense2
# "Installed:" should show a version ≥ 2.58.0, not "(none)"

dpkg -L librealsense2-dev | grep -i realsense2Config
# should list .../cmake/realsense2/realsense2Config.cmake
```

**Remove the ROS-packaged SDK to avoid a version conflict.** Keeping both
installed risks CMake's `find_package(realsense2)` resolving against
whichever is earlier on `CMAKE_PREFIX_PATH` — after sourcing
`/opt/ros/lyrical/setup.bash`, that's the older ROS one, not the SDK you
just installed. Once you've confirmed the standalone SDK works
(`realsense-viewer` detects your camera), remove the ROS one:

```bash
sudo apt purge ros-lyrical-librealsense2
```

## 4. Build

```bash
cd ~/realsense_ws
rm -rf build install log

source /opt/ros/lyrical/setup.bash
colcon build --symlink-install
```

## 5. Current status

| Component                   | Status |
|------------------------------|--------|
| ROS 2 Lyrical                 | ✓ |
| System Python (matches ROS)   | ✓ |
| `rosidl_adapter`              | ✓ |
| `realsense2_camera_msgs`      | ✓ |
| Lyrical support in driver     | ✓ |
| `librealsense2` ≥ 2.58.0      | ✓ (2.58.4 via RealSenseAI apt repo) |
| `realsense2_camera` build     | ✓ builds clean (only benign tf2/C++20 deprecation warnings) |
| `realsense2_description` build| ✓ |

## 6. Verify it actually works

Source the workspace (on top of ROS itself):
```bash
source /opt/ros/lyrical/setup.bash
source ~/realsense_ws/install/setup.bash
```

**Plug in the camera**, then confirm the SDK itself sees it (this bypasses
ROS entirely, so it isolates SDK/udev problems from ROS/build problems):
```bash
realsense-viewer
```
You should see the device listed and be able to stream color/depth. If it's
not detected here, it's a udev/permissions/USB issue, not a ROS one — check
`dmesg | tail` after plugging in, and confirm
`librealsense2-udev-rules` is installed (`dpkg -l | grep udev-rules`).
A replug or reboot after installing udev rules is sometimes needed.

Once `realsense-viewer` works, test the ROS wrapper:
```bash
ros2 launch realsense2_camera rs_launch.py
```

In a second terminal (after sourcing the workspace there too):
```bash
ros2 topic list
```
You should see topics like `/camera/camera/color/image_raw` and
`/camera/camera/depth/image_rect_raw`. Visually confirm a stream with:
```bash
ros2 run rqt_image_view rqt_image_view
```
and pick a `/camera/...image_raw` topic from the dropdown. Depth data is
flowing correctly if `ros2 topic hz /camera/camera/depth/image_rect_raw`
reports a steady rate matching your configured fps.

## Troubleshooting notes

- If `colcon build` still reports an old librealsense2 version after
  Step 3, run `hash -r` and open a fresh shell, then re-check
  `apt-cache policy librealsense2` and re-source
  `/opt/ros/lyrical/setup.bash` before building.
- If you'd rather not touch system apt packages, an alternative is to
  build `librealsense` from source (`development` branch) and point
  `CMAKE_PREFIX_PATH` at it — more control, more maintenance.