"""Build the editable synthetic PX-200 demo sources into citation-ready PDFs."""

from __future__ import annotations

from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "demo-corpus"
PAGE = pymupdf.paper_rect("a4")
DISCLAIMER = "SYNTHETIC PX-200 DEMONSTRATION DATA - NOT ABB EQUIPMENT"
CSS = """
* { font-family: Helvetica, sans-serif; color: #172033; font-variant-ligatures: none;
    font-feature-settings: "liga" 0; }
h1 { font-size: 25px; color: #b42318; margin: 0 0 8px; }
h2 { font-size: 16px; color: #244a70; margin: 13px 0 5px; }
p, li { font-size: 10.5px; line-height: 1.35; }
.meta { background: #fff1f0; border: 1px solid #d92d20; padding: 7px; font-weight: bold; }
.warning { background: #fff8e1; border-left: 4px solid #f59e0b; padding: 8px; }
table { border-collapse: collapse; width: 100%; margin-top: 7px; }
th, td { border: 1px solid #667085; padding: 5px; font-size: 9px; vertical-align: top; }
th { background: #e9f1f8; color: #173b5e; }
.figure { border: 2px solid #5b7792; padding: 18px; margin-top: 12px; text-align: center; }
.flow { font-size: 16px; font-weight: bold; color: #244a70; padding: 24px 0; }
.caption { font-size: 9px; font-weight: bold; text-align: left; }
"""


def add_page(document: pymupdf.Document, html: str, title: str) -> None:
    page = document.new_page(width=PAGE.width, height=PAGE.height)
    page.insert_text((42, 25), title, fontsize=8, color=(0.2, 0.3, 0.4))
    result = page.insert_htmlbox(pymupdf.Rect(42, 48, 553, 790), html, css=CSS)
    if result[0] < 0:
        raise RuntimeError(f"Demo content did not fit on page: {title}")
    page.insert_text(
        (42, 820),
        f"{DISCLAIMER}   |   Page {document.page_count}",
        fontsize=7,
        color=(0.55, 0.1, 0.08),
    )


