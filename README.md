# Projekt ChirurgAR - Moduł Voice Control

Ten moduł umożliwia sterowanie aplikacją 3D Slicer za pomocą komend głosowych w języku polskim.

## Instalacja i Przygotowanie

### 1. Pobranie projektu
Sklonuj repozytorium na swój dysk lub pobierz je jako plik ZIP i rozpakuj.

### 2. Model językowy Vosk 
Program do poprawnego działania wymaga konkretnego modelu językowego umieszczonego wewnątrz folderu klienta.

* Pobierz polski model: [vosk-model-small-pl-0.22](https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip).
* Rozpakuj go tak, aby folder o nazwie **`vosk-model-small-pl-0.22`** znalazł się bezpośrednio wewnątrz folderu `voice_client`.

**Prawidłowa struktura plików:**
```text
voice_client/
  ├── vosk-model-small-pl-0.22/  <-- Oryginalny folder z modelu
  │   ├── am/
  │   ├── graph/
  │   ├── conf/
  │   └── ...
  ├── requirements.txt
  └── voice_client.py
```
## Konfiguracja 3D Slicer dla ChirurgAR

Aby moduł działał poprawnie i komunikował się z klientem głosowym, wykonaj poniższe kroki konfiguracyjne:

### 1. Dodanie ścieżki do modułu
1.  Otwórz **3D Slicer**.
2.  Przejdź do menu: **Edit** -> **Application Settings**.
3.  Z listy po lewej wybierz **Modules**.
4.  W sekcji **Additional module paths** kliknij przycisk **Add**.
5.  Wskaż folder `slicer_module` (ten, który pobrałeś z tego repozytorium).
6.  Zatwierdź przyciskiem **OK**.
7.  **Zrestartuj 3D Slicer** – jest to niezbędne, aby program załadował nowe pliki.

### 2. Sprawdzenie modułu
* Po restarcie kliknij w wyszukiwarkę modułów (ikonka lupy na górnym pasku lub skrót `Ctrl+F`).
* Wpisz **ChirurgAR**. Jeśli moduł się pojawi, oznacza to, że ścieżka została dodana prawidłowo.

## Uruchomienie systemu

System składa się z dwóch niezależnych części, które muszą działać jednocześnie:

### Krok 1: Przygotowanie Slicera (Odbiorca)
1. Uruchom **3D Slicer**.
2. Upewnij się, że moduł **ChirurgAR** jest załadowany (zgodnie z instrukcją powyżej).
3. W interfejsie modułu włącz jego nasłuchiwanie poprzez wciśnięcie przycisku: **URUCHOM NASŁUCH (Port 7777)**

### Krok 2: Uruchomienie Klienta Głosowego (Nadawca)
**WAŻNE:** Tego skryptu NIE uruchamiamy wewnątrz 3D Slicera. Uruchamiamy go w Twoim standardowym terminalu systemowym lub w VS Code:

