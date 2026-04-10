<table align="center" width="100%">
  <tr>
    <td align="center" bgcolor="#1A1C23" style="padding: 40px; border-radius: 8px;">
      <h1><font color="#FFFFFF">Antigravity Hand Tracking</font></h1>
      <p><font color="#A0AEC0">Dynamic real-time hand tracking visualization built with Python and MediaPipe.</font></p>
    </td>
  </tr>
</table>

This is a Python-based real-time hand-tracking tool that focuses on smooth, aesthetic visuals. It utilizes MediaPipe and OpenCV to capture and process inputs, generating glowing connections between corresponding fingertips of both hands in real-time. The visualization's color dynamically transitions according to the physical distance between the hands, creating a captivating visual effect without the need for complex software suites like TouchDesigner.

## Example Visuals

Here is an overview of what to expect while running the project. Notice how the glowing line colors adapt interactively:

<div align="center">
  <img src="example%20images/Example%201.png" width="48%" alt="Example 1" style="border-radius: 8px;" />
  <img src="example%20images/Example%202.png" width="48%" alt="Example 2" style="border-radius: 8px;" />
  <br><br>
  <img src="example%20images/Example%203.png" width="48%" alt="Example 3" style="border-radius: 8px;" />
  <img src="example%20images/Example%204.png" width="48%" alt="Example 4" style="border-radius: 8px;" />
  <br><br>
  <img src="example%20images/Example%205.png" width="60%" alt="Example 5" style="border-radius: 8px;" />
</div>

## Features

- **Dynamic Camera Selection**: Lightweight Tkinter interface on startup that identifies and lists all available cameras.
- **Robust Tracking Performance**: Highly responsive real-time 2-hand tracking powered by MediaPipe.
- **Aesthetic Overlays**: Implementation of smooth, glowing connections between joints.
- **Distance-based Interactivity**: Live color-shifting effects mapped directly to inter-hand distance metrics.
- **Local Processing**: Utilizes the `hand_landmarker.task` model locally for optimized and offline functionality.

---

## Setup & Installation

Below are the complete steps to get a copy of this project running on your local machine using an isolated virtual environment (`.venv`).

### 1. Clone the repository
Copy the project to your local machine using git:
```bash
git clone <your-repository-url>
cd Antigravity
```

### 2. Create your Virtual Environment 
A virtual environment ensures required versions of dependencies are used without conflicting with your system's global Python environment.

**On Windows:**
```bash
python -m venv .venv
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment
Before proceeding, you must activate the isolated `.venv` space.

**On Windows:**
```bash
# In Command Prompt
.venv\Scripts\activate.bat

# In PowerShell
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
source .venv/bin/activate
```
*(You will know it worked if your terminal prompt begins with `(.venv)`).*

### 4. Install Dependencies
With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 5. Run the Application
Finally, launch the visualization file. Make sure you are in the root project folder and your virtual environment is still activated.

```bash
python main.py
```

A window will appear asking you to choose a camera. Select one, and press `q` on your keyboard at any time to exit the visualization.

---

*Ensure the `hand_landmarker.task` model file remains in the exact same directory as `main.py` for successful execution.*
