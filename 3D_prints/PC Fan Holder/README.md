# 👋 Sub-canopy Air Movement Using PC Fans for Grow Tents
The PC fan system combines waterproof fans, 3D-printed parts, and marine-grade wiring to create a customizable air circulation solution for under the plant canopy. Key components include a level of water proofing, marine grade wiring that uses T-tap connectors for easy assembly without soldering, swiveling fan holders to adjust the in place angle of air flow, ground-insertable posts to position close to the plant area that needs the circulation. This DIY approach balances durability, flexibility, and ease of implementation.  It has been "good enough" in smaller grow spaces like indoor grow tents.  The design is intended for these type of grow tents and not indoor commercial facilities.

> **Note** This project is a hobbyist-level DIY effort, combining electronics, software, and gardening. It's not professionally engineered or tested, and comes with no guarantees. The design builds upon and modifies work shared by other makers in the community, without whom this wouldn't be possible. It's shared to potentially inspire or assist other hobbyists, but may not be suitable for serious applications.

This guide provides instructions on building and using a PC fan holder for your grow tent. It covers the 3D-printed parts, wiring, and power setup.

### 🌱 In the Grow Tent
The image here shows the integrated system in the grow tent. The intent is to give an overview of how everything fits together.
TODO: NEED AN IMAGE

The image serves to visualize:
- the PC Fans can be placed anywhere within the soil. Once placed, the fan can tilt a bit to adjust to create targeted airflow patterns for specific areas.

