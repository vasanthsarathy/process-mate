"""
Chess Thought Process Analyzer
A focused application that analyzes chess games move-by-move
according to a specific thought process flowchart.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import chess
import chess.pgn
import chess.svg
import chess.engine
import io
import os
import re
import threading
from PIL import Image, ImageTk
import cairosvg


class ChessThoughtAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Thought Process Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Set theme
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        
        # Game data
        self.game = None
        self.current_node = None
        self.board = chess.Board()
        
        # Board orientation - False = white at bottom, True = black at bottom
        self.board_flipped = False
        
        # Analysis options
        self.simplify_analysis = False
        
        # Engine setup
        self.engine_path = self.find_engine_path()
        self.engine = None
        
        # Setup UI
        self.setup_ui()
        self.start_engine()
        
    def find_engine_path(self):
        """Find the chess engine on the system."""
        # Default paths to check for common engines
        possible_paths = [
            # Windows paths
            "stockfish/stockfish.exe",
            "C:/Program Files/Stockfish/stockfish.exe",
            # Mac paths
            "stockfish/stockfish-mac-x64",
            "/usr/local/bin/stockfish",
            # Linux paths
            "stockfish/stockfish-ubuntu-x64",
            "/usr/games/stockfish",
            "/usr/bin/stockfish"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # If not found, return a default path and let user configure later
        return "stockfish"
    
    def setup_ui(self):
        """Set up the main user interface."""
        # Set up keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.prev_move())
        self.root.bind('<Right>', lambda e: self.next_move())
        self.root.bind('<Home>', lambda e: self.goto_start())
        self.root.bind('<End>', lambda e: self.goto_end())
        self.root.bind('<F5>', lambda e: self.analyze_current_position())
        self.root.bind('<F2>', lambda e: self.flip_board())
        
        # Create menu
        self.setup_menu()
        
        # Main paned window (board on left, analysis on right)
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for board and move list
        self.left_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_panel, weight=4)
        
        # Right panel for thought process analysis
        self.right_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_panel, weight=6)
        
        # Setup board display
        self.board_frame = ttk.LabelFrame(self.left_panel, text="Chess Board")
        self.board_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.board_canvas = tk.Canvas(self.board_frame, width=500, height=500, bg="white")
        self.board_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Board navigation controls
        self.controls_frame = ttk.Frame(self.left_panel)
        self.controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.controls_frame, text="<<", command=self.goto_start).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.controls_frame, text="<", command=self.prev_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.controls_frame, text=">", command=self.next_move).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.controls_frame, text=">>", command=self.goto_end).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.controls_frame, text="↻ Flip Board", command=self.flip_board).pack(side=tk.LEFT, padx=10)
        
        # Game info
        self.game_info_frame = ttk.LabelFrame(self.left_panel, text="Game Information")
        self.game_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.game_info_text = tk.Text(self.game_info_frame, height=2, wrap=tk.WORD)
        self.game_info_text.pack(fill=tk.X, padx=5, pady=5)
        self.game_info_text.config(state=tk.DISABLED)
        
        # Move list (using Treeview for a nice look)
        self.move_list_frame = ttk.LabelFrame(self.left_panel, text="Move List")
        self.move_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.move_list = ttk.Treeview(self.move_list_frame, columns=("white", "black"), 
                                      show="headings", selectmode="browse")
        self.move_list.heading("white", text="White")
        self.move_list.heading("black", text="Black")
        
        self.move_list.column("white", width=100)
        self.move_list.column("black", width=100)
        
        self.move_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.move_list.bind("<<TreeviewSelect>>", self.on_move_selected)
        
        # Right panel - Thought Process Analysis
        self.analysis_frame = ttk.LabelFrame(self.right_panel, text="Thought Process Analysis")
        self.analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thought process output - rich text with some styling
        self.thought_output = scrolledtext.ScrolledText(self.analysis_frame, wrap=tk.WORD)
        self.thought_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.thought_output.tag_configure("heading", font=("TkDefaultFont", 12, "bold"))
        self.thought_output.tag_configure("subheading", font=("TkDefaultFont", 11, "bold"))
        self.thought_output.tag_configure("normal", font=("TkDefaultFont", 10))
        self.thought_output.tag_configure("highlight", font=("TkDefaultFont", 10, "bold"), foreground="blue")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Please load a PGN file.")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initial board display
        self.update_board_display()
    
    def setup_menu(self):
        """Set up the application menu."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open PGN", command=self.load_pgn)
        file_menu.add_command(label="Save Analysis", command=self.save_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Flip Board", command=self.flip_board)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Engine menu
        engine_menu = tk.Menu(menubar, tearoff=0)
        engine_menu.add_command(label="Configure Engine", command=self.configure_engine)
        menubar.add_cascade(label="Engine", menu=engine_menu)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        self.simplify_var = tk.BooleanVar()
        self.simplify_var.set(self.simplify_analysis)
        analysis_menu.add_checkbutton(label="Simplify Analysis on Threats", 
                                     variable=self.simplify_var, 
                                     command=self.toggle_simplified_analysis)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Thought Process Guide", command=self.show_thought_process)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def load_pgn(self):
        """Load a PGN file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, "r") as pgn_file:
                self.game = chess.pgn.read_game(pgn_file)
            
            if self.game:
                self.current_node = self.game
                self.board = self.game.board()
                
                # Update game info
                self.update_game_info()
                
                # Update move list
                self.update_move_list()
                
                # Update board
                self.update_board_display()
                
                # Clear analysis
                self.clear_analysis()
                
                self.status_var.set(f"Loaded game from {os.path.basename(file_path)}")
            else:
                self.status_var.set("No game found in the PGN file.")
                
        except Exception as e:
            self.status_var.set(f"Error loading PGN: {str(e)}")
    
    def update_game_info(self):
        """Update the game information display."""
        self.game_info_text.config(state=tk.NORMAL)
        self.game_info_text.delete("1.0", tk.END)
        
        white = self.game.headers.get("White", "Unknown")
        black = self.game.headers.get("Black", "Unknown")
        event = self.game.headers.get("Event", "Unknown")
        date = self.game.headers.get("Date", "Unknown")
        result = self.game.headers.get("Result", "Unknown")
        
        info = f"{white} vs {black}, {event}, {date}, {result}"
        self.game_info_text.insert(tk.END, info)
        self.game_info_text.config(state=tk.DISABLED)
    
    def update_move_list(self):
        """Update the move list display."""
        # Clear current move list
        for item in self.move_list.get_children():
            self.move_list.delete(item)
            
        # Add moves
        mainline = list(self.game.mainline())
        
        for i in range(0, len(mainline), 2):
            white_node = mainline[i] if i < len(mainline) else None
            black_node = mainline[i+1] if i+1 < len(mainline) else None
            
            white_move = white_node.san() if white_node else ""
            black_move = black_node.san() if black_node else ""
            
            move_number = i // 2 + 1
            self.move_list.insert("", tk.END, iid=str(i//2), 
                                 values=(white_move, black_move), 
                                 text=f"{move_number}.")
    
    def flip_board(self):
        """Flip the chess board orientation."""
        self.board_flipped = not self.board_flipped
        self.update_board_display()
        
    def toggle_simplified_analysis(self):
        """Toggle simplified analysis mode."""
        self.simplify_analysis = self.simplify_var.get()
        # Re-analyze if a position is loaded
        if self.current_node:
            self.analyze_current_position()
            
    def update_board_display(self):
        """Update the chess board display using Tkinter's native features."""
        if not hasattr(self, 'board_canvas'):
            return
            
        try:
            self.board_canvas.delete("all")
            
            # Board dimensions
            sq_size = 60  # Square size in pixels
            board_size = 8 * sq_size
            self.board_canvas.config(width=board_size, height=board_size)
            
            # Draw board squares
            for row in range(8):
                for col in range(8):
                    # Adjust coordinates based on board orientation
                    if self.board_flipped:
                        # Black at bottom (flipped view)
                        x1, y1 = (7 - col) * sq_size, row * sq_size
                    else:
                        # White at bottom (normal view)
                        x1, y1 = col * sq_size, (7 - row) * sq_size
                        
                    x2, y2 = x1 + sq_size, y1 + sq_size
                    
                    # Determine square color (light or dark)
                    color = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"  # Light and dark square colors
                    
                    self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                    
                    # Add rank/file coordinates
                    if col == 0:  # First column (ranks)
                        rank_number = row + 1
                        if self.board_flipped:
                            rank_number = 8 - rank_number
                        self.board_canvas.create_text(
                            x1 + 10, y1 + sq_size // 2, 
                            text=str(rank_number), 
                            fill="#000" if (row + col) % 2 == 0 else "#FFF",
                            font=("Helvetica", 10, "bold"),
                            anchor=tk.W
                        )
                    
                    if row == 0:  # Bottom row (files)
                        file_index = col
                        if self.board_flipped:
                            file_index = 7 - col
                        self.board_canvas.create_text(
                            x1 + sq_size // 2, y1 + sq_size - 10, 
                            text=chess.FILE_NAMES[file_index], 
                            fill="#000" if (row + col) % 2 == 0 else "#FFF",
                            font=("Helvetica", 10, "bold"),
                            anchor=tk.S
                        )
            
            # Draw pieces
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if not piece:
                    continue
                    
                # Get rank and file
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                
                # Calculate row and column based on board orientation
                if self.board_flipped:
                    # Black at bottom (flipped view)
                    row = rank
                    col = 7 - file
                else:
                    # White at bottom (normal view)
                    row = 7 - rank
                    col = file
                
                # Calculate pixel position
                x = col * sq_size + sq_size // 2
                y = row * sq_size + sq_size // 2
                
                # Piece symbol for display
                symbol = self._get_piece_symbol(piece)
                
                # Piece color
                text_color = "white" if piece.color == chess.WHITE else "black"
                outline_color = "black" if piece.color == chess.WHITE else "white"
                
                # Create the piece text with a thin outline
                self.board_canvas.create_text(
                    x, y,
                    text=symbol,
                    fill=text_color,
                    font=("Helvetica", 32, "bold")
                )
            
            # Highlight the last move
            if self.board.move_stack:
                last_move = self.board.peek()
                for square in [last_move.from_square, last_move.to_square]:
                    rank = chess.square_rank(square)
                    file = chess.square_file(square)
                    
                    # Calculate row and column based on board orientation
                    if self.board_flipped:
                        # Black at bottom (flipped view)
                        row = rank
                        col = 7 - file
                    else:
                        # White at bottom (normal view)
                        row = 7 - rank
                        col = file
                        
                    x1, y1 = col * sq_size, row * sq_size
                    x2, y2 = x1 + sq_size, y1 + sq_size
                    self.board_canvas.create_rectangle(
                        x1, y1, x2, y2, 
                        outline="#FFD700",  # Gold
                        width=3,
                        dash=(2, 4)
                    )
            
            # Highlight king in check
            if self.board.is_check():
                king_square = self.board.king(self.board.turn)
                if king_square is not None:
                    rank = chess.square_rank(king_square)
                    file = chess.square_file(king_square)
                    
                    # Calculate row and column based on board orientation
                    if self.board_flipped:
                        # Black at bottom (flipped view)
                        row = rank
                        col = 7 - file
                    else:
                        # White at bottom (normal view)
                        row = 7 - rank
                        col = file
                        
                    x1, y1 = col * sq_size, row * sq_size
                    x2, y2 = x1 + sq_size, y1 + sq_size
                    self.board_canvas.create_rectangle(
                        x1, y1, x2, y2, 
                        outline="#FF0000",  # Red
                        width=3
                    )
            
            # Update status
            turn = "White" if self.board.turn == chess.WHITE else "Black"
            status = f"{turn} to move"
            if self.board.is_check():
                status += " (CHECK)"
            elif self.board.is_checkmate():
                status = "Checkmate!"
            elif self.board.is_stalemate():
                status = "Stalemate!"
            
            self.status_var.set(status)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error updating board: {e}")
            self.status_var.set(f"Error: {e}")
            # Fallback to displaying a simple message on the canvas
            self.board_canvas.delete("all")
            self.board_canvas.create_text(250, 250, text=f"Board display error:\n{str(e)}", justify=tk.CENTER)
            
    def _get_piece_symbol(self, piece):
        """Get Unicode symbol for a chess piece."""
        symbols = {
            chess.PAWN: "♟" if piece.color == chess.BLACK else "♙",
            chess.KNIGHT: "♞" if piece.color == chess.BLACK else "♘",
            chess.BISHOP: "♝" if piece.color == chess.BLACK else "♗",
            chess.ROOK: "♜" if piece.color == chess.BLACK else "♖",
            chess.QUEEN: "♛" if piece.color == chess.BLACK else "♕",
            chess.KING: "♚" if piece.color == chess.BLACK else "♔"
        }
        return symbols.get(piece.piece_type, "?")
    
    def goto_start(self):
        """Go to the start of the game."""
        if self.game:
            self.current_node = self.game
            self.board = self.game.board()
            self.update_board_display()
            self.clear_analysis()
    
    def goto_end(self):
        """Go to the end of the game."""
        if self.game:
            self.current_node = self.game
            while self.current_node.variations:
                self.current_node = self.current_node.variations[0]
            self.board = self.current_node.board()
            self.update_board_display()
            self.analyze_current_position()
    
    def next_move(self):
        """Go to the next move."""
        if self.current_node and self.current_node.variations:
            self.current_node = self.current_node.variations[0]
            self.board = self.current_node.board()
            self.update_board_display()
            self.analyze_current_position()
    
    def prev_move(self):
        """Go to the previous move."""
        if self.current_node and self.current_node.parent:
            self.current_node = self.current_node.parent
            self.board = self.current_node.board()
            self.update_board_display()
            self.analyze_current_position()
    
    def on_move_selected(self, event):
        """Handle move selection from the move list."""
        selection = self.move_list.selection()
        if not selection:
            return
            
        try:
            move_idx = int(selection[0])
            self.current_node = self.game
            
            # Find the corresponding node (white's move)
            mainline = list(self.game.mainline())
            target_idx = min(move_idx * 2, len(mainline) - 1)
            
            for _ in range(target_idx + 1):
                if self.current_node.variations:
                    self.current_node = self.current_node.variations[0]
            
            self.board = self.current_node.board()
            self.update_board_display()
            self.analyze_current_position()
            
        except Exception as e:
            print(f"Error selecting move: {e}")
    
    def clear_analysis(self):
        """Clear thought process analysis."""
        self.thought_output.config(state=tk.NORMAL)
        self.thought_output.delete("1.0", tk.END)
        self.thought_output.config(state=tk.DISABLED)
    
    def analyze_current_position(self):
        """Analyze the current position using the thought process."""
        if not self.current_node:
            return
            
        self.thought_output.config(state=tk.NORMAL)
        self.thought_output.delete("1.0", tk.END)
        
        # Check if it's start position
        if self.current_node == self.game:
            self.thought_output.insert(tk.END, "Initial position. No analysis needed.", "normal")
            self.thought_output.config(state=tk.DISABLED)
            return
        
        # Get last move
        last_move = self.board.peek() if self.board.move_stack else None
        if not last_move:
            self.thought_output.config(state=tk.DISABLED)
            return
        
        # Initialize our candidate move collection
        candidate_moves_collection = {
            "Threats Response": [],
            "Checks": [],
            "Captures": [],
            "Threats": [],
            "Tactical Opportunities": [],
            "Strategic Improvements": []
        }
        
        # Implement thought process
        # 1. Check for threats
        threats = self.find_threats()
        
        # Insert step 1 heading
        self.thought_output.insert(tk.END, "STEP 1: Opponent Threats?\n", "heading")
        
        if threats:
            self.thought_output.insert(tk.END, "YES - Threats detected:\n", "highlight")
            for threat in threats:
                self.thought_output.insert(tk.END, f"• {threat}\n", "normal")
            
            # Step 2: Generate responses
            self.thought_output.insert(tk.END, "\nSTEP 2: Response Options\n", "heading")
            
            responses = self.generate_responses(threats)
            for category, moves in responses.items():
                if moves:
                    self.thought_output.insert(tk.END, f"{category}:\n", "subheading")
                    for move in moves:
                        self.thought_output.insert(tk.END, f"• {move}\n", "normal")
                        # Add these moves to candidate moves
                        candidate_moves_collection["Threats Response"].extend(moves)
            
        else:
            self.thought_output.insert(tk.END, "NO - No immediate threats\n", "normal")
            
            # Check if in opening or middlegame
            self.thought_output.insert(tk.END, "\nSTEP 2: Game Phase\n", "heading")
            
            # Determine game phase
            num_pieces = len(self.board.piece_map())
            move_number = (len(list(self.board.move_stack)) + 1) // 2
            
            if num_pieces > 28 and move_number < 10:  # Most pieces still on board and early moves
                phase = "Opening"
            elif num_pieces < 12:  # Few pieces left
                phase = "Endgame"
            else:
                phase = "Middlegame"
                
            self.thought_output.insert(tk.END, f"Current phase: {phase}\n", "normal")
        
        # Step 3 - Look for tactical signals (regardless of threats)
        self.thought_output.insert(tk.END, "\nSTEP 3: Tactical Signals or Targets?\n", "heading")
        
        # First, systematically check all checks, captures, and threats
        self.thought_output.insert(tk.END, "Performing CCT (Checks, Captures, Threats) analysis:\n", "subheading")
        
        # Check all possible checks
        checks = []
        for move in self.board.legal_moves:
            board_copy = self.board.copy()
            board_copy.push(move)
            if board_copy.is_check():
                checks.append(self.board.san(move))
        
        if checks:
            self.thought_output.insert(tk.END, "Possible checks:\n", "normal")
            for check in checks:
                self.thought_output.insert(tk.END, f"• {check}\n", "normal")
            candidate_moves_collection["Checks"].extend(checks)
        else:
            self.thought_output.insert(tk.END, "No checks available\n", "normal")
        
        # Check all possible captures
        captures = []
        for move in self.board.legal_moves:
            if self.board.is_capture(move):
                captures.append(self.board.san(move))
        
        if captures:
            self.thought_output.insert(tk.END, "Possible captures:\n", "normal")
            for capture in captures:
                self.thought_output.insert(tk.END, f"• {capture}\n", "normal")
            candidate_moves_collection["Captures"].extend(captures)
        else:
            self.thought_output.insert(tk.END, "No captures available\n", "normal")
        
        # Check all possible threats (moves that attack opponent pieces)
        threats = []
        for move in self.board.legal_moves:
            if not self.board.is_capture(move):  # Skip captures as they're already listed
                board_copy = self.board.copy()
                from_square = move.from_square
                to_square = move.to_square
                piece = board_copy.piece_at(from_square)
                
                if not piece:
                    continue
                
                # Make the move
                board_copy.push(move)
                
                # See if this creates new attacks on opponent pieces
                creates_threat = False
                for sq in chess.SQUARES:
                    target = board_copy.piece_at(sq)
                    if target and target.color != board_copy.turn:
                        if board_copy.is_attacked_by(board_copy.turn, sq):
                            attackers = list(board_copy.attackers(board_copy.turn, sq))
                            if to_square in attackers:
                                creates_threat = True
                                break
                
                if creates_threat:
                    threats.append(self.board.san(move))
        
        if threats:
            self.thought_output.insert(tk.END, "Moves creating threats:\n", "normal")
            for threat in threats[:5]:  # Limit to top 5 for readability
                self.thought_output.insert(tk.END, f"• {threat}\n", "normal")
            candidate_moves_collection["Threats"].extend(threats)
        else:
            self.thought_output.insert(tk.END, "No immediate threat-creating moves identified\n", "normal")
        
        # Now check for other tactical signals
        signals = self.find_tactical_signals()
        if signals:
            self.thought_output.insert(tk.END, "\nTactical opportunities identified:\n", "highlight")
            for signal in signals:
                self.thought_output.insert(tk.END, f"• {signal}\n", "normal")
                
            # Tactical ideas
            self.thought_output.insert(tk.END, "\nTactical Ideas:\n", "subheading")
            tactical_ideas, tactical_moves = self.analyze_tactical_position()
            for idea in tactical_ideas:
                self.thought_output.insert(tk.END, f"• {idea}\n", "normal")
            
            # Add tactical opportunity moves to candidates
            if tactical_moves:
                self.thought_output.insert(tk.END, "\nTactical candidate moves:\n", "normal")
                for move in tactical_moves:
                    self.thought_output.insert(tk.END, f"• {move}\n", "normal")
                candidate_moves_collection["Tactical Opportunities"].extend(tactical_moves)
        
        # Strategic position analysis (conditionally based on threats and user preference)
        self.thought_output.insert(tk.END, "\nSTEP 4: Strategic Analysis\n", "heading")
        
        # Check if threats were detected and simplified analysis is enabled
        if threats and self.simplify_analysis:
            self.thought_output.insert(tk.END, "Strategic analysis skipped due to detected threats\n", "highlight")
            self.thought_output.insert(tk.END, "Focus on addressing the immediate threats first\n", "normal")
            strategic_moves = []
        else:
            # Perform regular strategic analysis if no threats or simplified analysis is disabled
            strategic_ideas, strategic_moves = self.analyze_strategic_position()
            for idea in strategic_ideas:
                self.thought_output.insert(tk.END, f"• {idea}\n", "normal")
            
            # Add strategic moves to candidates
            if strategic_moves:
                self.thought_output.insert(tk.END, "\nStrategic candidate moves:\n", "normal")
                for move in strategic_moves:
                    self.thought_output.insert(tk.END, f"• {move}\n", "normal")
                candidate_moves_collection["Strategic Improvements"].extend(strategic_moves)
        
        # Compile the complete list of unique candidate moves
        all_candidates = []
        for category, moves in candidate_moves_collection.items():
            all_candidates.extend(moves)
        
        # Remove duplicates while preserving order
        unique_candidates = []
        seen = set()
        for move in all_candidates:
            if move not in seen:
                unique_candidates.append(move)
                seen.add(move)
        
        # Generate candidate moves from all sources
        if unique_candidates:
            self.thought_output.insert(tk.END, "\nSTEP 5: Candidate Move Selection\n", "heading")
            self.thought_output.insert(tk.END, "Complete list of candidate moves:\n", "normal")
            for move in unique_candidates:
                self.thought_output.insert(tk.END, f"• {move}\n", "normal")
            
            # Calculate variations for each candidate
            self.thought_output.insert(tk.END, "\nSTEP 6: Calculate Variations\n", "heading")
            self.thought_output.insert(tk.END, "Calculating lines for each candidate move...\n", "normal")
            
            # Check for actual next move made in the game
            next_node = None
            if self.current_node.variations:
                next_node = self.current_node.variations[0]
                actual_move = self.board.san(next_node.move)
                self.thought_output.insert(tk.END, f"\nActual move played: {actual_move}\n", "highlight")
            
            # Start engine analysis in separate thread
            threading.Thread(target=self._run_engine_analysis, args=(unique_candidates, next_node), daemon=True).start()
        else:
            self.thought_output.insert(tk.END, "\nNo candidate moves identified. Consider general principles.\n", "normal")
            
            # Still run engine analysis to get evaluation
            threading.Thread(target=self._run_engine_analysis, daemon=True).start()
        
        self.thought_output.config(state=tk.DISABLED)
    
    def can_lead_to_checkmate(self, attacking_square, king_square):
        """Determine if a checking piece could lead to checkmate within 3 ply."""
        # Create a copy of the board to analyze
        board_copy = self.board.copy()
        
        # Look ahead up to 3 ply to see if checkmate is possible
        for response in board_copy.legal_moves:
            # Make the response move
            board_after_response = board_copy.copy()
            board_after_response.push(response)
            
            # Check if the response prevents checkmate
            if board_after_response.is_checkmate():
                continue  # Checkmate already achieved!
                
            # Check opponent's moves
            has_checkmate_path = False
            for opponent_move in board_after_response.legal_moves:
                board_after_opponent = board_after_response.copy()
                board_after_opponent.push(opponent_move)
                
                # Check our next moves for checkmate
                for our_move in board_after_opponent.legal_moves:
                    final_board = board_after_opponent.copy()
                    final_board.push(our_move)
                    if final_board.is_checkmate():
                        has_checkmate_path = True
                        break
                        
                if has_checkmate_path:
                    break
                    
            if has_checkmate_path:
                return True
                
        return False
        
    def calculate_threat_line(self, target_square, attacker_square):
        """Calculate and explain a line showing how a threat could be executed."""
        # Create a copy of the board to analyze
        board_copy = self.board.copy()
        
        # Get information about the pieces involved
        target_piece = board_copy.piece_at(target_square)
        attacker_piece = board_copy.piece_at(attacker_square)
        
        if not target_piece or not attacker_piece:
            return None
            
        # Format piece names
        target_name = chess.piece_name(target_piece.piece_type).capitalize()
        attacker_name = chess.piece_name(attacker_piece.piece_type).capitalize()
        target_square_name = chess.square_name(target_square)
        attacker_square_name = chess.square_name(attacker_square)
        
        # Create a simple explanation
        explanation = f"The {attacker_name} on {attacker_square_name} can capture the {target_name}"
        
        # Calculate a possible continuation
        # Find the capturing move
        capture_move = None
        for move in board_copy.legal_moves:
            if move.from_square == attacker_square and move.to_square == target_square:
                capture_move = move
                break
                
        if not capture_move:
            return explanation
            
        # See what happens after the capture
        board_copy.push(capture_move)
        capturing_move_san = self.board.san(capture_move)
        
        # Check if this results in a tactical advantage
        if board_copy.is_check():
            return f"{explanation} with check: {capturing_move_san}+"
        
        # Check for material imbalance
        if self._piece_value(target_piece) > self._piece_value(attacker_piece):
            return f"{explanation} winning {self._piece_value(target_piece)} points of material with {capturing_move_san}"
            
        return explanation
    
    def find_threats(self):
        """Find tactical threats in the position."""
        threats = []
        
        # 1. Check for checks
        if self.board.is_check():
            # Find all checking pieces
            king_square = self.board.king(self.board.turn)
            checking_pieces = list(self.board.attackers(not self.board.turn, king_square))
            
            # Get explanation of the check
            if checking_pieces:
                checking_piece = self.board.piece_at(checking_pieces[0])
                checking_piece_name = chess.piece_name(checking_piece.piece_type).capitalize()
                checking_square = chess.square_name(checking_pieces[0])
                
                # Calculate the line that led to the check
                threat_explanation = f"You are in check by {checking_piece_name} from {checking_square}"
                
                # Add explanation of how the check could lead to material loss or checkmate
                if self.can_lead_to_checkmate(checking_pieces[0], king_square):
                    threat_explanation += " (could lead to checkmate)"
                
                threats.append(threat_explanation)
            else:
                threats.append("You are in check")
        
        # 2. Check for hanging (undefended) pieces
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                # Check if piece is attacked
                if self.board.is_attacked_by(not self.board.turn, square):
                    attackers = list(self.board.attackers(not self.board.turn, square))
                    defenders = list(self.board.attackers(self.board.turn, square))
                    
                    piece_name = chess.piece_name(piece.piece_type).capitalize()
                    piece_value = self._piece_value(piece)
                    sq_name = chess.square_name(square)
                    
                    # Case 1: Completely undefended piece
                    if len(defenders) == 0:
                        # Calculate a line to explain the threat
                        explanation = self.calculate_threat_line(square, attackers[0])
                        threat_msg = f"Undefended {piece_name} on {sq_name} is under attack"
                        if explanation:
                            threat_msg += f" - {explanation}"
                        threats.append(threat_msg)
                    # Case 2: Underdefended piece (more attackers than defenders)
                    elif len(attackers) > len(defenders):
                        explanation = self.calculate_threat_line(square, attackers[0])
                        threat_msg = f"Underdefended {piece_name} on {sq_name} is under attack"
                        if explanation:
                            threat_msg += f" - {explanation}"
                        threats.append(threat_msg)
                    # Case 3: Piece attacked by lower value piece
                    else:
                        for attacker_sq in attackers:
                            attacker = self.board.piece_at(attacker_sq)
                            if self._piece_value(attacker) < piece_value:
                                threats.append(f"{piece_name} on {sq_name} attacked by lower value piece")
                                break
        
        # 3. Check for tactical threats (forks, pins, discovered attacks)
        
        # Check for knight forks
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color != self.board.turn and piece.piece_type == chess.KNIGHT:
                # Get squares the knight attacks
                attack_squares = list(self.board.attacks(square))
                valuable_targets = []
                
                # Look for valuable pieces under attack
                for attack_sq in attack_squares:
                    target = self.board.piece_at(attack_sq)
                    if target and target.color == self.board.turn and target.piece_type in [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP]:
                        valuable_targets.append((attack_sq, target))
                
                # If knight attacks 2+ valuable pieces, it's a fork
                if len(valuable_targets) >= 2:
                    sq_name = chess.square_name(square)
                    threats.append(f"Knight fork threat from {sq_name}")
        
        # Check for pins and skewers
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece or piece.color != self.board.turn:
                continue
                
            if piece.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP]:
                # Define directions based on piece type
                directions = []
                if piece.piece_type in [chess.QUEEN, chess.ROOK]:
                    directions.extend([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Orthogonal
                if piece.piece_type in [chess.QUEEN, chess.BISHOP]:
                    directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])  # Diagonal
                
                # Check each direction for potential pins
                for dx, dy in directions:
                    file_idx = chess.square_file(square)
                    rank_idx = chess.square_rank(square)
                    
                    pieces_in_ray = []
                    x, y = file_idx + dx, rank_idx + dy
                    
                    # Follow the ray until we hit the edge or 3 pieces
                    while 0 <= x < 8 and 0 <= y < 8 and len(pieces_in_ray) < 3:
                        check_square = chess.square(x, y)
                        check_piece = self.board.piece_at(check_square)
                        
                        if check_piece:
                            pieces_in_ray.append((check_square, check_piece))
                        
                        x += dx
                        y += dy
                    
                    # Pin: We have exactly 2 pieces, the first is enemy, the second is a valuable enemy piece
                    if len(pieces_in_ray) == 2:
                        if (pieces_in_ray[0][1].color != self.board.turn and 
                            pieces_in_ray[1][1].color != self.board.turn):
                            # Check if the second piece is more valuable
                            if self._piece_value(pieces_in_ray[1][1]) > self._piece_value(pieces_in_ray[0][1]):
                                from_sq = chess.square_name(square)
                                target_sq = chess.square_name(pieces_in_ray[1][0])
                                threats.append(f"Potential skewer from {from_sq} to {target_sq}")
        
        # 4. Look for simple 3-ply tactics (including checkmates)
        
        # Check for checkmate in 2
        for move1 in self.board.legal_moves:
            board_after_move1 = self.board.copy()
            board_after_move1.push(move1)
            
            # If this move gives check
            if board_after_move1.is_check():
                no_escape = True
                
                # Try all opponent responses
                for response in board_after_move1.legal_moves:
                    board_after_response = board_after_move1.copy()
                    board_after_response.push(response)
                    
                    # Check if we can deliver checkmate
                    has_checkmate = False
                    for move2 in board_after_response.legal_moves:
                        board_final = board_after_response.copy()
                        board_final.push(move2)
                        
                        if board_final.is_checkmate():
                            has_checkmate = True
                            break
                    
                    # If no checkmate in this line, the enemy can escape
                    if not has_checkmate:
                        no_escape = False
                        break
                
                # If no escape exists, we found a forced checkmate
                if no_escape:
                    move_san = self.board.san(move1)
                    threats.append(f"Potential checkmate in 3 starting with {move_san}")
                    break
        
        # Look for other 3-ply winning tactics (like winning material)
        # This is a simplified version focusing on obvious material gain
        for move1 in self.board.legal_moves:
            # Skip if we already found checkmate
            if any("checkmate" in threat for threat in threats):
                break
                
            # Only consider captures or checks as first move
            if not (self.board.is_capture(move1) or self.board.gives_check(move1)):
                continue
                
            board_after_move1 = self.board.copy()
            board_after_move1.push(move1)
            
            # Skip if we're leaving our own pieces hanging after this move
            hanging_after_move = False
            for sq in chess.SQUARES:
                pc = board_after_move1.piece_at(sq)
                if pc and pc.color == board_after_move1.turn:
                    if board_after_move1.is_attacked_by(not board_after_move1.turn, sq):
                        attackers = list(board_after_move1.attackers(not board_after_move1.turn, sq))
                        defenders = list(board_after_move1.attackers(board_after_move1.turn, sq))
                        if len(attackers) > len(defenders) and self._piece_value(pc) >= 3:  # If valuable piece is hanging
                            hanging_after_move = True
                            break
            
            if hanging_after_move:
                continue
            
            # If we're forcing a response (check or attack on valuable piece)
            forced_response = False
            if board_after_move1.is_check():
                forced_response = True
            
            if forced_response:
                # Check all responses
                all_responses_losing = True
                for response in board_after_move1.legal_moves:
                    board_after_response = board_after_move1.copy()
                    board_after_response.push(response)
                    
                    # See if we can win material in the follow-up
                    material_win = False
                    for move2 in board_after_response.legal_moves:
                        if board_after_response.is_capture(move2):
                            captured_value = self._piece_value(board_after_response.piece_at(move2.to_square))
                            if captured_value >= 3:  # Winning at least a bishop/knight
                                material_win = True
                                break
                    
                    if not material_win:
                        all_responses_losing = False
                        break
                
                if all_responses_losing:
                    move_san = self.board.san(move1)
                    threats.append(f"Potential winning tactic starting with {move_san}")
        
        return threats
    
    def generate_responses(self, threats):
        """Generate possible responses to threats according to the thought process."""
        responses = {
            "Capture the attacker": [],
            "Block the threat": [],
            "Move the attacked piece": [],
            "Counterattack": []
        }
        
        # Get all legal moves
        legal_moves = list(self.board.legal_moves)
        
        # First, identify critical threats
        critical_threats = []
        for threat in threats:
            if "check" in threat.lower() or "under attack" in threat.lower():
                critical_threats.append(threat)
        
        # Process threats
        for threat in threats:
            # Handle check
            if "check" in threat.lower():
                for move in legal_moves:
                    board_copy = self.board.copy()
                    board_copy.push(move)
                    
                    # If not in check after move, it's a valid response
                    if not board_copy.is_check():
                        san = self.board.san(move)
                        
                        # Categorize the move
                        if self.board.is_capture(move):
                            attacker_square = None
                            for sq in self.board.attackers(not self.board.turn, self.board.king(self.board.turn)):
                                if move.to_square == sq:
                                    attacker_square = sq
                                    break
                            
                            if attacker_square is not None:
                                responses["Capture the attacker"].append(san)
                            else:
                                responses["Counterattack"].append(san)
                        elif self.board.piece_at(move.from_square).piece_type == chess.KING:
                            responses["Move the attacked piece"].append(san)
                        else:
                            responses["Block the threat"].append(san)
            
            # Handle piece under attack
            elif "under attack" in threat.lower():
                # Extract the square from the threat description
                match = re.search(r'on ([a-h][1-8])', threat)
                if match:
                    threatened_square = chess.parse_square(match.group(1))
                    
                    for move in legal_moves:
                        san = self.board.san(move)
                        
                        # Moving the threatened piece
                        if move.from_square == threatened_square:
                            responses["Move the attacked piece"].append(san)
                            
                        # Capturing an attacker
                        elif self.board.is_capture(move):
                            capture_target = self.board.piece_at(move.to_square)
                            if capture_target and capture_target.color != self.board.turn:
                                # Check if this captures an attacker
                                attackers = list(self.board.attackers(not self.board.turn, threatened_square))
                                if move.to_square in attackers:
                                    responses["Capture the attacker"].append(san)
                                else:
                                    responses["Counterattack"].append(san)
                                    
                        # Blocking the attack
                        else:
                            board_copy = self.board.copy()
                            original_attackers = list(board_copy.attackers(not board_copy.turn, threatened_square))
                            
                            board_copy.push(move)
                            new_attackers = list(board_copy.attackers(board_copy.turn, threatened_square))
                            
                            if len(new_attackers) > len(original_attackers):
                                responses["Block the threat"].append(san)
                            
                            # Check for counterattack
                            for square in chess.SQUARES:
                                piece = board_copy.piece_at(square)
                                if piece and piece.color != board_copy.turn:
                                    if board_copy.is_attacked_by(board_copy.turn, square):
                                        if "+" in san:  # If it gives check, it's a counterattack
                                            responses["Counterattack"].append(san)
                                            break
                                            
                                        # Or if it threatens a higher value piece
                                        threatened_piece = self.board.piece_at(threatened_square)
                                        if self._piece_value(piece) >= self._piece_value(threatened_piece):
                                            responses["Counterattack"].append(san)
                                            break
                                            
            # Handle fork threat
            elif "fork" in threat.lower():
                for move in legal_moves:
                    san = self.board.san(move)
                    board_copy = self.board.copy()
                    
                    # Find the potential forking piece
                    match = re.search(r'from ([a-h][1-8])', threat)
                    if match:
                        fork_square = chess.parse_square(match.group(1))
                        
                        # Capture the forking piece
                        if move.to_square == fork_square:
                            responses["Capture the attacker"].append(san)
                            
                        # Move a potentially forked piece
                        potential_targets = list(self.board.attacks(fork_square))
                        if move.from_square in potential_targets:
                            responses["Move the attacked piece"].append(san)
                            
                        # Create a counterattack
                        board_copy.push(move)
                        if board_copy.is_check():
                            responses["Counterattack"].append(san)
        
        # Remove duplicates and limit number of moves per category
        for category in responses:
            responses[category] = list(dict.fromkeys(responses[category]))  # Remove duplicates while preserving order
            responses[category] = responses[category][:5]  # Limit to 5 moves
            
        return responses
    
    def find_tactical_signals(self):
        """Find tactical signals in the position."""
        signals = []
        
        # Check for undefended pieces
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color != self.board.turn:
                if not any(self.board.attackers(not self.board.turn, square)):
                    piece_name = chess.piece_name(piece.piece_type).capitalize()
                    sq_name = chess.square_name(square)
                    signals.append(f"Undefended {piece_name} on {sq_name}")
        
        # Check for pins
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece or piece.color != self.board.turn or piece.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                continue
                
            # Check attacking rays
            directions = []
            if piece.piece_type in [chess.QUEEN, chess.ROOK]:
                directions.extend([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Orthogonal
            if piece.piece_type in [chess.QUEEN, chess.BISHOP]:
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])  # Diagonal
                
            for dx, dy in directions:
                file_idx = chess.square_file(square)
                rank_idx = chess.square_rank(square)
                
                pieces_in_ray = []
                x, y = file_idx + dx, rank_idx + dy
                
                while 0 <= x < 8 and 0 <= y < 8:
                    check_square = chess.square(x, y)
                    check_piece = self.board.piece_at(check_square)
                    
                    if check_piece:
                        pieces_in_ray.append((check_square, check_piece))
                        if len(pieces_in_ray) > 1:
                            break
                    
                    x += dx
                    y += dy
                
                if len(pieces_in_ray) == 2:
                    if pieces_in_ray[0][1].color != pieces_in_ray[1][1].color:
                        # Potential pin or X-ray attack
                        signals.append(f"Potential pin or X-ray attack with {chess.piece_name(piece.piece_type)} on {chess.square_name(square)}")
                        break
        
        # Check for weak king position
        enemy_king_square = self.board.king(not self.board.turn)
        if enemy_king_square is not None:
            # Count attackers around king
            king_file = chess.square_file(enemy_king_square)
            king_rank = chess.square_rank(enemy_king_square)
            
            attackers = 0
            for file_offset in [-1, 0, 1]:
                for rank_offset in [-1, 0, 1]:
                    if file_offset == 0 and rank_offset == 0:
                        continue
                    
                    check_file = king_file + file_offset
                    check_rank = king_rank + rank_offset
                    
                    if 0 <= check_file < 8 and 0 <= check_rank < 8:
                        check_square = chess.square(check_file, check_rank)
                        check_piece = self.board.piece_at(check_square)
                        
                        if check_piece and check_piece.color == self.board.turn:
                            attackers += 1
            
            if attackers >= 2:
                signals.append(f"Enemy king has multiple pieces attacking nearby (potential tactics)")
                
            # Check open files near king
            for file_offset in [-1, 0, 1]:
                check_file = king_file + file_offset
                if 0 <= check_file < 8:
                    is_open = True
                    for rank in range(8):
                        square = chess.square(check_file, rank)
                        if self.board.piece_at(square) and self.board.piece_type_at(square) == chess.PAWN:
                            is_open = False
                            break
                    
                    if is_open:
                        signals.append(f"Open file near enemy king (file {chess.FILE_NAMES[check_file]})")
        
        return signals
    
    def analyze_tactical_position(self):
        """Analyze tactical opportunities in the position."""
        ideas = []
        tactical_moves = []
        
        # Check for tactics possibilities
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece or piece.color != self.board.turn:
                continue
                
            # Knight fork opportunities
            if piece.piece_type == chess.KNIGHT:
                attack_squares = list(self.board.attacks(square))
                targets = []
                
                for attack_sq in attack_squares:
                    target = self.board.piece_at(attack_sq)
                    if target and target.color != self.board.turn and target.piece_type in [chess.KING, chess.QUEEN, chess.ROOK]:
                        targets.append(attack_sq)
                
                if len(targets) >= 2:
                    from_sq_name = chess.square_name(square)
                    ideas.append(f"Knight fork opportunity from {from_sq_name}")
                    
                    # Find moves that would create a knight fork
                    for move in self.board.legal_moves:
                        if move.from_square == square:
                            board_copy = self.board.copy()
                            board_copy.push(move)
                            
                            # Check if this created a fork
                            fork_targets = 0
                            attack_squares = list(board_copy.attacks(move.to_square))
                            for attack_sq in attack_squares:
                                target = board_copy.piece_at(attack_sq)
                                if target and target.color != board_copy.turn and target.piece_type in [chess.KING, chess.QUEEN, chess.ROOK]:
                                    fork_targets += 1
                            
                            if fork_targets >= 2:
                                move_san = self._safe_san(self.board, move)
                                if move_san:
                                    tactical_moves.append(move_san)
        
        # Check for discovered check opportunities
        for move in self.board.legal_moves:
            from_square = move.from_square
            piece = self.board.piece_at(from_square)
            if not piece:
                continue
                
            # Try the move
            board_copy = self.board.copy()
            board_copy.push(move)
            
            # If it gives check, it might be a discovered check
            if board_copy.is_check():
                # Check if the moving piece is not directly giving check
                king_square = board_copy.king(not board_copy.turn)
                if king_square:
                    if not board_copy.is_attacked_by(board_copy.turn, king_square):
                        move_san = self._safe_san(self.board, move)
                        if move_san:
                            ideas.append(f"Potential discovered check with {move_san}")
                            tactical_moves.append(move_san)
        
        # Check for checkmate patterns
        if self.board.is_check():
            ideas.append("Look for checkmate patterns")
            
            # Find potential checkmate moves
            for move in self.board.legal_moves:
                board_copy = self.board.copy()
                board_copy.push(move)
                
                if board_copy.is_checkmate():
                    ideas.append(f"Checkmate with {self.board.san(move)}")
                    tactical_moves.append(self.board.san(move))
        
        # Check for back rank weaknesses
        enemy_king_sq = self.board.king(not self.board.turn)
        if enemy_king_sq is not None:
            king_rank = chess.square_rank(enemy_king_sq)
            if (king_rank == 0 and not self.board.turn) or (king_rank == 7 and self.board.turn):
                # King on back rank - check for weaknesses
                ideas.append("Enemy king on back rank - look for mate patterns")
                
                # Find potential back rank moves
                for move in self.board.legal_moves:
                    if self.board.piece_type_at(move.from_square) in [chess.ROOK, chess.QUEEN]:
                        to_rank = chess.square_rank(move.to_square)
                        if to_rank == king_rank:
                            tactical_moves.append(self.board.san(move))
        
        # Look for pins
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece or piece.color != self.board.turn or piece.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
                continue
                
            # Check attacking rays
            directions = []
            if piece.piece_type in [chess.QUEEN, chess.ROOK]:
                directions.extend([(0, 1), (1, 0), (0, -1), (-1, 0)])  # Orthogonal
            if piece.piece_type in [chess.QUEEN, chess.BISHOP]:
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])  # Diagonal
                
            for dx, dy in directions:
                file_idx = chess.square_file(square)
                rank_idx = chess.square_rank(square)
                
                pieces_in_ray = []
                x, y = file_idx + dx, rank_idx + dy
                
                while 0 <= x < 8 and 0 <= y < 8:
                    check_square = chess.square(x, y)
                    check_piece = self.board.piece_at(check_square)
                    
                    if check_piece:
                        pieces_in_ray.append((check_square, check_piece))
                        if len(pieces_in_ray) > 1:
                            break
                    
                    x += dx
                    y += dy
                
                # If we have an enemy piece followed by an enemy king/queen, we might pin it
                if len(pieces_in_ray) == 2:
                    if (pieces_in_ray[0][1].color != self.board.turn and
                        pieces_in_ray[1][1].color != self.board.turn and
                        pieces_in_ray[1][1].piece_type in [chess.KING, chess.QUEEN, chess.ROOK]):
                        
                        # Find moves that would create a pin
                        for move in self.board.legal_moves:
                            if move.from_square == square:
                                # Check if move is along the same ray
                                to_file = chess.square_file(move.to_square)
                                to_rank = chess.square_rank(move.to_square)
                                
                                # If moving along the same ray towards the target
                                if (to_file - file_idx) // (abs(to_file - file_idx) if to_file != file_idx else 1) == dx and \
                                   (to_rank - rank_idx) // (abs(to_rank - rank_idx) if to_rank != rank_idx else 1) == dy:
                                    tactical_moves.append(self.board.san(move))
        
        # Find moves that exploit weak squares
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.color != self.board.turn:
                if not any(self.board.attackers(not self.board.turn, square)):
                    # This is an undefended piece - find moves that attack it
                    for move in self.board.legal_moves:
                        board_copy = self.board.copy()
                        board_copy.push(move)
                        
                        if board_copy.is_attacked_by(board_copy.turn, square):
                            tactical_moves.append(self.board.san(move))
        
        # Remove duplicates from tactical moves
        tactical_moves = list(dict.fromkeys(tactical_moves))
        
        return ideas, tactical_moves
    
    def analyze_strategic_position(self):
        """Analyze strategic elements of the position."""
        ideas = []
        strategic_moves = []
        
        # Determine game phase
        num_pieces = len(self.board.piece_map())
        if num_pieces > 28:  # Most pieces still on board
            phase = "Opening"
        elif num_pieces < 12:  # Few pieces left
            phase = "Endgame"
        else:
            phase = "Middlegame"
        
        # Phase-specific advice
        if phase == "Opening":
            # Check development status
            developed_minors = 0
            home_rank = 0 if self.board.turn == chess.WHITE else 7
            undeveloped_pieces = []
            
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    if chess.square_rank(square) != home_rank:
                        developed_minors += 1
                    else:
                        undeveloped_pieces.append(square)
            
            ideas.append(f"You have developed {developed_minors}/4 minor pieces")
            
            if developed_minors < 4:
                ideas.append("Focus on developing your remaining minor pieces")
                
                # Find development moves for undeveloped minor pieces
                for square in undeveloped_pieces:
                    piece = self.board.piece_at(square)
                    for move in self.board.legal_moves:
                        if move.from_square == square:
                            # Avoid moving to the first rank, and prefer more central moves
                            to_rank = chess.square_rank(move.to_square)
                            to_file = chess.square_file(move.to_square)
                            
                            if ((self.board.turn == chess.WHITE and to_rank > 0) or 
                                (self.board.turn == chess.BLACK and to_rank < 7)):
                                
                                # Prefer more central moves
                                if 2 <= to_file <= 5:
                                    strategic_moves.append(self.board.san(move))
                
            # Check castling status
            if self.board.has_castling_rights(self.board.turn):
                ideas.append("Consider castling to secure king safety")
                
                # Find castling moves
                for move in self.board.legal_moves:
                    if self.board.is_castling(move):
                        strategic_moves.append(self.board.san(move))
            
            # Check center control
            center_control = 0
            center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
            for square in center_squares:
                if self.board.is_attacked_by(self.board.turn, square):
                    center_control += 1
            
            ideas.append(f"You control {center_control}/4 central squares")
            
            if center_control < 2:
                ideas.append("Work on improving central control")
                
                # Find moves that improve center control
                for move in self.board.legal_moves:
                    board_copy = self.board.copy()
                    
                    # Current control
                    current_control = center_control
                    
                    # Apply move
                    board_copy.push(move)
                    
                    # Check new control
                    new_control = 0
                    for square in center_squares:
                        if board_copy.is_attacked_by(self.board.turn, square):
                            new_control += 1
                    
                    # If this move improves center control
                    if new_control > current_control:
                        strategic_moves.append(self.board.san(move))
                
        elif phase == "Middlegame":
            # Look for piece coordination and activity
            ideas.append("Focus on piece coordination and active pieces")
            
            # Find pieces with poor mobility and improve them
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if not piece or piece.color != self.board.turn:
                    continue
                
                if piece.piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                    # Calculate current piece mobility
                    current_moves = len(list(self.board.attacks(square)))
                    
                    # If piece has low mobility, find moves to improve it
                    if (piece.piece_type == chess.KNIGHT and current_moves < 4) or \
                       (piece.piece_type == chess.BISHOP and current_moves < 7) or \
                       (piece.piece_type == chess.ROOK and current_moves < 7) or \
                       (piece.piece_type == chess.QUEEN and current_moves < 14):
                        
                        ideas.append(f"Improve mobility of {chess.piece_name(piece.piece_type)} at {chess.square_name(square)}")
                        
                        # Find moves for this piece
                        for move in self.board.legal_moves:
                            if move.from_square == square:
                                board_copy = self.board.copy()
                                board_copy.push(move)
                                
                                # Calculate new mobility
                                if board_copy.is_capture(move):
                                    # Captures are generally good for activity
                                    strategic_moves.append(self.board.san(move))
                                else:
                                    new_moves = len(list(board_copy.attacks(move.to_square)))
                                    if new_moves > current_moves:
                                        strategic_moves.append(self.board.san(move))
            
            # Check pawn structure
            isolated_pawns = 0
            doubled_pawns = 0
            isolated_pawn_squares = []
            
            for file_idx in range(8):
                # Count pawns on this file
                pawns_on_file = []
                has_adjacent_pawn = False
                
                for rank_idx in range(8):
                    square = chess.square(file_idx, rank_idx)
                    piece = self.board.piece_at(square)
                    
                    if piece and piece.piece_type == chess.PAWN and piece.color == self.board.turn:
                        pawns_on_file.append(square)
                        
                        # Check for adjacent pawns
                        for adj_file in [file_idx - 1, file_idx + 1]:
                            if 0 <= adj_file < 8:
                                has_adjacent_file_pawn = False
                                
                                for adj_rank in range(8):
                                    adj_square = chess.square(adj_file, adj_rank)
                                    adj_piece = self.board.piece_at(adj_square)
                                    
                                    if adj_piece and adj_piece.piece_type == chess.PAWN and adj_piece.color == self.board.turn:
                                        has_adjacent_file_pawn = True
                                        break
                                
                                if has_adjacent_file_pawn:
                                    has_adjacent_pawn = True
                                    break
                
                if len(pawns_on_file) > 0 and not has_adjacent_pawn:
                    isolated_pawns += len(pawns_on_file)
                    isolated_pawn_squares.extend(pawns_on_file)
                
                if len(pawns_on_file) > 1:
                    doubled_pawns += len(pawns_on_file) - 1
            
            if isolated_pawns > 0:
                ideas.append(f"You have {isolated_pawns} isolated pawn(s) - consider strengthening your pawn structure")
                
                # Find moves that support isolated pawns
                for pawn_square in isolated_pawn_squares:
                    pawn_file = chess.square_file(pawn_square)
                    
                    # Find moves that place pieces near the isolated pawn
                    for move in self.board.legal_moves:
                        if self.board.piece_type_at(move.from_square) != chess.PAWN:
                            to_file = chess.square_file(move.to_square)
                            
                            # If the move places a piece on the same file or adjacent files
                            if abs(to_file - pawn_file) <= 1:
                                strategic_moves.append(self.board.san(move))
            
            if doubled_pawns > 0:
                ideas.append(f"You have {doubled_pawns} doubled pawn(s) - watch for weaknesses")
            
            # Check for outposts
            for square in chess.SQUARES:
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                
                # Potential outpost squares are on ranks 4-5-6 for White, 3-4-5 for Black
                if ((self.board.turn == chess.WHITE and 3 <= rank <= 5) or
                    (self.board.turn == chess.BLACK and 2 <= rank <= 4)):
                    
                    # Check if square can be protected by a pawn
                    can_be_pawn_protected = False
                    for adj_file in [file - 1, file + 1]:
                        if 0 <= adj_file < 8:
                            pawn_square = chess.square(adj_file, rank - 1 if self.board.turn == chess.WHITE else rank + 1)
                            pawn = self.board.piece_at(pawn_square)
                            if pawn and pawn.piece_type == chess.PAWN and pawn.color == self.board.turn:
                                can_be_pawn_protected = True
                                break
                    
                    if can_be_pawn_protected:
                        # Check if it's vacant or can be captured
                        piece = self.board.piece_at(square)
                        if not piece or piece.color != self.board.turn:
                            # Find knight moves to this square
                            for move in self.board.legal_moves:
                                if move.to_square == square and self.board.piece_type_at(move.from_square) == chess.KNIGHT:
                                    ideas.append(f"Knight outpost opportunity on {chess.square_name(square)}")
                                    strategic_moves.append(self.board.san(move))
            
        else:  # Endgame
            # King activity
            ideas.append("Activate your king in the endgame")
            
            # Find king activation moves
            king_square = self.board.king(self.board.turn)
            if king_square is not None:
                # Calculate current king distance from center
                king_file = chess.square_file(king_square)
                king_rank = chess.square_rank(king_square)
                king_center_distance = abs(king_file - 3.5) + abs(king_rank - 3.5)
                
                for move in self.board.legal_moves:
                    if move.from_square == king_square:
                        to_file = chess.square_file(move.to_square)
                        to_rank = chess.square_rank(move.to_square)
                        new_center_distance = abs(to_file - 3.5) + abs(to_rank - 3.5)
                        
                        # If move brings king closer to center
                        if new_center_distance < king_center_distance:
                            strategic_moves.append(self.board.san(move))
            
            # Passed pawns
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == self.board.turn:
                    file_idx = chess.square_file(square)
                    rank_idx = chess.square_rank(square)
                    
                    # Check if passed
                    is_passed = True
                    pawn_advance = 1 if self.board.turn == chess.WHITE else -1
                    
                    for advance in range(1, 8):
                        check_rank = rank_idx + advance * pawn_advance
                        if not (0 <= check_rank < 8):
                            break
                            
                        for check_file in [file_idx - 1, file_idx, file_idx + 1]:
                            if not (0 <= check_file < 8):
                                continue
                                
                            check_square = chess.square(check_file, check_rank)
                            check_piece = self.board.piece_at(check_square)
                            
                            if check_piece and check_piece.piece_type == chess.PAWN and check_piece.color != self.board.turn:
                                is_passed = False
                                break
                        
                        if not is_passed:
                            break
                    
                    if is_passed:
                        ideas.append(f"Passed pawn on {chess.square_name(square)} - advance it with support")
                        
                        # Find moves to advance this passed pawn
                        for move in self.board.legal_moves:
                            if move.from_square == square:
                                strategic_moves.append(self.board.san(move))
                            
                            # Find moves that support the passed pawn's advance
                            elif self.board.piece_at(move.from_square) and self.board.piece_at(move.from_square).color == self.board.turn:
                                # Check if move puts piece behind or beside the pawn
                                to_file = chess.square_file(move.to_square)
                                to_rank = chess.square_rank(move.to_square)
                                
                                if (to_file == file_idx or abs(to_file - file_idx) == 1) and \
                                   ((self.board.turn == chess.WHITE and to_rank < rank_idx) or 
                                    (self.board.turn == chess.BLACK and to_rank > rank_idx)):
                                    strategic_moves.append(self.board.san(move))
        
        # Remove duplicates
        strategic_moves = list(dict.fromkeys(strategic_moves))
        
        return ideas, strategic_moves
    
    def _run_engine_analysis(self, candidate_moves=None, next_node=None):
        """Run engine analysis in background thread."""
        try:
            if not self.engine:
                self.status_var.set("Engine not running. Analysis unavailable.")
                return
                
            # Analyze current position
            result = self.engine.analyse(
                self.board,
                chess.engine.Limit(depth=18, time=1.0)
            )
            
            # Dictionary to store full calculation lines for each candidate
            candidate_lines = {}
            
            # If we have candidate moves, evaluate each one and calculate lines
            candidate_evaluations = {}
            if candidate_moves:
                for move_san in candidate_moves:
                    try:
                        # Parse SAN move to get the move object
                        try:
                            move = self.board.parse_san(move_san)
                            # Verify it's a legal move in the current position
                            if move not in self.board.legal_moves:
                                print(f"Error evaluating move {move_san}: Illegal move in position {self.board.fen()}")
                                continue
                        except ValueError as e:
                            print(f"Error evaluating move {move_san}: {e}")
                            continue
                        except Exception as e:
                            print(f"Unexpected error evaluating move {move_san}: {e}")
                            continue
                        
                        # Make the move on a copy of the board
                        board_copy = self.board.copy()
                        board_copy.push(move)
                        
                        # Get a quick evaluation (lower depth for speed)
                        quick_result = self.engine.analyse(
                            board_copy,
                            chess.engine.Limit(depth=12, time=0.2)
                        )
                        
                        # Store evaluation (negate since it's from opponent's perspective)
                        score = -quick_result["score"].white().score(mate_score=10000)
                        candidate_evaluations[move_san] = score
                        
                        # Calculate deeper line for this candidate move
                        if "pv" in quick_result:
                            # Get the calculation line
                            calc_line = []
                            line_board = board_copy.copy()
                            
                            # First add the candidate move itself
                            calc_line.append(move_san)
                            
                            # Track if position is "quiet" (no captures, checks, or immediate threats)
                            quiet_reached = False
                            quiet_move_count = 0
                            max_depth = 5  # Limit calculation depth per candidate
                            
                            # Add opponent's best response and subsequent moves
                            for i, response_move in enumerate(quick_result["pv"]):
                                if i >= max_depth:
                                    break
                                    
                                # Get move in SAN notation
                                response_san = line_board.san(response_move)
                                line_board.push(response_move)
                                
                                # Check if position is now quiet
                                is_check = line_board.is_check()
                                has_captures = any(line_board.is_capture(m) for m in line_board.legal_moves)
                                has_threats = self._has_immediate_threats(line_board)
                                
                                quiet_position = not (is_check or has_captures or has_threats)
                                
                                if quiet_position:
                                    quiet_move_count += 1
                                else:
                                    quiet_move_count = 0
                                
                                # If we've had 2 quiet moves in a row, mark position as quiet
                                if quiet_move_count >= 2:
                                    quiet_reached = True
                                
                                # Format the move differently based on position state
                                if is_check:
                                    calc_line.append(f"{response_san}+ (check)")
                                elif has_captures:
                                    calc_line.append(f"{response_san} (capture)")
                                elif has_threats:
                                    calc_line.append(f"{response_san} (threat)")
                                else:
                                    calc_line.append(f"{response_san} (quiet)")
                                
                                if quiet_reached:
                                    calc_line.append("(Position is now quiet)")
                                    break
                            
                            # Store the complete calculation line
                            candidate_lines[move_san] = calc_line
                    except Exception as e:
                        print(f"Error evaluating move {move_san}: {e}")
            
            # Check actual move for blunders if available
            actual_move_analysis = None
            if next_node:
                try:
                    actual_move = next_node.move
                    # Use our safe SAN function
                    actual_move_san = self._safe_san(self.board, actual_move)
                    if actual_move_san is None:
                        raise ValueError(f"Illegal move: {actual_move} in position {self.board.fen()}")
                        
                    # Make the move on a copy of the board
                    board_after_actual = self.board.copy()
                    board_after_actual.push(actual_move)
                    
                    # Analyze the position after the actual move
                    actual_eval = self.engine.analyse(
                        board_after_actual,
                        chess.engine.Limit(depth=15, time=0.5)
                    )
                    
                    # Get evaluation of actual move
                    actual_score = -actual_eval["score"].white().score(mate_score=10000)
                    
                    # Check for tactics against the actual move
                    tactics_against = []
                    
                    # Check if there's a capture available
                    for move in board_after_actual.legal_moves:
                        if board_after_actual.is_capture(move) and board_after_actual.piece_at(move.to_square).piece_type != chess.PAWN:
                            capture_san = board_after_actual.san(move)
                            tactics_against.append(f"Immediate capture: {capture_san}")
                            break
                    
                    # Check if there's a fork available
                    for square in chess.SQUARES:
                        piece = board_after_actual.piece_at(square)
                        if piece and piece.color == board_after_actual.turn and piece.piece_type == chess.KNIGHT:
                            attack_squares = list(board_after_actual.attacks(square))
                            valuable_targets = 0
                            
                            for attack_sq in attack_squares:
                                target = board_after_actual.piece_at(attack_sq)
                                if target and target.color != board_after_actual.turn and target.piece_type in [chess.KING, chess.QUEEN, chess.ROOK]:
                                    valuable_targets += 1
                            
                            if valuable_targets >= 2:
                                tactics_against.append(f"Knight fork available with {chess.piece_name(piece.piece_type)} on {chess.square_name(square)}")
                                break
                    
                    # Compare with best move evaluation
                    if "pv" in result and result["pv"]:
                        best_move = result["pv"][0]
                        # Use our safe SAN function
                        best_move_san = self._safe_san(self.board, best_move)
                        if best_move_san is not None:  # Only proceed if the move can be converted to SAN
                            best_score = result["score"].white().score(mate_score=10000)
                            
                            # Check if actual move is significantly worse than best move
                            eval_difference = best_score - (-actual_score)
                            
                            if eval_difference > 100:  # More than 1 pawn worse
                                blunder_level = "inaccuracy"
                                if eval_difference > 200:  # More than 2 pawns worse
                                    blunder_level = "mistake"
                                if eval_difference > 300:  # More than 3 pawns worse
                                    blunder_level = "blunder"
                                
                            tactics_against.append(f"{blunder_level.capitalize()}: {best_move_san} was better by {eval_difference/100:.1f} pawns")
                    
                    # Store the blunder check result
                    actual_move_analysis = {
                        "move": actual_move_san,
                        "score": actual_score,
                        "tactics": tactics_against
                    }
                    
                except Exception as e:
                    print(f"Error analyzing actual move: {e}")
            
            # Update UI with analysis results
            self.root.after(0, lambda: self._update_analysis_output(
                result, 
                candidate_evaluations,
                candidate_lines,
                actual_move_analysis
            ))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Analysis error: {str(e)}"))
    
    def _update_analysis_output(self, result, candidate_evaluations=None, candidate_lines=None, actual_move_analysis=None):
        """Update analysis output with engine results."""
        self.thought_output.config(state=tk.NORMAL)
        
        # If we were evaluating candidate moves, update their evaluations first
        if candidate_evaluations:
            # Find and delete "Calculating..." placeholder
            calculate_pos = self.thought_output.search("Calculating lines for each candidate move...", "1.0", tk.END)
            if calculate_pos:
                line_end = self.thought_output.index(f"{calculate_pos} lineend")
                self.thought_output.delete(calculate_pos, f"{line_end}+1c")
                
            # Sort candidates by evaluation
            sorted_candidates = sorted(candidate_evaluations.items(), key=lambda x: x[1], reverse=True)
            
            # Identify clearly losing moves (more than 2 pawns worse than best move)
            if sorted_candidates:
                best_eval = sorted_candidates[0][1]
                threshold = best_eval - 200  # 2 pawns = 200 centipawns
                
                # Divide candidates into promising and eliminated
                promising_candidates = []
                eliminated_candidates = []
                
                for move_san, eval_score in sorted_candidates:
                    if eval_score < threshold:
                        eliminated_candidates.append((move_san, eval_score))
                    else:
                        promising_candidates.append((move_san, eval_score))
                
                # Show evaluations for promising candidates first
                self.thought_output.insert(tk.END, "Promising candidate moves (calculate further):\n", "highlight")
                for move_san, eval_score in promising_candidates:
                    eval_str = f"{eval_score/100:.2f}" if abs(eval_score) < 10000 else f"M{eval_score//10000}"
                    sign = "+" if eval_score > 0 else ""
                    self.thought_output.insert(tk.END, f"• {move_san}: {sign}{eval_str}\n", "normal")
                
                # Show detailed calculation for each promising candidate
                if candidate_lines and promising_candidates:
                    self.thought_output.insert(tk.END, "\nDetailed calculation for promising candidates:\n", "subheading")
                    
                    for move_san, _ in promising_candidates:
                        if move_san in candidate_lines:
                            line = candidate_lines[move_san]
                            self.thought_output.insert(tk.END, f"{move_san}: ", "highlight")
                            self.thought_output.insert(tk.END, " → ".join(line[1:]) + "\n\n", "normal")
                
                # Show eliminated candidates
                if eliminated_candidates:
                    self.thought_output.insert(tk.END, "Eliminated candidate moves (clearly worse):\n", "subheading")
                    for move_san, eval_score in eliminated_candidates:
                        eval_str = f"{eval_score/100:.2f}" if abs(eval_score) < 10000 else f"M{eval_score//10000}"
                        sign = "+" if eval_score > 0 else ""
                        self.thought_output.insert(tk.END, f"• {move_san}: {sign}{eval_str}\n", "normal")
        
        # Check actual move for blunders
        if actual_move_analysis:
            self.thought_output.insert(tk.END, "\nSTEP 7: Blunder Check for Actual Move\n", "heading")
            
            move_san = actual_move_analysis["move"]
            score = actual_move_analysis["score"]
            tactics = actual_move_analysis["tactics"]
            
            # Display the actual move's evaluation
            eval_str = f"{score/100:.2f}" if abs(score) < 10000 else f"M{score//10000}"
            sign = "+" if score > 0 else ""
            self.thought_output.insert(tk.END, f"Actual move played: {move_san} (Evaluation: {sign}{eval_str})\n", "highlight")
            
            # Display any tactics against the move
            if tactics:
                self.thought_output.insert(tk.END, "Potential issues with this move:\n", "normal")
                for tactic in tactics:
                    self.thought_output.insert(tk.END, f"• {tactic}\n", "normal")
            else:
                self.thought_output.insert(tk.END, "No tactical weaknesses found with this move.\n", "normal")
                
            # If we have a calculation line for the actual move, show it
            if candidate_lines and move_san in candidate_lines:
                line = candidate_lines[move_san]
                self.thought_output.insert(tk.END, "Calculation line after actual move:\n", "subheading")
                self.thought_output.insert(tk.END, " → ".join(line[1:]) + "\n", "normal")
        
        # Add a separator and engine analysis
        self.thought_output.insert(tk.END, "\n\nEngine Analysis\n", "heading")
        
        # Format the evaluation
        score = result["score"].white().score(mate_score=10000)
        if score is not None:
            score_str = f"{score/100:.2f}" if abs(score) < 10000 else f"M{score//10000}"
            sign = "+" if score > 0 else ""
            self.thought_output.insert(tk.END, f"Evaluation: {sign}{score_str}\n", "highlight")
            
            # Add the PV moves with calculation
            if "pv" in result:
                # Calculate variations until quiet
                self.thought_output.insert(tk.END, "Engine's best line until quiet position:\n", "normal")
                moves = []
                board_copy = self.board.copy()
                
                # Track if position is "quiet" (no captures, checks, or immediate threats)
                quiet_reached = False
                quiet_move_count = 0
                max_depth = 10  # Limit depth to avoid excessive output
                
                for i, move in enumerate(result["pv"]):
                    if i >= max_depth:
                        break
                    
                    # Get move in SAN notation using our safe function
                    move_san = self._safe_san(board_copy, move)
                    if move_san is None:
                        # Skip moves that can't be converted to SAN
                        continue
                        
                    # Push the move to update the board state
                    board_copy.push(move)
                    
                    # Check if position is now quiet
                    is_check = board_copy.is_check()
                    has_captures = any(board_copy.is_capture(m) for m in board_copy.legal_moves)
                    has_threats = self._has_immediate_threats(board_copy)
                    
                    quiet_position = not (is_check or has_captures or has_threats)
                    
                    if quiet_position:
                        quiet_move_count += 1
                    else:
                        quiet_move_count = 0
                    
                    # If we've had 2 quiet moves in a row, mark position as quiet
                    if quiet_move_count >= 2:
                        quiet_reached = True
                    
                    # Format the move differently based on position state
                    if is_check:
                        moves.append(f"{move_san}+ (check)")
                    elif has_captures:
                        moves.append(f"{move_san} (capture)")
                    elif has_threats:
                        moves.append(f"{move_san} (threat)")
                    else:
                        moves.append(f"{move_san} (quiet)")
                    
                    if quiet_reached:
                        moves.append("(Position is now quiet)")
                        break
                
                self.thought_output.insert(tk.END, " → ".join(moves) + "\n", "normal")
        
        # Add position evaluation
        self.thought_output.insert(tk.END, "\nSTEP 8: Final Position Evaluation\n", "heading")
        
        # Determine if position is good, equal, or bad based on evaluation
        if score is not None:
            if score > 100:  # More than 1 pawn advantage
                self.thought_output.insert(tk.END, "Position is favorable (+)\n", "highlight")
            elif score < -100:  # More than 1 pawn disadvantage
                self.thought_output.insert(tk.END, "Position is unfavorable (-)\n", "highlight")
            else:
                self.thought_output.insert(tk.END, "Position is roughly equal (=)\n", "highlight")
        
        # General advice for move selection
        self.thought_output.insert(tk.END, "\nMove Selection Guidelines:\n", "subheading")
        self.thought_output.insert(tk.END, "• Choose from the promising candidates after careful calculation\n", "normal")
        self.thought_output.insert(tk.END, "• Verify your selection doesn't blunder material\n", "normal")
        self.thought_output.insert(tk.END, "• Ensure your move addresses the position's key requirements\n", "normal")
        self.thought_output.insert(tk.END, "• Remember to blunder-check by looking for opponent's best responses\n", "normal")
        
        self.thought_output.config(state=tk.DISABLED)
    
    def _safe_san(self, board, move):
        """Safely convert a move to SAN notation with error handling."""
        try:
            # First verify move is legal in the current position
            if move in board.legal_moves:
                return board.san(move)
            else:
                return None
        except Exception as e:
            # Print error for debugging but don't crash
            print(f"Error converting move to SAN: {e}")
            return None

    def _has_immediate_threats(self, board):
        """Check if position has immediate threats."""
        # Check for pieces under attack
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:
                if board.is_attacked_by(not board.turn, square):
                    attackers = list(board.attackers(not board.turn, square))
                    defenders = list(board.attackers(board.turn, square))
                    
                    # If piece is attacked by lower-value piece, it's a threat
                    for attacker_sq in attackers:
                        attacker = board.piece_at(attacker_sq)
                        if self._piece_value(attacker) <= self._piece_value(piece):
                            return True
                            
                    # Or if more attackers than defenders
                    if len(attackers) > len(defenders):
                        return True
        
        # Check for fork opportunities
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color != board.turn and piece.piece_type == chess.KNIGHT:
                attack_squares = list(board.attacks(square))
                targets = []
                
                for attack_sq in attack_squares:
                    target = board.piece_at(attack_sq)
                    if target and target.color == board.turn and target.piece_type in [chess.KING, chess.QUEEN, chess.ROOK]:
                        targets.append(attack_sq)
                
                if len(targets) >= 2:
                    return True
        
        return False
    
    def _piece_value(self, piece):
        """Get the relative value of a piece."""
        if not piece:
            return 0
            
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 100
        }
        
        return values.get(piece.piece_type, 0)
    
    def start_engine(self):
        """Start the chess engine."""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            self.status_var.set(f"Engine started: {self.engine_path}")
        except Exception as e:
            self.status_var.set(f"Error starting engine: {str(e)}")
            self.engine = None
    
    def stop_engine(self):
        """Stop the chess engine."""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
            self.engine = None
            self.status_var.set("Engine stopped")
    
    def configure_engine(self):
        """Configure the chess engine."""
        engine_path = filedialog.askopenfilename(
            title="Select Chess Engine",
            filetypes=[
                ("Executable files", "*.exe *.bat"),
                ("All files", "*.*")
            ]
        )
        
        if engine_path:
            self.engine_path = engine_path
            self.stop_engine()
            self.start_engine()
    
    def show_thought_process(self):
        """Show thought process guide."""
        info = """
Chess Thinking Process:

1. When your opponent makes a move, check for threats:
   - Is your king in check?
   - Are any of your pieces under attack?
   - Are there any tactical threats (forks, pins, etc.)?

2. If there are threats, list all possible responses:
   - Capture the attacker
   - Block the threat
   - Move the attacked piece
   - Create a counterattack

3. If no threats, check the game phase and choose a direction:
   - In the opening: Develop pieces, control center, castle
   - In the middlegame: Look for tactics, improve pieces, make a plan
   - In the endgame: Activate king, advance pawns, create passed pawns

4. Look for tactical signals and targets:
   - Undefended pieces
   - Poorly defended pieces
   - Pieces lined up (X-rays, potential pins)
   - Weak enemy king
   - Overloaded pieces
   
5. Evaluate the position (+, =, or -) and choose a move
   - Always blunder-check your move before playing

This app will help you analyze how well you followed this process in your games.
"""
        tk.messagebox.showinfo("Thought Process Guide", info)
    
    def show_about(self):
        """Show about dialog."""
        tk.messagebox.showinfo(
            "About Chess Thought Analyzer",
            "Chess Thought Analyzer v1.0\n\n"
            "A focused application that helps you analyze chess games "
            "using a structured thought process.\n\n"
            "Created for adult chess improvers."
        )
    
    def save_analysis(self):
        """Save the current analysis to a text file."""
        if not self.game:
            tk.messagebox.showinfo("No Analysis", "No game has been analyzed yet.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="chess_analysis.txt"
        )
        
        if not file_path:
            return
            
        try:
            # Get the raw text from the thought process output
            analysis_text = self.thought_output.get("1.0", tk.END)
            
            # Save to file
            with open(file_path, 'w') as f:
                # Add game info
                white = self.game.headers.get("White", "Unknown")
                black = self.game.headers.get("Black", "Unknown")
                event = self.game.headers.get("Event", "Unknown")
                date = self.game.headers.get("Date", "Unknown")
                result = self.game.headers.get("Result", "Unknown")
                
                f.write(f"Game: {white} vs {black}, {event}, {date}, {result}\n\n")
                
                # Add current position info
                move_number = (len(list(self.board.move_stack)) + 1) // 2
                f.write(f"Analysis for move {move_number}\n\n")
                
                # Add the analysis
                f.write(analysis_text)
                
            self.status_var.set(f"Analysis saved to {file_path}")
            
        except Exception as e:
            tk.messagebox.showerror("Save Error", f"Error saving analysis: {str(e)}")
            self.status_var.set(f"Error saving analysis: {str(e)}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = ChessThoughtAnalyzer(root)
    root.mainloop()
    
    # Ensure engine is properly closed
    if app.engine:
        app.stop_engine()


if __name__ == "__main__":
    main()