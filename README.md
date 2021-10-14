# pygdk
Python G-code Development Kit.  A library to directly generate gcode for CNC machines based directly on object features without abstract design, slicing, processing, etc.

## Disclaimer

Use this software at your own risk.  Check the gcode thoroughly before running it on your machine.  Everything you do with this software is your choice and responsibility.  I hope it ss useful, but I cannot be held responsible for injury or damage, even if it's due to errors in this software.  CNC machines are dangerous.  Be smart about it.

## Scope

This project makes a solid effort to produce generic, standard gcode that will run properly on any CNC controller.  It does not currently leverage any advanced or proprietary features/codes and if we add any of that sort of thing in the future, they'll be tied to machine profiles so they're only used when expressly configured.

That said, I am limited in platforms I can personally test.  I'm currently testing on:
* [Onefinity Woodworker](https://www.youtube.com/playlist?list=PLcYx-h_NNPJls4yDDPTMY_HnSE9GhaZ48) with the stock Onefinity-flavored [Buildbotics](https://buildbotics.com/) controller, [Teco L510-101-H1 VFD](https://amzn.to/3DCxXOm), and a cheap [1.5kW, 24kRPM, air-cooled spindle](https://amzn.to/3AQvYo1)
* [DIY Kossel (delta) 3D-Printer](https://www.wolfteck.com/kossel/) running a [knock-off Smoothieboard](https://amzn.to/3oXYHoj) and [OctoPi](https://octoprint.org/download/)
* [DIY CNC retrofit Rong Fu RF-30 Mill](https://www.wolfteck.com/mill/) running a [knock-off Smoothieboard](https://amzn.to/3oXYHoj) and [OctoPi](https://octoprint.org/download/)
* [DIY modernized Denford ORAC Lathe](https://www.wolfteck.com/orac/) running a [knock-off Smoothieboard](https://amzn.to/3oXYHoj)

If anyone is interested in providing feedback on other platforms, I'd love to hear it.

## Quickstart

Copy one of the scripts from any of the directories under `test/` to the root of this repo and run it.  It's not going to talk to your machine; it's just going to spit out gcode, so you're safe.  For this example, we're playing with [bangle.py](tests/things/bangle.py).

![quickstart](https://user-images.githubusercontent.com/6083980/137239013-e89898a2-ae35-41a1-bf87-28c250affb0d.png)

## Simulate

This step is technically optional, but it's good practice to simulate your gcode before you run it on your machine.  Even if you do everything right, `pygdk` is very early in development and is likely to have bugs that you can catch in simulation before anything bad happens in the real world.

Personally, I'm a fan of [CAMotics](https://camotics.org/) as it integrates with and is made by the same folks as the [buildbotics](https://buildbotics.com/) controller my Onefinity uses.

![simulate-terminal](https://user-images.githubusercontent.com/6083980/137239020-0cd2d64f-2b1b-4e1f-8036-32e0f41b7f32.png)
![simulate-camotics](https://user-images.githubusercontent.com/6083980/137239030-15445d6b-7a24-4ac7-95e6-963395a0263d.png)

The first time you run CAMotics, you'll need to setup your tool table by right-clicking in the blank Tool Table section and selecting `Load Tool Table`.  If you don't already have a tool table you want to use, you can load in [tools.json](tools.json) -- `pygdk`'s default tool table has more information in it than CAMotics can leverage, but it is backwards compatible.

## Execute

Once you're happy that the simulation doesn't show anything bad happening, you can copy the gcode to your machine however you would normally do it.  This might be via the machine's native web interface, a USB stick, OctoPrint, or you can even push gcode to BuildBotics controllers from inside CAMotics.

Take a deep breath, remember that you are personally responsible for everything good or bad that your machine does, then let it rip.

## API

### Machine

#### Initialization

```
from pygdk import Machine

machine = Machine('onefinity.json')
```

To get started, import the `Machine` class and create your primary `Machine` object that you'll use to do pretty much everything else.  Check out [onefinity.json](onefinity.json) for a fleshed out configuration and [rf30.json](rf30.json) for a minimal example.

#### Configuration

##### Material

```
machine.material = 'Soft Wood'
```

Defining your workpiece material is not required, but if you do,  `pygdk` will attempt to automatically determine appropriate feeds and speeds.  If you don't define it, you're on your own and will have to set your [feed](#feed) and [rpm](#rpm) manually before `pygdk` will generate your gcode.  Check out [feeds-and-speeds.json](feeds-and-speeds.json) for supported tool and workpiece materials.

##### Feed

```
machine.feed = 500
```

This is the feed for your cutting moves.  It is separate from `max_feed` which is the feed used for rapid (non-cutting) moves and is defined in your machine configuration JSON.  If you do not define the workpiece [material](#material) and tool specifications, you have to set the feed manually before `pygdk` can generate gcode.  Setting `feed` manually will override a previously calculated value.

##### Constant Surface Speed

```
machine.css = 1000
```

Constant Surface Speed is the speed of the cutter against the workpiece, regardless of the operation.  On a lathe, it's the speed the workpiece is passing by the stationary tool.  On a mill, it's the speed each flute of the endmill is sweeping through the workpiece.  CSS will be automatically set if you define your tool parameters and workpiece [material](#material).  If you find you have to set this manually, either because your tool/material combination is not currently in `pygdk`'s lookup table or because the values we have don't work well, please [cut an issue](https://github.com/cilynx/pygdk/issues) or send a PR with updated parameters to improve and extend [feeds-and-speeds.json](feeds-and-speeds.json).

When you set `css`, spindle [rpm](#rpm) will automatically be calculated and set for you.

##### RPM

```
machine.rpm = 15000
```

Spindle RPM is the speed at which your tool rotates.  If you define your tool parameters and workpiece [material](#material), `pygdk` will calculate and set `rpm` for you automatically.  Expressly setting `rpm` will override a previously calculated value.  If you find you're having to override automatically calculated values or manually set due to missing tool/material combinations, please [cut an issue](https://github.com/cilynx/pygdk/issues) or send a PR with updated parameters to improve and extend [feeds-and-speeds.json](feeds-and-speeds.json).

When you set `rpm` and have your tool parameters defined, [css](#css) will be automatically calculated and set for you.

#### Motion Primitives

##### Linear

```
machine.rapid(x,y,z)
machine.irapid(u,v,w)
machine.cut(x,y,z)
machine.icut(u,v,w)
```
`rapid` moves (`G0`) at `max_feed` without cutting to the absolute point [x,y,z] in the currently defined coordinate system.

`irapid` moves (`G0`) at `max_feed` without cutting to the relative point [u,v,w] away from the current position.

`cut` moves (`G1`) at `feed`, cutting to the absolute point [x,y,z] in the currently defined coordinate system.

`icut` moves (`G1`) at `feed`, cutting to the relative point [u,v,w] away from the current position.

All moves take an optional `comment` string parameter that will be included on the relevant line of gcode.

#### Canned Features

##### Bolt Circle
```
machine.bolt_circle(c_x, c_y, n, r, depth)
```
`c_x` is the x coordinate of the center of the bolt circle

`c_y` is the y coordinate of the center of the bolt circle

`n` is the number of bolt holes to put around the perimeter

`r` is the radius of the bolt circle

`depth` is how deep to drill each hole

![bolt-circle](https://user-images.githubusercontent.com/6083980/137250363-e744a8eb-860a-4469-b524-80b671dd2edd.png)


##### Circular Pocket
```
machine.circular_pocket(c_x, c_y, diameter, depth, step=None, finish=0.1, retract=True)
```
`c_x` is the x coordinate of the center of the pocket

`c_y` is the y coordinate of the center of the pocket

`diameter` is the diameter of the pocket

`depth` is how deep to make the pocket

`step` is how much material to take off with each pass, but will be automatically calculated if not provided

`finish` is how much material to leave for the finishing pass

`retract` is whether or not to retract the cutter to a safe position outside of the pocket after completing the operation

![circular-pocket](https://user-images.githubusercontent.com/6083980/137250689-43b0f195-f6cc-4d5e-94e5-74d3525a861e.png)

##### Frame
```
machine.frame(c_x, c_y, x, y, z_top=0, z_bottom=0, z_step=None, inside=False, r=None, r_steps=10)
```
Like [helix](#helix), but rectangular.

`c_x` is the x coordinate of the center of the frame

`c_y` is the y coordinate of the center of the frame

`x` is the x-dimension of the frame

`y` is the y-dimension of the frame

`z_top` is the top of the frame -- usually 0

`z_bottom` is the bottom depth of the frame -- usually something negative

`z_step` is how far down z to move with each pass

`inside` is whether the cutter is inside or outside the requested dimensions

`r` is the corner radius

![frame](https://user-images.githubusercontent.com/6083980/137252297-1ebdec8d-ee64-4b0c-aaa6-543420e4dc3b.png)

##### Helix
```
machine.helix(c_x, c_y, diameter, depth, z_step=0.1, outside=False, retract=True):
```
Follows a circular path in [x,y] while steadily spiraling down in z.

`c_x` is the x coordinate of the center of the helix

`c_y` is the y coordinate of the center of the helix

`diameter` is the diameter of the helix

`depth` is how deep to cut in total

`z_step` is how far to move down for each rotation of the helix

If `outside` is `False` (the default), the cutter will run inside the requested diameter.  If `outside` is `True`, the cutter will run outside the requested diameter.

`retract` is whether or not to retract the cutter to a safe position outside of the helix after performing the operation.  If you're moving somewhere else, you probably want it to be `True`, but if you're going to slot off sideways from within the helix, you might want it to be `False`.
![helix](https://user-images.githubusercontent.com/6083980/137249644-4cf520f9-4083-4cbe-8c00-a45dc1e342a2.png)

##### Mill Drill
```
machine.mill_drill(c_x, c_y, diameter, depth, z_step=0.1, retract=True)
```
Uses a [helix](#helix) under the hood to drill a hole that is up to 2x the diameter of the endmill being used.

`c_x` is the x coordinate of the center of the hole

`c_y` is the y coordinate of the center of the hole

`diameter` is the diameter of the hole

`depth` is how deep to drill

`z_step` is how far to move down for each rotation of the helix

`retract` is whether or not to retract the cutter to a safe position outside of the hole after performing the operation.  Generally, you probably want to do this so it defaults to `True`, but it's useful to set to `False` when mill-drilling to start a pocket.

![mill-drill](https://user-images.githubusercontent.com/6083980/137251022-33a3c253-004b-44fd-8bb2-042e972b77ca.png)

##### Pocket Circle
```
machine.pocket_circle(c_x, c_y, n, r, depth, diameter)
```
Like a Bolt Circle, but all the holes are Circular Pockets

`c_x` is the x coordinate of the center of the pocket circle

`c_y` is the y coordinate of the center of the pocket circle

`n` is the number of pocket holes to put around the perimeter

`r` is the radius of the pocket circle

`depth` is how deep to mill each pocket

`diameter` is the diameter of each pocket
![pocket-circle](https://user-images.githubusercontent.com/6083980/137251587-468bf3a2-a7b2-499a-bf86-30552391bbb6.png)

##### Rectangular Pocket
```
machine.rectangular_pocket(c_x, c_y, x, y, z_top=0, z_bottom=0, z_step=None undercut=False, retract=True):
```

`c_x` is the x coordinate of the center of the pocket

`c_y` is the y coordinate of the center of the pocket

`x` is the x-dimension of the pocket

`y` is the y-dimension of the pocket

`z_top` is the top of the pocket -- usually 0

`z_bottom` is the bottom depth of the pocket -- usually something negative

`z_step` is how far down z to move with each pass when initially spiraling in

`undercut` is whether or not to put "mouse ears" in the corners to provide clearance for sharp corners to mate into the pocket

![rectangular-pocket](https://user-images.githubusercontent.com/6083980/137253197-dc26e02b-4a58-453d-ae6d-ee3afbafa049.png)
