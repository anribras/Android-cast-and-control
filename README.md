## An easy and handy tool for Android Cast and Control

Have you ever been rolled in  such circumstance, that your Android device screen(A phone, TV, broken dev board or whatever) is broken, you can't see anything on it although it's still running, or in a research team, that there are not enough really expensive screen for usage ?

This is for you. A handy tool implemented by python3,which can cast Android screen into PC on most platforms ,like Windows,Linux and Mac OS, and control it by mouse as if you're touching on your devices.

### Install and enable ADB first

Our work is based on adb bridge to apply a `tcp over usb` strategy. So you need install an adb on your computer firstly. It's easy to be done by google it.
And you should `enable adb debug mode` on your device ,or else nothing will work on it.


### Prepare and run

I recommended you firstly install `miniconda` to manage your python environment.
(https://conda.io/miniconda.html)

It's ok not to do so, but ensure you have the right `python 3.6.6` environment.(Have't tested for other 3.x version but should be OK)


You can go on by following commands below:
```
# install python 3.6.6 indeed
conda create -n pylink python=3.6
```

Check out `pip` has switched into the python3.6 version.

```
which pip
```

Then install neccessary package `wxpython`.

```
pip install -U wxpython
```
CD into our project,run a test program:

```
python -m ui
```

See a GUI window promp out means OK. Colse it, Next connect your device with PC, and finally run:
```
python -m pylink
```

Thas' all of it for windows and linux, but bit more need to do for Mac Os.

```
conda install python.app
```

Then run python by

```
pythonw -m pylink
```

Why `pythonw` ,not `python`? Well, here is the [answer...](https://stackoverflow.com/questions/43707656/how-to-use-a-framework-build-of-python-with-anaconda)

### Changing your settings


