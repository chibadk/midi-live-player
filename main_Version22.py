"""
MIDI LIVE PLAYER PRO - VERSION 22 - WORKING VERSION
Simpel, funktionel, ingen crashes!
"""

import json
import logging
import sys
import time
import traceback
from pathlib import Path
from threading import Thread, Lock
from typing import Dict, List, Optional

try:
    import mido
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install mido python-rtmidi PySide6")
    sys.exit(1)

# ============================================================================
# LOGGING
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("MidiPlayer")

# ============================================================================
# CONSTANTS
# ============================================================================
APP_TITLE = "🎤 MIDI Live Player PRO"
MIDI_CHANNELS = range(1, 17)

THEMES = {
    "dark": """
        QMainWindow, QWidget, QDialog { background: #1e1e1e; color: #e8e8e8; }
        QMenuBar { background: #2a2a2a; color: #e8e8e8; }
        QMenuBar::item:selected { background: #3a3a3a; }
        QMenu { background: #2a2a2a; color: #e8e8e8; }
        QMenu::item:selected { background: #3a3a3a; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #2d2d2d; color: #e8e8e8; border: 1px solid #555;
            border-radius: 3px; padding: 4px;
        }
        QPushButton {
            background: #3a3a3a; color: #e8e8e8; border: 1px solid #555;
            border-radius: 3px; padding: 4px 8px; font-weight: bold;
        }
        QPushButton:hover { background: #484848; }
        QPushButton:pressed { background: #2a2a2a; }
        QSlider::groove:vertical { background: #333; width: 8px; border-radius: 4px; }
        QSlider::handle:vertical {
            background: #00d26a; border-radius: 4px; margin: 0 -4px;
            width: 16px; height: 10px;
        }
        QToolButton {
            background: #3a3a3a; color: #e8e8e8; border: 1px solid #555;
            border-radius: 3px; padding: 2px; font-size: 9px;
        }
        QToolButton:hover { background: #484848; }
        QToolButton:checked { background: #00d26a; color: #000; font-weight: bold; }
        QListWidget { background: #252525; color: #e8e8e8; border: 1px solid #444; border-radius: 3px; }
        QListWidget::item:selected { background: #00d26a; color: #000; font-weight: bold; }
        QLabel { background: transparent; color: #e8e8e8; }
        QGroupBox { border: 1px solid #444; border-radius: 4px; margin-top: 8px; padding-top: 6px; font-weight: bold; }
        QFrame { background: #252525; border: 1px solid #333; border-radius: 3px; }
        QSplitter::handle { background: #444; }
        QSplitter::handle:hover { background: #666; }
    """,
    "light": """
        QMainWindow, QWidget, QDialog { background: #f5f5f5; color: #222; }
        QMenuBar { background: #eaeaea; color: #222; }
        QMenuBar::item:selected { background: #d0d0d0; }
        QMenu { background: #eaeaea; color: #222; }
        QMenu::item:selected { background: #d0d0d0; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #fff; color: #222; border: 1px solid #bbb;
            border-radius: 3px; padding: 4px;
        }
        QPushButton {
            background: #e8e8e8; color: #222; border: 1px solid #bbb;
            border-radius: 3px; padding: 4px 8px; font-weight: bold;
        }
        QPushButton:hover { background: #d0d0d0; }
        QPushButton:pressed { background: #c0c0c0; }
        QSlider::groove:vertical { background: #ddd; width: 8px; border-radius: 4px; }
        QSlider::handle:vertical {
            background: #0066cc; border-radius: 4px; margin: 0 -4px;
            width: 16px; height: 10px;
        }
        QListWidget { background: #fff; color: #222; border: 1px solid #ccc; border-radius: 3px; }
        QListWidget::item:selected { background: #0066cc; color: #fff; font-weight: bold; }
        QLabel { background: transparent; color: #222; }
        QGroupBox { border: 1px solid #ccc; border-radius: 4px; margin-top: 8px; padding-top: 6px; font-weight: bold; }
        QFrame { background: #f9f9f9; border: 1px solid #ddd; border-radius: 3px; }
        QSplitter::handle { background: #ccc; }
        QSplitter::handle:hover { background: #999; }
    """,
    "midnight": """
        QMainWindow, QWidget, QDialog { background: #0f172a; color: #e2e8f0; }
        QMenuBar { background: #1e293b; color: #e2e8f0; }
        QMenuBar::item:selected { background: #334155; }
        QMenu { background: #1e293b; color: #e2e8f0; }
        QMenu::item:selected { background: #334155; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #1e293b; color: #e2e8f0; border: 1px solid #475569;
            border-radius: 3px; padding: 4px;
        }
        QPushButton {
            background: #334155; color: #e2e8f0; border: 1px solid #475569;
            border-radius: 3px; padding: 4px 8px; font-weight: bold;
        }
        QPushButton:hover { background: #475569; }
        QSlider::groove:vertical { background: #1e293b; width: 8px; border-radius: 4px; }
        QSlider::handle:vertical {
            background: #93c5fd; border-radius: 4px; margin: 0 -4px;
            width: 16px; height: 10px;
        }
        QListWidget { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 3px; }
        QListWidget::item:selected { background: #93c5fd; color: #000; font-weight: bold; }
        QLabel { background: transparent; color: #e2e8f0; }
        QGroupBox { border: 1px solid #334155; border-radius: 4px; margin-top: 8px; padding-top: 6px; font-weight: bold; }
        QFrame { background: #1e293b; border: 1px solid #334155; border-radius: 3px; }
        QSplitter::handle { background: #334155; }
        QSplitter::handle:hover { background: #475569; }
    """,
    "forest_green": """
        QMainWindow, QWidget, QDialog { background: #1a3a1a; color: #c8e6c9; }
        QMenuBar { background: #2e5c2e; color: #c8e6c9; }
        QMenuBar::item:selected { background: #3d7a3d; }
        QMenu { background: #2e5c2e; color: #c8e6c9; }
        QMenu::item:selected { background: #3d7a3d; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #1a3a1a; color: #c8e6c9; border: 1px solid #4caf50;
            border-radius: 3px; padding: 4px;
        }
        QPushButton {
            background: #2e5c2e; color: #c8e6c9; border: 1px solid #4caf50;
            border-radius: 3px; padding: 4px 8px; font-weight: bold;
        }
        QPushButton:hover { background: #3d7a3d; }
        QSlider::groove:vertical { background: #1a3a1a; width: 8px; border-radius: 4px; }
        QSlider::handle:vertical {
            background: #66bb6a; border-radius: 4px; margin: 0 -4px;
            width: 16px; height: 10px;
        }
        QListWidget { background: #1a3a1a; color: #c8e6c9; border: 1px solid #4caf50; border-radius: 3px; }
        QListWidget::item:selected { background: #66bb6a; color: #000; font-weight: bold; }
        QLabel { background: transparent; color: #c8e6c9; }
        QGroupBox { border: 1px solid #4caf50; border-radius: 4px; font-weight: bold; }
        QFrame { background: #1a3a1a; border: 1px solid #2e5c2e; border-radius: 3px; }
        QSplitter::handle { background: #2e5c2e; }
        QSplitter::handle:hover { background: #4caf50; }
    """,
    "red_passion": """
        QMainWindow, QWidget, QDialog { background: #3a1a1a; color: #ffcccc; }
        QMenuBar { background: #5c2e2e; color: #ffcccc; }
        QMenuBar::item:selected { background: #7a3d3d; }
        QMenu { background: #5c2e2e; color: #ffcccc; }
        QMenu::item:selected { background: #7a3d3d; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #3a1a1a; color: #ffcccc; border: 1px solid #ef5350;
            border-radius: 3px; padding: 4px;
        }
        QPushButton {
            background: #5c2e2e; color: #ffcccc; border: 1px solid #ef5350;
            border-radius: 3px; padding: 4px 8px; font-weight: bold;
        }
        QPushButton:hover { background: #7a3d3d; }
        QSlider::groove:vertical { background: #3a1a1a; width: 8px; border-radius: 4px; }
        QSlider::handle:vertical {
            background: #f44336; border-radius: 4px; margin: 0 -4px;
            width: 16px; height: 10px;
        }
        QListWidget { background: #3a1a1a; color: #ffcccc; border: 1px solid #ef5350; border-radius: 3px; }
        QListWidget::item:selected { background: #f44336; color: #fff; font-weight: bold; }
        QLabel { background: transparent; color: #ffcccc; }
        QGroupBox { border: 1px solid #ef5350; border-radius: 4px; font-weight: bold; }
        QFrame { background: #3a1a1a; border: 1px solid #5c2e2e; border-radius: 3px; }
        QSplitter::handle { background: #5c2e2e; }
        QSplitter::handle:hover { background: #ef5350; }
    """,
    "brown_wood": """
        QMainWindow, QWidget, QDialog { background: #3e2723; color: #d7ccc8; }
        QMenuBar { background: #5d4037; color: #d7ccc8; }
        QMenuBar::item:selected { background: #6d4c41; }
        QMenu { background: #5d4037; color: #d7ccc8; }
        QMenu::item:selected { background: #6d4c41; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #3e2723; color: #d7ccc8; border: 1px solid #a1887f;
            border-radius: 3px; padding: 4px;
        }
        QPushButton {
            background: #5d4037; color: #d7ccc8; border: 1px solid #a1887f;
            border-radius: 3px; padding: 4px 8px; font-weight: bold;
        }
        QPushButton:hover { background: #6d4c41; }
        QSlider::groove:vertical { background: #3e2723; width: 8px; border-radius: 4px; }
        QSlider::handle:vertical {
            background: #8d6e63; border-radius: 4px; margin: 0 -4px;
            width: 16px; height: 10px;
        }
        QListWidget { background: #3e2723; color: #d7ccc8; border: 1px solid #a1887f; border-radius: 3px; }
        QListWidget::item:selected { background: #8d6e63; color: #fff; font-weight: bold; }
        QLabel { background: transparent; color: #d7ccc8; }
        QGroupBox { border: 1px solid #a1887f; border-radius: 4px; font-weight: bold; }
        QFrame { background: #3e2723; border: 1px solid #5d4037; border-radius: 3px; }
        QSplitter::handle { background: #5d4037; }
        QSplitter::handle:hover { background: #a1887f; }
    """,
    "ocean_blue": """
        QMainWindow, QWidget, QDialog { background: #0d1b2a; color: #b3e5fc; }
        QMenuBar { background: #1a2a3a; color: #b3e5fc; }
        QMenuBar::item:selected { background: #2a3f57; }
        QMenu { background: #1a2a3a; color: #b3e5fc; }
        QMenu::item:selected { background: #2a3f57; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background: #0d1b2a; color: #b3e5fc; border: 1px solid #0288d1;
            border-radius: 3px; padding: 4px;
        }
        QPushButton {
            background: #1a2a3a; color: #b3e5fc; border: 1px solid #0288d1;
            border-radius: 3px; padding: 4px 8px; font-weight: bold;
        }
        QPushButton:hover { background: #2a3f57; }
        QSlider::groove:vertical { background: #0d1b2a; width: 8px; border-radius: 4px; }
        QSlider::handle:vertical {
            background: #0288d1; border-radius: 4px; margin: 0 -4px;
            width: 16px; height: 10px;
        }
        QListWidget { background: #0d1b2a; color: #b3e5fc; border: 1px solid #0288d1; border-radius: 3px; }
        QListWidget::item:selected { background: #0288d1; color: #fff; font-weight: bold; }
        QLabel { background: transparent; color: #b3e5fc; }
        QGroupBox { border: 1px solid #0288d1; border-radius: 4px; font-weight: bold; }
        QFrame { background: #0d1b2a; border: 1px solid #1a2a3a; border-radius: 3px; }
        QSplitter::handle { background: #1a2a3a; }
        QSplitter::handle:hover { background: #0288d1; }
    """,
}

