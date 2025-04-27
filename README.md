# Baseband Board Configurer

The Baseband Board Configurer is a Python GUI program that simulates the configuration of baseband boards for a wireless base station. It allows the user to define board capacities, assign costs, and find valid combinations of boards that meet given technology requirements.

---

## What It Does

- Lets the user enter base station requirements (e.g. `6L + 3N + 2D`)
- Accepts custom board definitions, including their modes and costs
- Randomly generates additional boards to fill out the configuration
- Searches for all possible board combinations that meet the requirements
- Displays up to 100 solutions, and highlights the 10 most cost-effective ones

Each board can support multiple modes (configurations), and each mode supports different quantities of technologies (L, N, G, U, D).

---

## How to Run

### Requirements

- Python 3.x
- `tkinter` (comes with most Python installations)
- `sv_ttk` for themed GUI (install using pip)

### Install `sv_ttk`:

```bash
pip install sv-ttk