#### ❤️ 🙏 Thanks to Those That Went Before
**Thank you to the kind, and amazingly gifted folks that share their work.**  It is far easier for me to modify an existing design/implemenation than to forge an unchartered path.
- The actual fan holder parts is a modification of [**Brundak's** Fan holder - desk fan on printables](https://www.printables.com/model/272507-fan-holder-desk-fan)
- The stake is a modification of [the tent stake designed by **mistertech**](https://www.thingiverse.com/thing:2758339).

## 📜BoM
The pieces to put together this fan system include:

| Item     | Cost | Description |
|----------|----------|----------|
|[Cable Wire](https://amzn.to/3zxIo8Z)  | $10  | 66ft 22awg 2pin Wires.   |
|[T Tap Wire Connector](https://amzn.to/3XHGnkH)    | $10  | Solderless No Stripping 3 Way Wire Connector.   |
|[3D Print of fan holder parts](PC Fan Holder)    | Data 5   | See the image of the 3D Printed pieces.   |
|[PC Fans](https://www.amazon.com/gp/product/B0CQ85P43Z/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8)   | $16   | Waterproof DC Cooling Fan Dual. |
| 12V Power Supply | Depends | Please see the comments under the Power Supply heading. |

### 🔗Cable wires and T Tap Connector
A challenge with grow tents and electrical projects is dealing with water and dirt. If the wiring is hidden within a moving vehicle, add in vibration and the access to the cables once installed.  This DIY method may not be as robust as commercially available solutions, but is "good enough". The wiring and connections are the result of years of experimentation, balancing ease of implementation (e.g.: avoids soldering) and some protection from dirt and water (e.g.: a level of waterproofing and the closed/covered connectors).

### 🔌 Power Supply
The fans are wired in parallel.  The following principles apply:
- The **voltage** across each component in parallel is the same.
- The **current** is the sum of the currents through each of the devices/loads drawing power.

The PC fans in this setup operate at 12V, drawing 0.16A each. The power supply should be rated for 12V with a current capacity of n × 0.16A, where n is the number of fans. For instance, a 3-fan system requires 0.48A (3 × 0.16A).

It's important to overspec the power supply to prevent overheating and a potential fires. For the 3-fan example, a 12V 1A power supply provides ample headroom, ensuring safe and reliable operation.

## 🔩 Assembly
### 🛠️ Tools
- A DMM(Digital MultiMeter) is always useful when working with electronics.  It really helps with debugging the circuit.  This is the one I have used for quite awhile:
<p align="center">
  <img src="dmm.jpg" alt="DMM" height="400" />
</p>

- A pair of (small works great) wire clippers or scissors. The cables are only 22AWG gauge so scissors will work fine.

- Access to a 3D printer to print the fan holder parts.

### 👣 Assembly Steps
#### 🖨️ 3D Printed Parts
1. 🖨️ Print out the parts.

> **Note** Each PC fan requires it's own set of 3D printed parts.

This document asumes familiarity with 3D printing.   The components in the image were printed on a [Prusa MK3S](https://www.prusa3d.com/category/original-prusa-i3-mk3s/) using two-year-old PLA filament with default PLA settings.

There are three different pieces that come together to make the fan holder.
<p align="center">
  <img src="80mm_fan_holder_pieces_.jpg" alt="Fan Holder pieces" height="300" />
</p>

Here are the components put together:
<p align="center">
  <img src="80mm_with_fan_assembled.jpg" alt="Each Fan" height="300" />
</p>

Refer to the above image to map the file to the 3D printed component.  Each one needs to be printed for each fan.
##### 👩‍💻 Print out the Parts
The files for printing include:

- fan_holder (PART 1)v2.3mf

> **Note:** A .3MF file (3D Manufacturing Format) is a file format used for 3D printing. It contains a mesh, which is a collection of vertices, edges, and faces that defines the shape of a 3D object.  The file format evolves the STL file format with additional information such as colors, textures, materials, and other properties. This file was created by Fusion 360. It is typically opened within slicer software.  PrusaSlicer was used to print the components on the MK3S 3D Printer.

- post (Part 2)v3.3mf

- Nut (Part3).stl

With a set printed for each fan, assembly begins.

2. 🏗️ Assemble

Mount the fan holder (Part 1) to the PC fan using the long bolts provided by the fan distributors. The first screw will go in easily. To align the holes for the second screw, squeeze the fan holder until the holes line up. Next, wrap a small strip of duct tape around the ball of the fan holder (Part 1) to ensure a snug fit. Place the nut (Part 3) on the neck of the fan holder. Press the taped ball into the hole of the post (Part 2), then screw the nut down onto the post. Be aware that the plastic-on-plastic connection may make it difficult to screw down far, but it should grasp and tighten a bit.

Repeat for each fan holder unit.

> **NOTE** The PC fan should be able to swivel a bit.

### 🔗 Wiring
1. Lay out the end-end length of cable.
2. Space out the T-tap connectors along the length of cable where you want to place the fans and the power source.
3. Connect the fan and power source to the cable. You can attach the fans to the connectors first or the connectors to the long wire first, whichever you prefer. **It's crucial to follow the wiring diagram shown in the images below**. The chosen connectors provide shielding and a secure connection without requiring soldering. However, they have drawbacks: the connection relies on pricking the cable rather than a full solder with heat shield, which introduces friction. Additionally, clamping the plastic lids securely requires significant force. Despite these minor issues, this wiring and connection method has proven most effective for low-power DC devices like PC fans.

> **Note** Consider running connectivity tests between different wire inputs and outputs.  It is easier to do this now than to wait when everything is wired up.  It is best to go slow and verify step by step when wiring.

<p align="center">
  <img src="t-way-connector-1.jpg" alt="t-way connector 1" height="300" />
</p>

<p align="center">
  <img src="t-way-connector-2.jpg" alt="t-way connector 2" height="300" />
</p>
> Note: **Carefully verify the wiring, ensuring the red and black wires are in their correct positions. After checking, double-check again.** It's surprisingly to have wires crossed, so this extra step of verification is crucial.

4. Test the circuit before plugging in the power supply. Follow these steps:
  - Walk through the troubleshooting steps.
  - Plug in the power supply.
  - Check if the fans move and there's no smoke.
  - Unplug the power supply.

  If everything looks good, move to the next step. If not, move to the troubleshooting section.

----- Move foward if all is working -----

5. Set up the fan system in your grow tent, carefully positioning each post and fine-tuning fan tilt to create an ideal microclimate for your plants.

6. Turn the fans on.

Done 🙌😺😃😺🙌

#### 😟 Troubleshooting

You plug in the power supply and nothing happens.  Common causes include:
1. The connector has wires crossed.  View the above images closely and verify they match your wiring.
2. There is not an end to end connection.  Run connectivity tests between the input and output wires.
3. The power supply is not working - use a DMM to determine if there is a 12V DC Voltage reading.
4. Verify the power supply is 12V and can handle a load of n x 0.16A where n = the number of PC fans running in parallel along the wired circuit.
5. If you encounter a bug, have a feature request, or need assistance, submit an issue by navigating to the Issues tab of this repository.

## 👋 Bye for now

Thank you for following this guide. If you have any questions or need further assistance, please open an issue on GitHub.

😺 Please find many things to smile about. 😀