# ============================================================================
# GLOBAL STATE
# ============================================================================
main_window = None

# ============================================================================
# PLAYBACK WORKER
# ============================================================================

class PlaybackWorker(QtCore.QObject):
    """MIDI playback in thread."""
    
    statusChanged = QtCore.Signal(str)
    bpmChanged = QtCore.Signal(float)
    lyricChanged = QtCore.Signal(str)
    finished = QtCore.Signal()
    requestNext = QtCore.Signal()
    noteOn = QtCore.Signal(int)
    noteOff = QtCore.Signal(int)
    levelUpdate = QtCore.Signal(int, int)
    
    def __init__(self, path: Path, tempo: float = 1.0):
        super().__init__()
        self.path = path
        self.tempo = tempo
        self.port = None
        
        self.is_running = False
        self.should_stop = False
        self.is_paused = False
        self.lock = Lock()
    
    def set_port(self, port):
        self.port = port
    
    def set_tempo(self, tempo: float):
        with self.lock:
            self.tempo = max(0.25, min(2.0, tempo))
    
    def pause(self):
        self.is_paused = True
        self.statusChanged.emit("⏸ Paused")
    
    def resume(self):
        self.is_paused = False
        self.statusChanged.emit("▶ Playing")
    
    def stop(self):
        self.should_stop = True
    
    @QtCore.Slot()
    def run(self):
        """Main playback."""
        self.is_running = True
        self.should_stop = False
        
        try:
            self.statusChanged.emit(f"▶ {self.path.name}")
            
            mf = mido.MidiFile(str(self.path))
            self.bpmChanged.emit(120.0)
            
            for msg in mf.play(meta_messages=True):
                if self.should_stop:
                    break
                
                while self.is_paused and not self.should_stop:
                    time.sleep(0.05)
                
                if self.should_stop:
                    break
                
                with self.lock:
                    tempo = self.tempo
                
                wait = float(getattr(msg, "time", 0.0)) / max(0.25, tempo)
                if wait > 0:
                    time.sleep(wait)
                
                if self.should_stop:
                    break
                
                if msg.is_meta:
                    if msg.type == "set_tempo":
                        try:
                            bpm = mido.tempo2bpm(msg.tempo)
                            self.bpmChanged.emit(float(bpm))
                        except Exception:
                            pass
                    elif msg.type in ("lyrics", "text"):
                        text = getattr(msg, "text", "")
                        if text and isinstance(text, str):
                            self.lyricChanged.emit(text)
                    continue
                
                if hasattr(msg, 'type'):
                    if msg.type == 'note_on':
                        ch = int(getattr(msg, 'channel', 0)) + 1
                        vel = int(getattr(msg, 'velocity', 0))
                        if vel > 0:
                            self.noteOn.emit(ch)
                            self.levelUpdate.emit(ch, vel)
                        else:
                            self.noteOff.emit(ch)
                    elif msg.type == 'note_off':
                        ch = int(getattr(msg, 'channel', 0)) + 1
                        self.noteOff.emit(ch)
                
                if self.port and not self.should_stop:
                    try:
                        self.port.send(msg)
                    except Exception as e:
                        logger.debug(f"Send error: {e}")
            
            if not self.should_stop:
                self.statusChanged.emit("✓ Finished")
                self.requestNext.emit()
        
        except Exception as e:
            logger.error(f"Playback: {e}")
            self.statusChanged.emit(f"❌ {e}")
        
        finally:
            self.is_running = False
            self.finished.emit()

