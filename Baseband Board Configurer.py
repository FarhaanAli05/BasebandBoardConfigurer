import random
import re
from itertools import combinations
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sv_ttk

# Helper function to generate random boards
def generate_random_board():
    num_modes = random.randint(1, 5)
    board = []
    for i in range(num_modes):
        mode = {'L': 0, 'N': 0, 'G': 0, 'U': 0, 'D': 0}
        techs = ['L', 'N', 'G', 'U', 'D']
        num_techs = random.randint(1, 5)
        chosen_techs = random.sample(techs, num_techs)
        for tech in chosen_techs:
            mode[tech] = random.randint(3, 6)
        board.append(mode)
    return board

# Function to format cell data as a string
def format_cells(cells):
    result = ""
    for key in cells:
        if cells[key] > 0:
            if result != "":
                result = result + " + "
            result = result + str(cells[key]) + key
    return result

# Function to find all possible solutions
def find_solutions(bs_req, boards, max_solutions=100):
    solutions = []
    max_boards = 5

    # Helper function to check if a combination of boards meets the requirements
    def check_solution(combination):
        total_cells = {'L': 0, 'N': 0, 'G': 0, 'U': 0, 'D': 0}
        for item in combination:
            board = item[0]
            mode = item[1]
            for tech in boards[board][mode]:
                total_cells[tech] = total_cells[tech] + boards[board][mode][tech]
        for tech in bs_req:
            if total_cells[tech] < bs_req[tech]:
                return False
        return True

    # Generate all possible board and mode combinations
    all_board_modes = []
    for board in boards:
        for mode in range(len(boards[board])):
            all_board_modes.append((board, mode))

    # Find all possible solutions
    for num_boards in range(1, max_boards + 1):
        for combination in combinations(all_board_modes, num_boards):
            if check_solution(combination):
                solution = []
                for item in combination:
                    board = item[0]
                    mode = item[1]
                    solution.append(f"{board}m{mode+1}")
                solution.sort()
                solution = tuple(solution)
                if solution not in solutions:
                    solutions.append(solution)
                    if len(solutions) >= max_solutions:
                        solutions.sort(key=lambda x: (len(x), x))
                        return solutions

    solutions.sort(key=lambda x: (len(x), x))
    return solutions

# Function to parse inputted string into cell data
def parse_cells(input_str):
    cells = {'L': 0, 'N': 0, 'G': 0, 'U': 0, 'D': 0}
    valid_chars = ['L', 'N', 'G', 'U', 'D']
    input_str = input_str.upper()
    matches = re.findall(r'(\d+)([A-Za-z])', input_str)
    for match in matches:
        number = int(match[0])
        letter = match[1]
        if letter not in valid_chars:
            return None
        cells[letter] = cells[letter] + number
    return cells

