## FreeCAD Maker Workbench

This FreeCAD [external workbench](https://wiki.freecad.org/External_Workbench) is composed of: 
* a mechatronic components system
* an optic components system

The user can modify these components to customize their own system. This also includes a [Filter Stage](https://github.com/felipe-m/freecad_filter_stage) (see screenshot below)

![filter_stage](https://github.com/URJCMakerGroup/MakerWorkbench_Documentation/blob/master/parts/img/filter_stage.png)

All the models are parametric, meaning the user can set the dimensions dynamically, generate the preferred placement and the models will scale correctly. There are many models to choose from and create ones own Mechatronic system.

![sk](https://github.com/URJCMakerGroup/MakerWorkbench_Documentation/blob/master/parts/img/sk08.png)
![bracket](https://github.com/URJCMakerGroup/MakerWorkbench_Documentation/blob/master/parts/img/bracket_30x30_m6.png)
![motor_holder](https://github.com/URJCMakerGroup/MakerWorkbench_Documentation/blob/master/parts/img/nema17_holder_rail35_8.FCStd.png)
![bear_house](https://github.com/URJCMakerGroup/MakerWorkbench_Documentation/blob/master/parts/img/thinlinbearhouse1rail_lm8.png)
![aluprof](https://github.com/URJCMakerGroup/MakerWorkbench_Documentation/blob/master/parts/img/Profiles.png)
![clamp](https://github.com/URJCMakerGroup/MakerWorkbench_Documentation/blob/master/parts/img/Belt_clamp_simple.png)

You can see the Workbench in action in [YouTube](https://www.youtube.com/playlist?list=PLJAGaIjAPiFIkdTY4OOOegZvmtumLL3OK):

[![](http://img.youtube.com/vi/Fow7y8KEO1E/0.jpg)](http://www.youtube.com/watch?v=Fow7y8KEO1E "")

### Additional Functionality

1. Enable exporting the model selected to `STL` format for immediate 3D printing!!
2. Achieve creating an a basic assembly in **2 clicks**

You can see all the models on the [readthedocs](https://mechatronic.readthedocs.io/en/master/) page.


## Installation

### Automatic (recommended)

Install using the builtin FreeCAD [Addon Manager](https://wiki.freecad.org/AddonManager).  
In FreeCAD, go to the `Tools -> Addon manager` dropdown menu and search for **Maker Workbench**  

### Manual

<details>
<summary>Expand this section on how to install this workbench manually</summary>

- Identify the location of your personal FreeCAD folder 
    - On Linux it is usually `/home/username/.FreeCAD/Mod/`
    - On Windows it is `%APPDATA%\FreeCAD\Mod\` which is usually `C:\Users\username\Appdata\Roaming\FreeCAD\Mod\`
    - On macOS it is usually `/Users/username/Library/Preferences/FreeCAD/Mod/`

##### `git`

* `cd .FreeCAD/Mod` (create the `Mod/` folder if it doesn't exist)
* `git clone https://github.com/URJCMakerGroup/MakerWorkbench`
* Start FreeCAD

"MakerWorkbench" workbench should now show up in the [workbench dropdown list](https://wiki.freecad.org/Std_Workbench).

##### zip file

* Download Maker Workbench from the following [file](https://codeload.github.com/URJCMakerGroup/MakerWorkbench/zip/master).
* Extract the `MakerWorkbench-master` folder from the `MakerWorkbench.zip` and rename to `Maker` 
* Put this folder in the `Mod/` folder inside the `FreeCAD` installation folder mentioned above.

</details>

After install, restart FreeCAD. "MakerWorkbench" should now show up in the [workbench dropdown list](https://wiki.freecad.org/Std_Workbench).

## Documentation

All the information from the project is in the [readthedocs](https://makerworkbench.readthedocs.io/en/stable/) page.

## Source Code

The source code of this workbench is available in the official MakerWorkbench repository: https://github.com/URJCMakerGroup/MakerWorkbench

## Feedback

Do you have questions, found a bug, don't see a feature you'd love? Please leave us a comment on the official [FreeCAD Forum thread](https://forum.freecadweb.org/viewtopic.php?f=9&t=44498) discussion of MakerWorkbench (FYI, it used to be named Mechatronic until name was changed).

It is also possible to contact [davidmubernal](https://forum.freecadweb.org/memberlist.php?mode=viewprofile&u=30188) on the [FreeCAD forum](https://forum.freecadweb.org/) directly if you're having any issues but not getting any help on the forum thread.

## License

[LGPLv3](LICENSE)