def build_manual() -> None:
    document = pymupdf.open()
    add_page(
        document,
        """
        <h1>Sentinel PX-200 Pump Controller</h1>
        <p class="meta">Synthetic demonstration manual | Version 1.0 | Model PX-200<br>
        Created for ProofRAG. This document does not describe ABB equipment and must not be used
        to service real equipment.</p>
        <h2>1. Safety prerequisites</h2>
        <p class="warning"><b>Qualified personnel only.</b> Before opening the enclosure, stop the
        pump through the normal control sequence, isolate the upstream electrical disconnect,
        apply the site's lockout/tagout procedure, and verify absence of voltage with an approved
        tester. Wear the PPE required by the site risk assessment.</p>
        <p>Never bypass the door interlock, thermal switch, or motor-protection relay. Do not
        restart equipment when the cause of an over-temperature event remains unknown.</p>
        <h2>2. Status and fault codes</h2>
        <table><tr><th>Code</th><th>Meaning</th><th>Immediate response</th></tr>
        <tr><td>E-11</td><td>Inlet pressure below configured minimum</td><td>Stop the pump and
        inspect the supply path for a closed valve, blockage, or empty source tank.</td></tr>
        <tr><td>E-17</td><td>Controller cooling airflow restricted</td><td>Allow the controller to
        cool. After isolation, inspect the enclosure filter, fan intake, cooling fan, and
        J4.</td></tr>
        <tr><td>E-23</td><td>Motor current imbalance</td><td>Stop operation; inspect motor leads,
        terminals, and supply phase balance.</td></tr>
        <tr><td>W-05</td><td>Maintenance interval approaching</td><td>Schedule the applicable
        preventive-maintenance work order.</td></tr></table>
        """,
        "Sentinel PX-200 Pump Controller - Version 1.0",
    )
    add_page(
        document,
        """
        <h1>3. E-17 troubleshooting procedure</h1>
        <p>E-17 is raised when heat-sink temperature exceeds <b>70 C for more than 30 seconds</b>
        while the cooling-fan command is active.</p>
        <ol>
        <li>Stop the pump using the normal control sequence.</li>
        <li><b>Isolate electrical energy, apply lockout/tagout, and verify absence of voltage</b>
        before opening the enclosure.</li>
        <li>Wait at least five minutes for internal components to cool.</li>
        <li>Inspect the air inlet and enclosure filter. Clean or replace a blocked filter.</li>
        <li>Confirm the fan rotor turns freely and no cable or debris obstructs it.</li>
        <li>Inspect cooling-fan connector <b>J4</b> for looseness, corrosion, or damaged
        conductors.</li>
        <li>Restore the enclosure, remove lockout/tagout under site procedure, and run the
        diagnostic fan test.</li>
        <li>Return to service only when the fan test passes and heat-sink temperature remains
        below <b>55 C for ten minutes</b>.</li>
        </ol>
        <p class="warning">If E-17 returns, stop the controller and escalate to an authorized
        service technician. Do not repeatedly reset the fault.</p>
        <h2>4. Normal-condition cooling inspection</h2>
        <p>Under normal indoor conditions, inspect the enclosure filter every <b>500 operating
        hours</b>. Nominal fan speed is 2,400-3,200 rpm. A commanded speed below 1,800 rpm for more
        than 20 seconds triggers the fan diagnostic warning.</p>
        """,
        "Sentinel PX-200 Pump Controller - E-17 Procedure",
    )
    add_page(
        document,
        """
        <h1>5. Connector reference</h1>
        <p class="meta">Model PX-200 | Manual version 1.0</p>
        <table><tr><th>Connector</th><th>Function</th><th>Inspection notes</th></tr>
        <tr><td>J2</td><td>Inlet pressure sensor</td><td>Confirm the shield is terminated at the
        controller end only.</td></tr>
        <tr><td>J4</td><td>Cooling fan power and tachometer</td><td>Check latch engagement, pin
        seating, corrosion, and conductor damage.</td></tr>
        <tr><td>J7</td><td>Motor current sensors</td><td>Do not disconnect while
        energized.</td></tr>
        </table>
        <h2>Diagnostic interpretation</h2>
        <p>A fan command with no tachometer feedback can be caused by a loose J4 connection,
        damaged conductors, rotor obstruction, or a fan fault. Do not replace the fan solely from
        an E-17 indication; complete the procedure and diagnostic fan test.</p>
        """,
        "Sentinel PX-200 Pump Controller - Connector Table",
    )
    add_page(
        document,
        """
        <h1>6. Simplified cooling path</h1>
        <p>Keep at least <b>150 mm</b> clearance around the inlet and exhaust openings.</p>
        <div class="figure"><div class="flow">FILTERED LOWER INLET &rarr; J4-POWERED FAN
        &rarr; HEAT SINK &rarr; UPPER EXHAUST</div>
        <p class="caption">Figure 1: Cooling path from the filtered lower inlet through the
        J4-powered fan and heat sink to the upper exhaust. This caption is indexed by ProofRAG;
        it is not full diagram reasoning.</p></div>
        <h2>Inspection notes</h2>
        <p>Check that inlet and exhaust openings remain unobstructed. Inspect the filter media,
        fan rotor, and nearby cabling only after the safety prerequisites on page 1 are
        satisfied.</p>
        """,
        "Sentinel PX-200 Pump Controller - Cooling Path Figure",
    )
    document.set_metadata({"title": "Sentinel PX-200 Pump Controller", "subject": DISCLAIMER})
    document.save(OUTPUT / "sentinel_px200_manual_v1.pdf", garbage=4, deflate=True)
    document.close()


def build_bulletin() -> None:
    document = pymupdf.open()
    add_page(
        document,
        """
        <h1>Service Bulletin SB-PX200-04</h1>
        <p class="meta">Synthetic demonstration bulletin | Version 1.1 | Model PX-200<br>
        Not ABB equipment. Applies only under the conditions below.</p>
        <h2>Subject</h2><p>Reduced cooling-filter inspection interval in dusty or fiber-rich
        environments.</p>
        <h2>Applicability</h2><p>This bulletin applies to synthetic PX-200 controllers installed in
        woodworking, textile, aggregate-handling, or other locations where airborne dust or fibers
        can accumulate at the enclosure inlet.</p>
        <h2>Updated requirement</h2>
        <p class="warning">For affected installations, inspect the cooling filter every
        <b>250 operating hours or monthly, whichever occurs first</b>. This conditionally
        supersedes the 500-hour normal-condition interval in manual version 1.0 only for the
        environments listed above.</p>
        <p>Record filter condition and heat-sink temperature in the maintenance log. If two
        consecutive inspections find a blocked filter, assess enclosure placement and consider an
        approved higher-capacity filtration kit.</p>
        <h2>E-17 clarification</h2>
        <p>An E-17 event does not by itself prove the cooling fan has failed. A blocked filter,
        obstructed exhaust, loose J4 connector, or high ambient temperature can produce the same
        event. Follow the complete E-17 procedure and diagnostic fan test before replacing the
        fan.</p>
        <p class="warning">All electrical inspection remains subject to lockout/tagout and
        absence-of-voltage requirements in the base manual.</p>
        """,
        "Service Bulletin SB-PX200-04 - Version 1.1",
    )
    document.set_metadata({"title": "Service Bulletin SB-PX200-04", "subject": DISCLAIMER})
    document.save(OUTPUT / "sentinel_px200_service_bulletin_v1_1.pdf", garbage=4, deflate=True)
    document.close()


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_manual()
    build_bulletin()
    print("Built synthetic PX-200 manual and bulletin PDFs.")
