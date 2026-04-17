import slicer
from slicer.ScriptedLoadableModule import *
import qt
import json 

class VoiceControl(ScriptedLoadableModule):
    def __init__(self, parent):
            ScriptedLoadableModule.__init__(self, parent)
            self.parent.title = "Głosowe Sterowanie Slicerem" 
            self.parent.categories = ["Chirurgia AR"]
            self.parent.dependencies = []
            self.parent.helpText = "Moduł do sterowania głosowego."
            self.parent.acknowledgementText = "Projekt ChirurgAR."

class VoiceControlWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Uruchomienie przycisków
        self.start_button = qt.QPushButton("URUCHOM NASŁUCH (Port 7777)")
        self.start_button.setFixedHeight(40)
        self.start_button.setStyleSheet("background-color: #e1e1e1;")
        self.start_button.connect('clicked(bool)', self.on_start)
        self.layout.addWidget(self.start_button)

        #Zakończenie przycisków
        self.stop_button = qt.QPushButton("ZAKOŃCZ NASŁUCH")
        self.stop_button.setFixedHeight(40)
        self.stop_button.enabled = False 
        self.stop_button.setStyleSheet("background-color: #ffcccc;") 
        self.stop_button.connect('clicked(bool)', self.on_stop)
        self.layout.addWidget(self.stop_button)
        
        # Etykieta informacyjna
        self.info_label = qt.QLabel("Status: Oczekiwanie na start...")
        self.info_label.setStyleSheet("font-size: 14px; color: gray; margin-top: 10px;")
        self.layout.addWidget(self.info_label)

        # Socket UDP
        self.socket = qt.QUdpSocket()
        self.socket.readyRead.connect(self.on_data)
        self.listening = False

    def on_start(self):
        self.socket.close()
        self.listening = True
        if self.socket.bind(7777):
            # Zmiana stanu przycisków
            self.start_button.enabled = False
            self.stop_button.enabled = True
            self.start_button.text = "NASŁUCHIWANIE AKTYWNE"
            self.info_label.text = "Status: Połączono. Port 7777 aktywny."
            slicer.util.showStatusMessage("Nasłuch UDP uruchomiony", 3000)
        else:
            self.info_label.text = "BŁĄD: Port 7777 zajęty!"

    def on_stop(self):
        self.listening = False
        try:
            self.socket.readyRead.disconnect(self.on_data)
        except:
            pass

        self.socket.close()
        
        # Przywrócenie stanu przycisków
        self.start_button.enabled = True
        self.stop_button.enabled = False
        self.start_button.text = "URUCHOM NASŁUCH (Port 7777)"
        self.info_label.text = "Status: Nasłuch został zatrzymany."
        slicer.util.showStatusMessage("Nasłuch UDP zatrzymany", 3000)

    def on_data(self):
        if not self.listening:
            return
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            try:
                # Odbieramy dane i dekodujemy JSON
                wiadomosc = datagram.data().data().decode('utf-8').strip()
                data = json.loads(wiadomosc)
                
                # Wyciągamy parametry z bezpiecznymi wartościami domyślnymi
                plane = data.get("plane", "global")
                action = data.get("action")
                value = data.get("value", 1)
                label = data.get("label") # Może być None

                # Wywołujemy logikę sterowania
                if action:
                    self.execute_command(plane, action, value, label)
                self.info_label.text = f"Akcja: {action} | Plane: {plane} | Value: {value} | Label: {label}"
            except Exception as e:
                print(f"Błąd UDP: {e}")

    def execute_command(self, plane, action, value, label):
        layoutManager = slicer.app.layoutManager()
        
        # Mapowanie nazw na kolory okien w Slicerze
        plane_map = {
            "axial": "Red",
            "coronal": "Green",
            "sagittal": "Yellow"
        }

        layout_map = {
            "axial": slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView,
            "coronal": slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView,
            "sagittal": slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView
        }

        # Decydujemy, które okna modyfikować
        if plane in plane_map:
            target_widgets = [plane_map[plane]]
        else:
            target_widgets = ["Red", "Green", "Yellow"]

        for widget_name in target_widgets:
            sliceWidget = layoutManager.sliceWidget(widget_name)
            if not sliceWidget: continue
            
            sliceLogic = sliceWidget.sliceLogic()
            sliceNode = sliceLogic.GetSliceNode()

            # OBSŁUGA LANDAMRKÓW
            if action in ["show_landmark", "hide_landmark"] and label:
                visible = (action == "show_landmark")

                voice_label = label.lower()

                nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsFiducialNode")

                for node in nodes:
                    for i in range(node.GetNumberOfControlPoints()):
                        node_label = node.GetNthControlPointLabel(i).lower()

                        if voice_label == node_label:
                            node.SetNthControlPointVisibility(i, visible)
                continue

            # PRZESUWANIE 
            if "pan_" in action:
                origin = list(sliceNode.GetXYZOrigin()) 
                shift = 3 * value
                
                if action == "pan_left": origin[0] += shift
                elif action == "pan_right": origin[0] -= shift
                elif action == "pan_up": origin[1] -= shift
                elif action == "pan_down": origin[1] += shift
                
                sliceNode.SetXYZOrigin(origin[0], origin[1], origin[2])

            # Do nawigacji pomiędzy slajdami
            elif action == "next_slice":
                sliceLogic.SetSliceOffset(sliceLogic.GetSliceOffset() + value)
            
            elif action == "prev_slice":
                sliceLogic.SetSliceOffset(sliceLogic.GetSliceOffset() - value)

            # Przybliżanie i oddalanie
            elif action == "zoom_in":
                fov = sliceNode.GetFieldOfView()
                sliceNode.SetFieldOfView(fov[0]*0.99*(1/value), fov[1]*0.99*(1/value), fov[2])

            elif action == "zoom_out":
                fov = sliceNode.GetFieldOfView()
                sliceNode.SetFieldOfView(fov[0]*1.01*value, fov[1]*1.01*value, fov[2])

            # Skupienie na jednej z płaszczyzn
            elif action == "focus_plane":
                lm = slicer.app.layoutManager()

                layout_id = layout_map.get(plane, None)

                if layout_id:
                    lm.setLayout(layout_id)
            
            elif action == "reset_view":
                sliceLogic.FitSliceToAll()
                lm = slicer.app.layoutManager()
                lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

            # Zakończenie nasłuchiwania
            elif action == "exit":
                self.on_stop()