# ============================================================================
# MIDI ENGINE
# ============================================================================

class MidiEngine(QtCore.QObject):
    """MIDI engine."""
    
    statusChanged = QtCore.Signal(str)
    devicesChanged = QtCore.Signal(list)
    bpmChanged = QtCore.Signal(float)
    lyricChanged = QtCore.Signal(str)
    noteOn = QtCore.Signal(int)
    noteOff = QtCore.Signal(int)
    levelUpdate = QtCore.Signal(int, int)
    padPlayed = QtCore.Signal(int)  # Signal when pad finishes
    
    def __init__(self):
        super().__init__()
        self.port = None
        self.tempo = 1.0
        
        self.transport_thread = None
        self.transport_worker = None
        self.transport_path = None
        
        self.pad_threads: Dict[int, QtCore.QThread] = {}
        self.pad_workers: Dict[int, PlaybackWorker] = {}
        
        self.volumes = {ch: 100 for ch in MIDI_CHANNELS}
        self.muted_channels = set()
        self.solo_channel = None
    
    def get_devices(self) -> List[str]:
        """Get MIDI output devices."""
        try:
            return list(mido.get_output_names())
        except Exception as e:
            logger.warning(f"Devices: {e}")
            return []
    
    def refresh_devices(self):
        devices = self.get_devices()
        self.devicesChanged.emit(devices)
    
    def set_output(self, name: str):
        """Set MIDI output."""
        if self.port:
            try:
                self.port.close()
            except Exception:
                pass
        
        if name:
            try:
                self.port = mido.open_output(name)
                logger.info(f"MIDI output: {name}")
            except Exception as e:
                logger.error(f"Failed to open {name}: {e}")
                self.port = None
        else:
            self.port = None
        
        self.statusChanged.emit(f"Output: {name or '(none)'}")
    
    def send_volume(self, channel: int, value: int):
        """Send CC7 (volume)."""
        if not self.port:
            return
        
        ch = max(0, min(15, channel - 1))
        val = max(0, min(127, int(value)))
        
        try:
            msg = mido.Message("control_change", channel=ch, control=7, value=val)
            self.port.send(msg)
        except Exception as e:
            logger.debug(f"Volume: {e}")
    
    def set_tempo(self, factor: float):
        self.tempo = max(0.25, min(2.0, factor))
        if self.transport_worker:
            self.transport_worker.set_tempo(self.tempo)
        for worker in self.pad_workers.values():
            try:
                worker.set_tempo(self.tempo)
            except Exception:
                pass
    
    def play_file(self, path: Path, on_next=None, force: bool = False):
        """Play MIDI file (transport). force=True ignores if already playing."""
        # Check if already playing this file (prevent double-play)
        if not force and self.transport_path == path and self.is_transport_playing():
            logger.info(f"Already playing {path.name}, skipping")
            return
        
        self.stop_transport()
        
        if not path.exists():
            self.statusChanged.emit("❌ File not found")
            return
        
        try:
            self.transport_thread = QtCore.QThread()
            self.transport_worker = PlaybackWorker(path, self.tempo)
            self.transport_worker.moveToThread(self.transport_thread)
            
            self.transport_worker.statusChanged.connect(self.statusChanged)
            self.transport_worker.bpmChanged.connect(self.bpmChanged)
            self.transport_worker.lyricChanged.connect(self.lyricChanged)
            self.transport_worker.noteOn.connect(self.noteOn)
            self.transport_worker.noteOff.connect(self.noteOff)
            self.transport_worker.levelUpdate.connect(self.levelUpdate)
            self.transport_worker.finished.connect(self.transport_thread.quit)
            
            if on_next:
                self.transport_worker.requestNext.connect(on_next)
            
            self.transport_worker.set_port(self.port)
            self.transport_path = path
            
            self.transport_thread.started.connect(self.transport_worker.run)
            self.transport_thread.start()
        
        except Exception as e:
            logger.error(f"Play: {e}")
            self.statusChanged.emit(f"❌ {e}")
    
    def play_pad(self, pad_index: int, path: Path):
        """Play MIDI file on pad - STOPS main transport."""
        pad_index = int(pad_index)
        
        # STOP MAIN TRANSPORT FIRST
        self.stop_transport()
        
        self.stop_pad(pad_index)
        
        if not path.exists():
            self.statusChanged.emit("❌ Pad file not found")
            return
        
        try:
            thread = QtCore.QThread()
            worker = PlaybackWorker(path, self.tempo)
            worker.moveToThread(thread)
            
            worker.statusChanged.connect(self.statusChanged)
            worker.bpmChanged.connect(self.bpmChanged)
            worker.lyricChanged.connect(self.lyricChanged)
            worker.noteOn.connect(self.noteOn)
            worker.noteOff.connect(self.noteOff)
            worker.levelUpdate.connect(self.levelUpdate)
            worker.finished.connect(thread.quit)
            
            def cleanup():
                self.pad_workers.pop(pad_index, None)
                self.pad_threads.pop(pad_index, None)
                self.padPlayed.emit(pad_index)  # Signal that pad finished
            
            worker.finished.connect(cleanup)
            worker.set_port(self.port)
            
            self.pad_threads[pad_index] = thread
            self.pad_workers[pad_index] = worker
            
            thread.started.connect(worker.run)
            thread.start()
        
        except Exception as e:
            logger.error(f"Play pad: {e}")
            self.statusChanged.emit(f"❌ {e}")
    
    def pause_transport(self):
        if self.transport_worker:
            self.transport_worker.pause()
    
    def resume_transport(self):
        if self.transport_worker:
            self.transport_worker.resume()
    
    def stop_transport(self):
        """Stop transport playback."""
        if self.transport_worker:
            try:
                self.transport_worker.stop()
            except Exception:
                pass
        
        if self.transport_thread and self.transport_thread.isRunning():
            self.transport_thread.quit()
            if not self.transport_thread.wait(1500):
                logger.warning("Transport thread timeout")
                self.transport_thread.terminate()
                self.transport_thread.wait(500)
        
        if self.port:
            try:
                for ch in range(16):
                    self.port.send(mido.Message("control_change", channel=ch, control=123, value=0))
                    self.port.send(mido.Message("control_change", channel=ch, control=120, value=0))
            except Exception:
                pass
        
        self.transport_worker = None
        self.transport_thread = None
        self.transport_path = None
    
    def stop_pad(self, pad_index: int):
        """Stop pad playback."""
        pad_index = int(pad_index)
        worker = self.pad_workers.get(pad_index)
        thread = self.pad_threads.get(pad_index)
        
        if worker:
            try:
                worker.stop()
            except Exception:
                pass
        
        if thread and thread.isRunning():
            thread.quit()
            if not thread.wait(1500):
                logger.warning(f"Pad {pad_index} thread timeout")
                thread.terminate()
                thread.wait(500)
        
        if self.port:
            try:
                for ch in range(16):
                    self.port.send(mido.Message("control_change", channel=ch, control=123, value=0))
                    self.port.send(mido.Message("control_change", channel=ch, control=120, value=0))
            except Exception:
                pass
        
        self.pad_workers.pop(pad_index, None)
        self.pad_threads.pop(pad_index, None)
    
    def stop_all_pads(self):
        """Stop all pads."""
        for pad_index in list(self.pad_workers.keys()):
            self.stop_pad(pad_index)
    
    def is_transport_playing(self) -> bool:
        return bool(self.transport_worker and self.transport_worker.is_running)
    
    def is_pad_playing(self, pad_index: int) -> bool:
        worker = self.pad_workers.get(int(pad_index))
        return bool(worker and worker.is_running)
    
    def get_transport_path(self) -> Optional[Path]:
        """Get current transport playing file."""
        return self.transport_path
    
    def close(self):
        """Cleanup all."""
        self.stop_transport()
        self.stop_all_pads()
        
        if self.port:
            try:
                self.port.close()
            except Exception:
                pass