1. Otwórz terminal w folderze `voice_client`.
2. Uruchom skrypt komendą:
   ```bash
   python voice_client.py

## Instrukcja obsługi – komendy głosowe

Aby korzystać z systemu, uruchom najpierw `voice_client.py`, a następnie wydawaj komendy głosowe w języku polskim.

System interpretuje polecenia i przekazuje je do środowiska 3D Slicer w czasie rzeczywistym.


### 1. Nawigacja i płaszczyzny

Możesz sterować konkretnymi płaszczyznami (osiowa, strzałkowa, czołowa) lub używać komend ogólnych.

### Komendy:

- **„następna / kolejna [o X]”**  
  Przesunięcie warstwy do przodu (offset +1 lub +X)

- **„poprzednia / cofnij [o X]”**  
  Przesunięcie warstwy do tyłu

- **„przybliż” / „oddal”**  
  Zmiana zoomu widoku

- **„lewo / prawo / góra / dół”**  
  Przesuwanie obrazu (pan)

- **„reset”**  
  Powrót do widoku 4-okienkowego i centrowanie sceny

- **„zostaw / zostać”**  
  Maksymalizacja wybranej płaszczyzny (tryb focus)

### 2. Zarządzanie punktami (landmarki)

System obsługuje punkty anatomiczne (Markups Fiducials) i pozwala sterować ich widocznością.
### Dane testowe i Landmarki:

W folderze `landmarki_json` znajdują się przykładowe punkty anatomiczne (pliki `.json`), które pozwalają przetestować komendy zarządzające widocznością punktów anatomicznych.  
Punkty zostały przygotowane dla danych: **Zatoki 1, Seria nr 7**.

### Jak wczytać dane do 3D Slicer?

Aby system działał na tych samych współrzędnych co w przykładach, wykonaj poniższe kroki:

1. Wczytanie obrazu (DICOM), dla którego zostały przygotowane punkty anatomiczne (**Zatoki 1, Seria nr 7**).

2. Wczytanie Landmarków

   2.1. Przeciągnij plik `.json` z folderu `landmarki_json` do okna programu. (Możesz również wczytać pliki przez wbudowany w Slicerze moduł `Add Data`).

   2.2. Slicer automatycznie rozpozna wczytany plik jako **Markups**.


3. Weryfikacja w module Markups

   3.1. Przejdź do modułu **Markups** (ikona strzałki z punktami).

   3.2. Upewnij się, że widoczne są etykiety punktów które wczytałeś:
   - Blaszka sitowa  
   - Tętnica sitowa  
   - Nerw wzrokowy  

4. Weryfikacja położenia puntków  

    Punkty anatomiczne są zlokalizowane na konkretnych głębokościach.  
    Wartości głębokości możesz wpisywać ręcznie bądź wykorzystać do tego sterowanie głosowe (po uprzednim uruchomieniu nasłuchiwania w module **ChirurgAR** i uruchomieniu skryptu `voice_client.py`), korzystając z komend do sterowania poszczególnymi płaszczyznami (następna/poprzednia).

    Poniżej przedstawiono wartości suwaków płaszczyzn, na których można zobaczyć wybrane punkty w widoku 2D.
    
    | Punkt anatomiczny | Axial (Czerwona) | Coronal (Zielona) | Sagittal (Żółta) |
    |------------------|------------------|-------------------|------------------|
    | Blaszka sitowa   | SP: -516.97 mm   | ASL: 109.35 mm    | LP: -5.11 mm     |
    | Tętnica sitowa   | SP: -515.70 mm   | ASL: 117.92 mm    | LP: 4.35 mm      |
    | Nerw wzrokowy    | SP: -518.01 mm   | ASL: 112.07 mm    | LP: -29.18 mm    |

### Testowanie głosowe
Po uruchomieniu skryptu `voice_client.py` i włączeniu nasłuchu w Slicerze, możesz przetestować system komendami:

### Komendy:

- **„pokaż [nazwa]”**  
  Wyświetla punkt o danej etykiecie (np. „pokaż guz”)

- **„ukryj [nazwa]”**  
  Ukrywa punkt o danej etykiecie (np. „ukryj guz”)

### Przykłady:

- **"Pokaż blaszka sitowa"**  
  → włącza widoczność punktu w przestrzeni 3D i 2D  

- **"Ukryj tętnica sitowa"**  
  → wyłącza znacznik, aby nie zasłaniał struktur  

- **"Czołowa następna o dziesięć"**  
  → przejście przez kolejne warstwy zatok w płaszczyźnie Coronal  


### Obsługiwane wartości:

- słownie: *jeden, pięć, dziesięć, dwadzieścia*

## Uwagi

- System działa lokalnie (UDP, port 7777)
- Wymaga uruchomionego `voice_client.py`
- Komendy są przetwarzane w czasie rzeczywistym
- Integracja z 3D Slicer
