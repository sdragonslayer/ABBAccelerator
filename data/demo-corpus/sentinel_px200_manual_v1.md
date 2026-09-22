# Sentinel PX-200 Pump Controller

**Synthetic demonstration manual — Version 1.0**

This document was created for the ProofRAG hackathon prototype. It does not describe an ABB product and must not be used to service real equipment.

## 1. Safety prerequisites

Only qualified personnel may inspect the PX-200 controller. Before opening the enclosure, stop the pump through the normal control sequence, isolate the upstream electrical disconnect, apply the site's lockout/tagout procedure, and verify absence of voltage with an approved tester. Wear the PPE required by the site risk assessment.

Never bypass the door interlock, thermal switch, or motor-protection relay. Do not restart equipment when the cause of an over-temperature event remains unknown.

## 2. Status and fault codes

| Code | Meaning | Immediate response |
|---|---|---|
| E-11 | Inlet pressure below configured minimum | Stop the pump and inspect the supply path for a closed valve, blockage, or empty source tank. |
| E-17 | Controller cooling airflow restricted | Allow the controller to cool. After isolation, inspect the enclosure filter, fan intake, cooling fan, and connector J4. |
| E-23 | Motor current imbalance | Stop operation and have qualified personnel inspect motor leads, terminals, and supply phase balance. |
| W-05 | Maintenance interval approaching | Schedule the applicable preventive-maintenance work order. |

## 3. E-17 troubleshooting procedure

E-17 is raised when the controller heat-sink temperature exceeds 70 °C for more than 30 seconds while the cooling-fan command is active.

1. Stop the pump using the normal control sequence.
2. Isolate electrical energy, apply lockout/tagout, and verify absence of voltage before opening the enclosure.
3. Wait at least five minutes for internal components to cool.
4. Inspect the air inlet and enclosure filter. Clean or replace a blocked filter.
5. Confirm that the fan rotor turns freely and that no cable or debris obstructs it.
6. Inspect cooling-fan connector J4 for looseness, corrosion, or damaged conductors.
7. Restore the enclosure, remove lockout/tagout according to site procedure, and run the diagnostic fan test.
8. Return the pump to service only when the fan test passes and heat-sink temperature remains below 55 °C for ten minutes.

If E-17 returns after these checks, stop the controller and escalate to an authorized service technician. Do not repeatedly reset the fault.

## 4. Cooling system inspection

Under normal indoor conditions, inspect the enclosure filter every 500 operating hours. Replace damaged filter media rather than cleaning it. The diagnostic screen exposes fan speed, commanded fan state, and heat-sink temperature.

Nominal fan speed is 2,400–3,200 rpm. A commanded fan speed below 1,800 rpm for more than 20 seconds triggers the fan diagnostic warning.

## 5. Connector reference

| Connector | Function | Inspection notes |
|---|---|---|
| J2 | Inlet pressure sensor | Confirm the shield is terminated at the controller end only. |
| J4 | Cooling fan power and tachometer | Check latch engagement, pin seating, corrosion, and conductor damage. |
| J7 | Motor current sensors | Do not disconnect while energized. |

## 6. Simplified cooling path figure

The cooling path runs from the filtered lower enclosure inlet to the J4-powered fan and then across the heat sink toward the upper exhaust. Keep at least 150 mm of clearance around both inlet and exhaust openings.