# ============================================================================
# PAD BUTTON
# ============================================================================

class PadButton(QtWidgets.QPushButton):
    """Pad button - grøn når der er en fil."""
    
    triggered = QtCore.Signal(int)
    
    def __init__(self, index: int):
        super().__init__()
        self.index = index
        self.midi_file = None
        self.is_playing = False
        self.has_been_played = False  # Track if ever played
        
        self.setText(f"Pad {index + 1}")
        self.setMinimumHeight(70)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        self.clicked.connect(self._on_click)
        self.update_display()
    
    def set_file(self, path: Optional[Path]):
        self.midi_file = path
        self.has_been_played = False  # Reset when loading new file
        self.update_display()
    
    def set_playing(self, playing: bool):
        """Update visual when playing status changes."""
        self.is_playing = playing
        if playing:
            self.has_been_played = True
        self.update_display()
    
    def update_display(self):
        """Update button appearance based on state."""
        if self.midi_file:
            if self.is_playing:
                # Playing: cyan border, grøn bg
                self.setStyleSheet("""
                    background: #00d26a; color: #000; font-weight: bold; 
                    font-size: 12px; border: 3px solid #00ffff; padding: 10px;
                """)
                self.setToolTip(f"Playing: {self.midi_file.name}\n(Click to stop)")
            elif self.has_been_played:
                # Been played: grøn + checkmark
                check = "✓ "
                self.setStyleSheet("""
                    background: #00d26a; color: #000; font-weight: bold; 
                    font-size: 12px; padding: 10px;
                """)
                self.setText(f"{check}Pad {self.index + 1}")
                self.setToolTip(f"Played: {self.midi_file.name}\n(Click to play again)")
            else:
                # Loaded but not playing: grøn
                self.setStyleSheet("""
                    background: #00d26a; color: #000; font-weight: bold; 
                    font-size: 12px; padding: 10px;
                """)
                self.setText(f"Pad {self.index + 1}")
                self.setToolTip(f"Loaded: {self.midi_file.name}\n(Click to play)")
        else:
            # No file
            self.setStyleSheet("padding: 10px;")
            self.setText(f"Pad {self.index + 1}")
            self.setToolTip("Right-click to load")
    
    def _show_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        a_load = menu.addAction("Load MIDI...")
        a_clear = menu.addAction("Clear")
        action = menu.exec(self.mapToGlobal(pos))
        
        if action == a_load:
            fn, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, f"Load Pad {self.index + 1}", "", "MIDI (*.mid *.midi)"
            )
            if fn:
                self.set_file(Path(fn))
        elif action == a_clear:
            self.set_file(None)
    
    def _on_click(self):
        if main_window and self.midi_file:
            main_window.play_pad(self.index)

