"""
MIDI LIVE PLAYER PRO - VERSION 22 - WORKING VERSION
Simpel, funktionel, ingen crashes!
"""

...

# I _init_ui
        pads_layout = QtWidgets.QGridLayout()
        pads_layout.setSpacing(6)
        pads_layout.setContentsMargins(8, 18, 8, 8)   # yderligere luft over pads groupbox

        for i in range(12):
            pad = PadButton(i)
            self.pads.append(pad)
            r, c = divmod(i, 6)
            pads_layout.addWidget(pad, r, c)

        pads_group = QtWidgets.QGroupBox("🎹 Pads (12) - Right-click: Load, Left-click: Play/Stop")
        pads_group.setLayout(pads_layout)
        pads_group.setMaximumHeight(170)
        pads_group.setStyleSheet("""
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 12px; top: 2px;
                padding: 4px 10px 4px 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QGroupBox {
                margin-top: 28px;
            }
        """)

# Samt globalt: ret alle forekomster af "Version21" til "Version22"
# og øverst i filen: "MIDI LIVE PLAYER PRO - VERSION 22 - WORKING VERSION"