class BasebandBoardConfigurer:
    def __init__(self, master):
        self.master = master
        self.master.title("Baseband Board Configurer")
        self.master.geometry("600x800")

        sv_ttk.set_theme("dark")

        self.custom_boards = {}
        self.create_widgets()
        self.customize_boards_menu()

    def create_widgets(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Create title
        self.title_label = ttk.Label(self.main_frame, text="Baseband Board Configurer", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Create requirements entry
        self.req_label = ttk.Label(self.main_frame, text="Base stand tower requirements:")
        self.req_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.req_entry = ttk.Entry(self.main_frame, width=25)
        self.req_entry.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        self.req_entry.insert(0, "6L + 3N + 2D")
        self.req_entry.bind("<FocusIn>", self.req_preview_text)
        self.req_entry.bind("<FocusOut>", self.restore_req_preview_text)

        # Create board capacity entry
        self.board_label = ttk.Label(self.main_frame, text="First board's capacity:")
        self.board_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.board_entry = ttk.Entry(self.main_frame, width=25)
        self.board_entry.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        self.board_entry.insert(0, "3L + 3N or 6L + 2D")
        self.board_entry.bind("<FocusIn>", self.board_preview_text)
        self.board_entry.bind("<FocusOut>", self.restore_board_preview_text)

        # Create cost entry
        self.cost_label = ttk.Label(self.main_frame, text="First board's cost ($5 to $20):")
        self.cost_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.cost_entry = ttk.Entry(self.main_frame, width=10)
        self.cost_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.cost_entry.insert(0, "10.00")
        self.cost_entry.bind("<FocusIn>", self.cost_preview_text)
        self.cost_entry.bind("<FocusOut>", self.restore_cost_preview_text)

        # Create button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Create generate solutions button
        self.generate_button = ttk.Button(self.button_frame, text="Generate Solutions", command=self.generate_solutions, style="Accent.TButton")
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Create randomize input button
        self.randomize_button = ttk.Button(self.button_frame, text="Randomize Input", command=self.randomize_input)
        self.randomize_button.pack(side=tk.LEFT, padx=5)

        # Create dashboard text box
        self.dashboard_label = ttk.Label(self.main_frame, text="Dashboard of Boards (5 Boards Minimum):")
        self.dashboard_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.dashboard_text = scrolledtext.ScrolledText(self.main_frame, width=50, height=8, wrap=tk.WORD)
        self.dashboard_text.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Create solutions text box
        self.solutions_label = ttk.Label(self.main_frame, text="Possible Solutions:")
        self.solutions_label.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.solutions_text = scrolledtext.ScrolledText(self.main_frame, width=50, height=8, wrap=tk.WORD)
        self.solutions_text.grid(row=8, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Create top solutions text box
        self.top_solutions_label = ttk.Label(self.main_frame, text="Top 10 Cost-Effective Solutions:")
        self.top_solutions_label.grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.top_solutions_text = scrolledtext.ScrolledText(self.main_frame, width=50, height=8, wrap=tk.WORD)
        self.top_solutions_text.grid(row=10, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Configure grid weights
        self.main_frame.columnconfigure(1, weight=1)
        for i in range(6, 11, 2):
            self.main_frame.rowconfigure(i, weight=1)

        # Style the generate solutions button
        self.style = ttk.Style()
        self.style.configure("Accent.TButton", foreground="white", background="#58ccfc")

    def customize_boards_menu(self):
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)

        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Customize Boards", command=self.board_customization)

    def board_customization(self):
        self.customize_window = tk.Toplevel(self.master)
        self.customize_window.title("Customize Boards")
        self.customize_window.geometry("400x300")

        self.customize_frame = ttk.Frame(self.customize_window, padding="10")
        self.customize_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.customize_window.columnconfigure(0, weight=1)
        self.customize_window.rowconfigure(0, weight=1)

        self.board_name_label = ttk.Label(self.customize_frame, text="Board Name:")
        self.board_name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.board_name_entry = ttk.Entry(self.customize_frame, width=20)
        self.board_name_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)

        self.board_capacity_label = ttk.Label(self.customize_frame, text="Board Capacity:")
        self.board_capacity_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.board_capacity_entry = ttk.Entry(self.customize_frame, width=20)
        self.board_capacity_entry.grid(row=1, column=1, sticky="we", padx=5, pady=5)

        self.board_cost_label = ttk.Label(self.customize_frame, text="Board Cost:")
        self.board_cost_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.board_cost_entry = ttk.Entry(self.customize_frame, width=10)
        self.board_cost_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.add_board_button = ttk.Button(self.customize_frame, text="Add Board", command=self.add_board)
        self.add_board_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.custom_boards_label = ttk.Label(self.customize_frame, text="Current Custom Boards:")
        self.custom_boards_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.custom_boards_text = scrolledtext.ScrolledText(self.customize_frame, width=40, height=8, wrap=tk.WORD)
        self.custom_boards_text.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Configure grid weights
        self.customize_frame.columnconfigure(1, weight=1)
        self.customize_frame.rowconfigure(5, weight=1)

        self.update_custom_boards_display()

    def add_board(self):
        name = self.board_name_entry.get()
        capacity = self.board_capacity_entry.get()
        cost = self.board_cost_entry.get()
        
        if name and capacity and cost:
            try:
                cost = float(cost)
                if 5 <= cost <= 20:
                    modes = [parse_cells(mode.strip()) for mode in capacity.split("or")]
                    if all(mode is not None for mode in modes):
                        self.custom_boards[name] = {"capacity": modes, "cost": cost}
                        messagebox.showinfo("Success", f"Board '{name}' added successfully.")
                        self.board_name_entry.delete(0, tk.END)
                        self.board_capacity_entry.delete(0, tk.END)
                        self.board_cost_entry.delete(0, tk.END)
                        self.update_custom_boards_display()
                    else:
                        messagebox.showerror("Error", "Invalid character entered in the board capacity.")
                else:
                    messagebox.showerror("Error", "Board cost must be between $5 and $20.")
            except ValueError:
                messagebox.showerror("Error", "Invalid cost. Please enter a number.")
        else:
            messagebox.showerror("Error", "All fields are required.")

    def update_custom_boards_display(self):
        self.custom_boards_text.delete(1.0, tk.END)
        for name, details in self.custom_boards.items():
            self.custom_boards_text.insert(tk.END, f"{name}: {details['capacity']} (Cost: ${details['cost']:.2f})\n")

    def req_preview_text(self, event):
        if self.req_entry.get() == "6L + 3N + 2D":
            self.req_entry.delete(0, "end")
            self.req_entry.insert(0, '')

    def restore_req_preview_text(self, event):
        if self.req_entry.get() == '':
            self.req_entry.insert(0, "6L + 3N + 2D")

    def board_preview_text(self, event):
        if self.board_entry.get() == "3L + 3N or 6L + 2D":
            self.board_entry.delete(0, "end")
            self.board_entry.insert(0, '')

    def restore_board_preview_text(self, event):
        if self.board_entry.get() == '':
            self.board_entry.insert(0, "3L + 3N or 6L + 2D")

    def cost_preview_text(self, event):
        if self.cost_entry.get() == "10.00":
            self.cost_entry.delete(0, "end")
            self.cost_entry.insert(0, '')

    def restore_cost_preview_text(self, event):
        if self.cost_entry.get() == '':
            self.cost_entry.insert(0, "10.00")

    def generate_solutions(self):
        # Get requirements
        bs_input = self.req_entry.get()
        bs_req = parse_cells(bs_input)

        if bs_req is None:
            messagebox.showerror("Error", "Invalid character entered in the requirements.")
            return

        board_input = self.board_entry.get()
        board_modes = board_input.split("or")
        base_board = []
        for mode in board_modes:
            base_board.append(parse_cells(mode.strip()))

        try:
            base_board_cost = float(self.cost_entry.get())
            if not 5 <= base_board_cost <= 20:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid cost. Please enter a number between 5 and 20.")
            return

        num_boards = 5
        dashboard = {}
        dashboard["UBPe1p"] = base_board
        board_costs = {}
        board_costs["UBPe1p"] = base_board_cost

        for name, details in self.custom_boards.items():
            dashboard[name] = details['capacity']
            board_costs[name] = details['cost']

        for i in range(2, num_boards + 1 - len(self.custom_boards)):
            board_name = f"UBPe{i}p"
            if board_name not in dashboard:
                dashboard[board_name] = generate_random_board()
                board_costs[board_name] = round(random.uniform(5, 20), 2)

        self.dashboard_text.delete(1.0, tk.END)
        self.dashboard_text.insert(tk.END, "Dashboard of Boards:\n")
        for board_name in dashboard:
            self.dashboard_text.insert(tk.END, f"{board_name} (Cost: ${board_costs[board_name]:.2f}):\n")
            for i in range(len(dashboard[board_name])):
                mode = dashboard[board_name][i]
                self.dashboard_text.insert(tk.END, f"  Mode {i+1}: {format_cells(mode)}\n")

        solutions = find_solutions(bs_req, dashboard)

        self.solutions_text.delete(1.0, tk.END)
        self.top_solutions_text.delete(1.0, tk.END)
    
        if len(solutions) > 0:
            self.solutions_text.insert(tk.END, f"Possible solutions (capped at {len(solutions)}):\n")
            for i in range(len(solutions)):
                solution = solutions[i]
                total_cost = sum(board_costs[board.split('m')[0]] for board in solution)
                self.solutions_text.insert(tk.END, f"Solution {i+1}: {' + '.join(solution)} (Total Cost: ${total_cost:.2f})\n")

            ranked_solutions = sorted(solutions, key=lambda x: sum(board_costs[board.split('m')[0]] for board in x))

            self.top_solutions_text.insert(tk.END, "Top 10 most cost-effective solutions:\n")
            for i in range(min(10, len(ranked_solutions))):
                solution = ranked_solutions[i]
                total_cost = sum(board_costs[board.split('m')[0]] for board in solution)
                self.top_solutions_text.insert(tk.END, f"Rank {i+1}: {' + '.join(solution)} (Total Cost: ${total_cost:.2f})\n")
        else:
            self.solutions_text.insert(tk.END, "No solutions found. The available boards cannot meet the requirements.")

    def randomize_input(self):
        techs = ['L', 'N', 'G', 'U', 'D']
        
        num_techs = random.randint(2, 5)
        chosen_techs = random.sample(techs, num_techs)
        req = []
        for tech in chosen_techs:
            req.append(f"{random.randint(1, 6)}{tech}")
        req_string = ' + '.join(req)
        self.req_entry.delete(0, tk.END)
        self.req_entry.insert(0, req_string)

        num_modes = random.randint(1, 2)
        modes = []
        for _ in range(num_modes):
            num_techs = random.randint(1, 3)
            chosen_techs = random.sample(techs, num_techs)
            mode = []
            for tech in chosen_techs:
                mode.append(f"{random.randint(3, 6)}{tech}")
            modes.append(' + '.join(mode))
        board_capacity = ' or '.join(modes)
        self.board_entry.delete(0, tk.END)
        self.board_entry.insert(0, board_capacity)

        cost = round(random.uniform(5, 20), 2)
        self.cost_entry.delete(0, tk.END)
        self.cost_entry.insert(0, f"{cost:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BasebandBoardConfigurer(root)
    root.mainloop()