# ============================================================================
# CHANNEL STRIP
# ============================================================================

class ChannelStrip(QtWidgets.QFrame):
    """Mixer channel with node indicator."""
    
    volumeChanged = QtCore.Signal(int, int)
    muteToggled = QtCore.Signal(int, bool)
    soloClicked = QtCore.Signal(int)
    
    def __init__(self, ch: int):
        super().__init__()
        self.ch = ch
        self.setFixedWidth(80)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(6)
        
        label = QtWidgets.QLabel(f"CH {ch}")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 11px; font-weight: bold; color: #e8e8e8; height: 26px; min-height: 26px; background: #1a1a1a; border-radius: 3px; padding: 4px;")
        layout.addWidget(label, 0)
        
        self.indicator = QtWidgets.QLabel("●")
        self.indicator.setAlignment(QtCore.Qt.AlignCenter)
        self.indicator.setStyleSheet("color: #333; font-size: 14px; height: 20px; min-height: 20px;")
        layout.addWidget(self.indicator, 0)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.slider.setRange(0, 127)
        self.slider.setValue(100)
        self.slider.setMinimumHeight(100)
        self.slider.valueChanged.connect(lambda v: self.volumeChanged.emit(self.ch, v))
        layout.addWidget(self.slider, 1)
        
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.setSpacing(3)
        btn_layout.setContentsMargins(0, 6, 0, 0)
        
        self.solo_btn = QtWidgets.QPushButton("S")
        self.solo_btn.setCheckable(True)
        self.solo_btn.setMaximumHeight(22)
        self.solo_btn.setMinimumHeight(22)
        self.solo_btn.setStyleSheet("""
            QPushButton {
                font-size: 9px; font-weight: bold; padding: 0px;
                background: #555; color: #fff; border: 1px solid #666;
                border-radius: 3px;
            }
            QPushButton:checked {
                background: #00d26a; color: #000; border: 1px solid #00ff00;
            }
        """)
        self.solo_btn.toggled.connect(self._on_solo_toggled)
        btn_layout.addWidget(self.solo_btn)
        
        self.mute_btn = QtWidgets.QPushButton("M")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setMaximumHeight(22)
        self.mute_btn.setMinimumHeight(22)
        self.mute_btn.setStyleSheet("""
            QPushButton {
                font-size: 9px; font-weight: bold; padding: 0px;
                background: #555; color: #fff; border: 1px solid #666;
                border-radius: 3px;
            }
            QPushButton:checked {
                background: #FF4444; color: #fff; border: 1px solid #FF6666;
            }
        """)
        self.mute_btn.toggled.connect(self._on_mute_toggled)
        btn_layout.addWidget(self.mute_btn)
        
        layout.addLayout(btn_layout, 0)
        self.setLayout(layout)
    
    def _on_solo_toggled(self, checked: bool):
        self.soloClicked.emit(self.ch)
    
    def _on_mute_toggled(self, checked: bool):
        self.muteToggled.emit(self.ch, checked)
    
    def get_volume(self) -> int:
        return self.slider.value()
    
    def set_volume(self, v: int):
        self.slider.blockSignals(True)
        self.slider.setValue(v)
        self.slider.blockSignals(False)
    
    def is_muted(self) -> bool:
        return self.mute_btn.isChecked()
    
    def is_soloed(self) -> bool:
        return self.solo_btn.isChecked()
    
    def set_note_active(self, active: bool):
        if active:
            self.indicator.setStyleSheet("color: #00d26a; font-size: 14px; height: 20px; min-height: 20px;")
        else:
            self.indicator.setStyleSheet("color: #333; font-size: 14px; height: 20px; min-height: 20px;")
    
    def reset_note(self):
        QtCore.QTimer.singleShot(300, lambda: self.set_note_active(False))

# ============================================================================
# VU METER DISPLAY
# ============================================================================

class VuMeterDisplay(QtWidgets.QWidget):
    """VU meter display - Vertical bars like real mixer."""
    
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        title = QtWidgets.QLabel("🎚️ VU Meters (Real-time)")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 10px; font-weight: bold; height: 20px;")
        layout.addWidget(title)
        
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(4, 4, 4, 4)
        self.level_bars = {}
        
        for ch in range(1, 17):
            container = QtWidgets.QWidget()
            container_layout = QtWidgets.QVBoxLayout()
            container_layout.setContentsMargins(3, 3, 3, 3)
            container_layout.setSpacing(3)
            
            label = QtWidgets.QLabel(f"CH {ch}")
            label.setStyleSheet("font-size: 9px; font-weight: bold; text-align: center;")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setMaximumHeight(18)
            label.setMinimumHeight(18)
            container_layout.addWidget(label)
            
            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 127)
            bar.setValue(0)
            bar.setOrientation(QtCore.Qt.Vertical)
            bar.setMinimumHeight(80)
            bar.setMaximumWidth(24)
            bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #333;
                    border-radius: 2px;
                    background: #1a1a1a;
                }
                QProgressBar::chunk {
                    background: #00d26a;
                    border-radius: 1px;
                }
            """)
            container_layout.addWidget(bar, 1, QtCore.Qt.AlignHCenter)
            
            container.setLayout(container_layout)
            
            r, c = divmod(ch - 1, 8)
            grid.addWidget(container, r, c)
            
            self.level_bars[ch] = bar
        
        layout.addLayout(grid)
        self.setLayout(layout)
        self.setStyleSheet("background: #0a0a0a; border: 1px solid #333; border-radius: 4px;")
    
    def update_level(self, channel: int, level: int):
        """Update channel level and color."""
        if channel in self.level_bars:
            bar = self.level_bars[channel]
            bar.setValue(level)
            
            if level < 42:
                color = "#00d26a"
            elif level < 85:
                color = "#FFD700"
            else:
                color = "#FF4444"
            
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #333;
                    border-radius: 2px;
                    background: #1a1a1a;
                }}
                QProgressBar::chunk {{
                    background: {color};
                    border-radius: 1px;
                }}
            """)

# ============================================================================
# LYRICS DISPLAY
# ============================================================================

class LyricsDisplay(QtWidgets.QWidget):
    """Single line lyrics display - Font 36px."""
    
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        
        self.label = QtWidgets.QLabel("")
        self.label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            font-family: Arial;
            font-size: 36px;
            color: #ffffff;
            font-weight: bold;
            min-height: 80px;
        """)
        layout.addWidget(self.label)
        
        self.setLayout(layout)
        self.setStyleSheet("background: #101214; border-radius: 6px; padding: 8px;")
    
    def set_lyrics(self, text: str):
        """Set lyrics text."""
        self.label.setText(str(text).strip())

# ============================================================================
# MAIN WINDOW
# ============================================================================

class MainWindow(QtWidgets.QMainWindow):
    """Main window."""
    
    def __init__(self):
        super().__init__()
        global main_window
        main_window = self
        
        self.setWindowTitle(APP_TITLE)
        self.resize(1400, 900)
        
        self.settings = QtCore.QSettings("midi-live-player", "midi_live_player_pro")
        self.theme = str(self.settings.value("theme", "dark"))
        
        self.engine = MidiEngine()
        self.engine.statusChanged.connect(self.on_status)
        self.engine.bpmChanged.connect(self.on_bpm)
        self.engine.lyricChanged.connect(self.on_lyric)
        self.engine.noteOn.connect(self.on_note_on)
        self.engine.noteOff.connect(self.on_note_off)
        self.engine.levelUpdate.connect(self.on_level_update)
        self.engine.padPlayed.connect(self.on_pad_played)
        
        self.playing_index = -1
        self.pads: List[PadButton] = []
        self.channels: Dict[int, ChannelStrip] = {}
        
        # Timer for updating pad states
        self.pad_update_timer = QtCore.QTimer()
        self.pad_update_timer.timeout.connect(self.update_pad_states)
        self.pad_update_timer.start(200)
        
        self._init_ui()
        self._setup_menu()
        self.engine.refresh_devices()
        
        app = QtWidgets.QApplication.instance()
        if app and self.theme in THEMES:
            app.setStyleSheet(THEMES[self.theme])
        
        self.on_status("✓ Ready")
    
    def update_pad_states(self):
        """Update pad visual states based on playback."""
        for idx, pad in enumerate(self.pads):
            is_playing = self.engine.is_pad_playing(idx)
            pad.set_playing(is_playing)
    
    def on_pad_played(self, pad_index: int):
        """Called when pad finishes playing."""
        pass  # Just for tracking
    
    def _init_ui(self):
        """Initialize UI."""
        self.playlist = QtWidgets.QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_selected)
        
        self.status_label = QtWidgets.QLabel("✓ Ready")
        self.status_label.setStyleSheet("font-size: 10px;")
        
        self.bpm_label = QtWidgets.QLabel("BPM: 120.0")
        self.bpm_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        
        pads_layout = QtWidgets.QGridLayout()
        pads_layout.setSpacing(6)
        pads_layout.setContentsMargins(8, 18, 8, 8)  # top=18 for extra space under pads title
        
        for i in range(12):
            pad = PadButton(i)
            self.pads.append(pad)
            r, c = divmod(i, 6)
            pads_layout.addWidget(pad, r, c)
        
        pads_group = QtWidgets.QGroupBox("🎹 Pads (12) - Right-click: Load, Left-click: Play/Stop")
        pads_group.setLayout(pads_layout)
        pads_group.setMaximumHeight(170)
        pads_group.setStyleSheet("""
            QGroupBox::title {
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
        
        self.play_btn = QtWidgets.QPushButton("▶ Play")
        self.pause_btn = QtWidgets.QPushButton("⏸ Pause")
        self.stop_btn = QtWidgets.QPushButton("⏹ Stop")
        self.prev_btn = QtWidgets.QPushButton("⏮ Prev")
        self.next_btn = QtWidgets.QPushButton("⏭ Next")
        
        self.play_btn.clicked.connect(self.play_selected)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.stop_btn.clicked.connect(self.stop)
        self.prev_btn.clicked.connect(self.prev)
        self.next_btn.clicked.connect(self.next)
        
        self.tempo = QtWidgets.QDoubleSpinBox()
        self.tempo.setRange(0.25, 2.0)
        self.tempo.setSingleStep(0.1)
        self.tempo.setValue(1.0)
        self.tempo.setMaximumWidth(100)
        self.tempo.setMinimumWidth(80)
        self.tempo.setStyleSheet("font-size: 12px; padding: 4px;")
        self.tempo.valueChanged.connect(lambda v: self.engine.set_tempo(float(v)))
        
        trans_layout = QtWidgets.QHBoxLayout()
        trans_layout.addWidget(self.prev_btn)
        trans_layout.addWidget(self.play_btn)
        trans_layout.addWidget(self.pause_btn)
        trans_layout.addWidget(self.stop_btn)
        trans_layout.addWidget(self.next_btn)
        trans_layout.addSpacing(20)
        trans_layout.addWidget(QtWidgets.QLabel("Tempo:"))
        trans_layout.addWidget(self.tempo)
        trans_layout.addWidget(QtWidgets.QLabel("BPM:"))
        trans_layout.addWidget(self.bpm_label)
        trans_layout.addStretch()
        
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)
        
        left_layout.addLayout(trans_layout)
        left_layout.addWidget(QtWidgets.QLabel("📋 Playlist:"), 0)
        left_layout.addWidget(self.playlist, 1)
        left_layout.addWidget(pads_group, 0)
        left_layout.addWidget(QtWidgets.QLabel("Status:"), 0)
        left_layout.addWidget(self.status_label, 0)
        
        self.version_label = QtWidgets.QLabel("v22")
        self.version_label.setStyleSheet("color: #888; font-size: 10px; margin-top: 4px;")
        left_layout.addWidget(self.version_label, 0, QtCore.Qt.AlignLeft)
        
        left = QtWidgets.QWidget()
        left.setLayout(left_layout)
        
        self.lyrics_display = LyricsDisplay()
        self.vu_display = VuMeterDisplay()
        
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(10)
        right_layout.addWidget(QtWidgets.QLabel("🎤 Lyrics:"), 0)
        right_layout.addWidget(self.lyrics_display, 0)
        right_layout.addWidget(QtWidgets.QLabel("🎚️ VU Meters:"), 0)
        right_layout.addWidget(self.vu_display, 1)
        
        right = QtWidgets.QWidget()
        right.setLayout(right_layout)
        
        top_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        top_splitter.addWidget(left)
        top_splitter.addWidget(right)
        top_splitter.setStretchFactor(0, 35)
        top_splitter.setStretchFactor(1, 65)
        top_splitter.setCollapsible(0, False)
        top_splitter.setCollapsible(1, False)
        
        mixer_layout = QtWidgets.QHBoxLayout()
        mixer_layout.setContentsMargins(6, 6, 6, 6)
        mixer_layout.setSpacing(2)
        
        mixer_layout.addStretch(1)
        
        for ch in range(1, 17):
            strip = ChannelStrip(ch)
            strip.volumeChanged.connect(self.on_volume_changed)
            strip.muteToggled.connect(self.on_mute_toggled)
            strip.soloClicked.connect(self.on_solo_clicked)
            self.channels[ch] = strip
            mixer_layout.addWidget(strip, 0)
        
        master = ChannelStrip(0)
        self.master_slider = master.slider
        self.master_mute = master.mute_btn
        self.master_slider.setValue(127)
        self.master_slider.valueChanged.connect(self.on_master_volume)
        self.master_mute.toggled.connect(self.on_master_mute)
        mixer_layout.addWidget(master, 0)
        
        mixer_layout.addStretch(1)
        
        mixer_group = QtWidgets.QGroupBox("🎛️ Mixer (16 Channels + Master)")
        mixer_group.setLayout(mixer_layout)
        
        mixer = QtWidgets.QWidget()
        mixer_inner = QtWidgets.QVBoxLayout()
        mixer_inner.setContentsMargins(4, 4, 4, 4)
        mixer_inner.setSpacing(4)
        mixer_inner.addWidget(mixer_group)
        mixer.setLayout(mixer_inner)
        mixer.setMaximumHeight(300)
        
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(mixer)
        main_splitter.setStretchFactor(0, 11)
        main_splitter.setStretchFactor(1, 9)
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        
        main_splitter.setHandleWidth(8)
        main_splitter.setStyleSheet("QSplitter::handle { background: #444; margin: 0px; }")
        
        self.setCentralWidget(main_splitter)
    
    def _setup_menu(self):
        """Setup menu."""
        mb = self.menuBar()
        
        file_menu = mb.addMenu("📁 File")
        
        a_open = QtGui.QAction("Open MIDI...", self)
        a_open.setShortcut("Ctrl+O")
        a_open.triggered.connect(self.add_file)
        file_menu.addAction(a_open)
        
        a_folder = QtGui.QAction("Add Folder...", self)
        a_folder.triggered.connect(self.add_folder)
        file_menu.addAction(a_folder)
        
        file_menu.addSeparator()
        
        a_quit = QtGui.QAction("Exit", self)
        a_quit.setShortcut("Ctrl+Q")
        a_quit.triggered.connect(self.close)
        file_menu.addAction(a_quit)
        
        session_menu = mb.addMenu("💾 Session")
        
        a_save = QtGui.QAction("Save...", self)
        a_save.setShortcut("Ctrl+S")
        a_save.triggered.connect(self.save_session)
        session_menu.addAction(a_save)
        
        a_load = QtGui.QAction("Load...", self)
        a_load.setShortcut("Ctrl+L")
        a_load.triggered.connect(self.load_session)
        session_menu.addAction(a_load)
        
        edit_menu = mb.addMenu("✏️ Edit")
        
        a_pref = QtGui.QAction("Preferences...", self)
        a_pref.setShortcut("Ctrl+,")
        a_pref.triggered.connect(self.preferences)
        edit_menu.addAction(a_pref)
        
        a_refresh = QtGui.QAction("Refresh MIDI", self)
        a_refresh.setShortcut("F5")
        a_refresh.triggered.connect(self.engine.refresh_devices)
        edit_menu.addAction(a_refresh)
        
        view_menu = mb.addMenu("👁️ View")
        
        a_theme = QtGui.QAction("Change Theme...", self)
        a_theme.triggered.connect(self.change_theme)
        view_menu.addAction(a_theme)
    
    def on_status(self, text: str):
        self.status_label.setText(str(text))
    
    def on_bpm(self, bpm: float):
        self.bpm_label.setText(f"{bpm:.1f}")
    
    def on_lyric(self, text: str):
        self.lyrics_display.set_lyrics(str(text))
    
    def on_note_on(self, channel: int):
        if channel in self.channels:
            self.channels[channel].set_note_active(True)
    
    def on_note_off(self, channel: int):
        if channel in self.channels:
            self.channels[channel].reset_note()
    
    def on_level_update(self, channel: int, level: int):
        self.vu_display.update_level(channel, level)
    
    def on_volume_changed(self, ch: int, val: int):
        master = self.master_slider.value()
        final = (val * master) // 127
        self.engine.send_volume(ch, final)
    
    def on_master_volume(self, val: int):
        for ch in range(1, 17):
            ch_vol = self.channels[ch].get_volume()
            final = (ch_vol * val) // 127
            self.engine.send_volume(ch, final)
    
    def on_mute_toggled(self, ch: int, muted: bool):
        if muted:
            self.engine.send_volume(ch, 0)
        else:
            vol = self.channels[ch].get_volume()
            master = self.master_slider.value()
            final = (vol * master) // 127
            self.engine.send_volume(ch, final)
    
    def on_master_mute(self, muted: bool):
        if muted:
            for ch in range(1, 17):
                self.engine.send_volume(ch, 0)
        else:
            self.on_master_volume(self.master_slider.value())
    
    def on_solo_clicked(self, ch: int):
        is_soloed = self.channels[ch].is_soloed()
        
        if is_soloed:
            for c in range(1, 17):
                if c != ch:
                    vol = 0
                else:
                    vol_val = self.channels[c].get_volume()
                    master = self.master_slider.value()
                    vol = (vol_val * master) // 127
                self.engine.send_volume(c, vol)
        else:
            for c in range(1, 17):
                if not self.channels[c].is_muted():
                    vol_val = self.channels[c].get_volume()
                    master = self.master_slider.value()
                    vol = (vol_val * master) // 127
                else:
                    vol = 0
                self.engine.send_volume(c, vol)
    
    def add_file(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open MIDI", "", "MIDI (*.mid *.midi)"
        )
        if fn:
            item = QtWidgets.QListWidgetItem(Path(fn).name)
            item.setData(QtCore.Qt.UserRole, fn)
            self.playlist.addItem(item)
    
    def add_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self)
        if folder:
            p = Path(folder)
            for f in sorted(list(p.glob("*.mid")) + list(p.glob("*.midi"))):
                item = QtWidgets.QListWidgetItem(f.name)
                item.setData(QtCore.Qt.UserRole, str(f))
                self.playlist.addItem(item)
    
    def play_selected(self):
        item = self.playlist.currentItem()
        if not item:
            self.on_status("❌ Select file")
            return
        
        path = item.data(QtCore.Qt.UserRole)
        if path:
            self.playing_index = self.playlist.row(item)
            
            for i in range(self.playlist.count()):
                self.playlist.item(i).setBackground(QtGui.QColor("transparent"))
            item.setBackground(QtGui.QColor("#00d26a"))
            
            self.engine.play_file(Path(path), self.auto_next, force=True)
            self.pause_btn.setText("⏸ Pause")
    
    def play_pad(self, idx: int):
        pad = self.pads[idx]
        if pad.midi_file:
            if self.engine.is_pad_playing(idx):
                self.engine.stop_pad(idx)
                self.on_status(f"Pad {idx + 1} stopped")
            else:
                # STOPS MAIN TRANSPORT
                self.engine.play_pad(idx, pad.midi_file)
                self.on_status(f"Pad {idx + 1} playing")
    
    def auto_next(self):
        QtCore.QTimer.singleShot(0, self.next)
    
    def toggle_pause(self):
        if not self.engine.is_transport_playing():
            self.play_selected()
            return
        
        if self.pause_btn.text() == "⏸ Pause":
            self.engine.pause_transport()
            self.pause_btn.setText("▶ Resume")
        else:
            self.engine.resume_transport()
            self.pause_btn.setText("⏸ Pause")
    
    def stop(self):
        self.engine.stop_transport()
        self.pause_btn.setText("⏸ Pause")
        self.on_status("⏹ Stopped")
        
        for i in range(self.playlist.count()):
            self.playlist.item(i).setBackground(QtGui.QColor("transparent"))
    
    def prev(self):
        if self.playlist.count():
            row = max(0, self.playlist.currentRow() - 1)
            self.playlist.setCurrentRow(row)
            self.play_selected()
    
    def next(self):
        if self.playlist.count():
            row = min(self.playlist.count() - 1, self.playlist.currentRow() + 1)
            self.playlist.setCurrentRow(row)
            self.play_selected()
    
    def save_session(self):
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Session", "", "JSON (*.json)"
        )
        if fn:
            data = {
                "playlist": [self.playlist.item(i).data(QtCore.Qt.UserRole) for i in range(self.playlist.count())],
                "pads": [str(p.midi_file) if p.midi_file else "" for p in self.pads],
                "tempo": self.tempo.value(),
            }
            Path(fn).write_text(json.dumps(data, indent=2))
            self.on_status("✓ Saved")
    
    def load_session(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Session", "", "JSON (*.json)"
        )
        if fn:
            try:
                data = json.loads(Path(fn).read_text())
                
                self.playlist.clear()
                for p in data.get("playlist", []):
                    item = QtWidgets.QListWidgetItem(Path(p).name)
                    item.setData(QtCore.Qt.UserRole, p)
                    self.playlist.addItem(item)
                
                for i, p in enumerate(data.get("pads", [])):
                    if i < len(self.pads) and p:
                        self.pads[i].set_file(Path(p))
                
                self.tempo.setValue(data.get("tempo", 1.0))
                self.on_status("✓ Loaded")
            except Exception as e:
                self.on_status(f"❌ {e}")
    
    def preferences(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Preferences")
        dlg.resize(300, 120)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("MIDI Output Device:"))
        
        combo = QtWidgets.QComboBox()
        combo.addItem("(None)")
        
        try:
            for dev in mido.get_output_names():
                combo.addItem(dev)
        except Exception:
            pass
        
        def on_change(text):
            self.engine.set_output(text)
            self.settings.setValue("midi_output", text)
        
        combo.currentTextChanged.connect(on_change)
        layout.addWidget(combo)
        
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)
        
        dlg.setLayout(layout)
        dlg.exec()
    
    def change_theme(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Select Theme")
        dlg.resize(250, 150)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Choose theme:"))
        
        combo = QtWidgets.QComboBox()
        for t in THEMES.keys():
            combo.addItem(t)
        
        idx = combo.findText(self.theme)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        
        layout.addWidget(combo)
        
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        
        dlg.setLayout(layout)
        
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.theme = combo.currentText()
            self.settings.setValue("theme", self.theme)
            
            app = QtWidgets.QApplication.instance()
            if app:
                app.setStyleSheet(THEMES[self.theme])
    
    def closeEvent(self, event: QtGui.QCloseEvent):
        try:
            self.pad_update_timer.stop()
            self.engine.close()
        except Exception:
            pass
        super().closeEvent(event)

# ============================================================================
# MAIN
# ============================================================================

def main() -> int:
    QtCore.QCoreApplication.setOrganizationName("midi-live-player")
    QtCore.QCoreApplication.setApplicationName("midi_live_player_pro")
    
    app = QtWidgets.QApplication(sys.argv)
    
    try:
        w = MainWindow()
        w.show()
        return app.exec()
    except Exception as e:
        logger.critical(f"FATAL: {e}\n{traceback.format_exc()}")
        print(f"\n❌ ERROR: {e}")
        print(f"\nMake sure you have installed:\n  pip install mido python-rtmidi PySide6")
        return 1

if __name__ == "__main__":
    sys.exit(main())