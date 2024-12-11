import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import hclib
from urllib.parse import urlparse, parse_qs, unquote
from db import (
    add_game,
    add_move,
    get_latest_move,
    get_next_turn_no,
    update_game_result,
    create_tables,
    find_game_waiting_for_opponent,
    update_black_handle,
    get_game_by_no,
    get_all_games,
    get_moves_by_game_no,
)


# Add a constant global variable for game time
GAME_TIME = 300

# Ensure the tables are created
create_tables()
class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/' or parsed_url.path == '/index.html':
            self.serve_index()
        elif parsed_url.path == '/player.html':
            self.serve_player(parsed_url)
        elif parsed_url.path == '/opponent.html':
            self.serve_opponent(parsed_url)
        elif parsed_url.path == '/history.html':
            self.serve_history()
        elif parsed_url.path == '/gamelog.html':
            self.serve_gamelog(parsed_url)
        elif parsed_url.path == '/gameover.html':
            self.serve_gameover(parsed_url)
        elif parsed_url.path.startswith('/css/'):
            self.serve_static(parsed_url.path, 'css')
        elif parsed_url.path.startswith('/js/'):
            self.serve_static(parsed_url.path, 'js')
        elif parsed_url.path.startswith('/img/'):
            self.serve_static(parsed_url.path, 'img')
        elif parsed_url.path == '/check_for_opponent':
            self.handle_check_for_opponent_get(parsed_url)
        else:
            self.send_error(404, "Page not found")

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/login.html':
            self.handle_login(parsed_url)
        elif parsed_url.path == '/check_for_move':
            self.check_for_move()
        elif parsed_url.path == '/get_time_remaining':
            self.get_time_remaining()
        elif parsed_url.path == '/submit_move':
            self.process_player_move()
        elif parsed_url.path == '/check_for_opponent':
            self.handle_check_for_opponent_post()
        else:
            self.send_error(404, "Unsupported POST method")

    # -------------------- GET Handlers --------------------

    def serve_index(self):
        try:
            with open("index.html", "r") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in serve_index: %s", str(e))

    def serve_player(self, parsed_url):
        try:
            query_params = parse_qs(parsed_url.query)
            game_no_str = query_params.get('game_no', [None])[0]
            turn_no_str = query_params.get('turn_no', [None])[0]
            handle = query_params.get('handle', [None])[0]

            if game_no_str is None or turn_no_str is None or handle is None:
                self.send_error(400, "Missing game_no, turn_no, or handle")
                return

            try:
                game_no = int(game_no_str)
                turn_no = int(turn_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no or turn_no")
                return

            # Normalize handle to lower case
            handle = handle.strip().lower()

            # Get the game data
            game = get_game_by_no(game_no)

            if not game:
                self.send_error(404, "Game not found")
                return

            # Normalize stored handles to lower case
            white_handle = game[1].strip().lower()
            black_handle = game[2].strip().lower() if game[2] else None
            if not black_handle:
                # Redirect back to waiting.html without using an alert
                redirect_url = f"/waiting.html?game_no={game_no}&handle={handle}"
                content = f"""
                <html>
                <head>
                    <title>Waiting for Opponent</title>
                    <script>
                        window.location.href = '{redirect_url}';
                    </script>
                </head>
                <body>
                    <p>Opponent has not joined yet. Redirecting to waiting room...</p>
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode())
                return
            # Add debug statements
            print(f"serve_player - Player handle: {handle}")
            print(f"serve_player - White handle: {white_handle}")
            print(f"serve_player - Black handle: {black_handle}")

            # Determine player's color
            if white_handle == handle:
                player_color = 'W'
            elif black_handle == handle:
                player_color = 'B'
            else:
                self.send_error(403, "You are not part of this game.")
                return

            # Get the latest move
            latest_move = get_latest_move(game_no)
            if not latest_move:
                self.send_error(500, "No moves found for this game.")
                return

            # Check if it's the player's turn
            if latest_move[2] != player_color:
                # Not the player's turn; redirect to opponent.html
                self.redirect_to_opponent(game_no, latest_move[1], handle)
                return

            # Use the latest EFEN
            board_state_efen = latest_move[3]
            efen_fields = board_state_efen.strip().split(' ')
            if len(efen_fields) != 10:
                self.send_error(500, "Invalid EFEN format")
                return

            # Extract FEN and EFEN fields
            standard_fen = efen_fields[0]
            active_color = efen_fields[1]
            castling = efen_fields[2]
            enpassant = efen_fields[3]
            halfmove_clock = efen_fields[4]
            fullmove_number = efen_fields[5]
            white_prisoners = efen_fields[6]
            black_prisoners = efen_fields[7]
            white_holdable = efen_fields[8]
            black_holdable = efen_fields[9]

            # Read and render player.html with placeholders
            with open("player.html", "r") as f:
                content = f.read()
                content = content.replace("{{ game_no }}", str(game_no))
                content = content.replace("{{ turn_no }}", str(turn_no))
                content = content.replace("{{ handle }}", handle)
                content = content.replace("{{ white_handle }}", white_handle)
                content = content.replace("{{ black_handle }}", black_handle)
                content = content.replace("{{ board_state }}", board_state_efen)
                content = content.replace("{{ standard_fen }}", standard_fen)
                content = content.replace("{{ active_color }}", active_color)
                content = content.replace("{{ castling }}", castling)
                content = content.replace("{{ enpassant }}", enpassant)
                content = content.replace("{{ halfmove_clock }}", halfmove_clock)
                content = content.replace("{{ fullmove_number }}", fullmove_number)
                content = content.replace("{{ white_prisoners }}", white_prisoners)
                content = content.replace("{{ black_prisoners }}", black_prisoners)
                content = content.replace("{{ white_holdable }}", white_holdable)
                content = content.replace("{{ black_holdable }}", black_holdable)

            # Send the response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in serve_player: %s", str(e))


    def serve_opponent(self, parsed_url):
        try:
            query_params = parse_qs(parsed_url.query)
            game_no_str = query_params.get('game_no', [None])[0]
            turn_no_str = query_params.get('turn_no', [None])[0]
            handle = query_params.get('handle', [None])[0]

            if game_no_str is None or turn_no_str is None or handle is None:
                self.send_error(400, "Missing game_no, turn_no, or handle")
                return

            try:
                game_no = int(game_no_str)
                turn_no = int(turn_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no or turn_no")
                return

            # Normalize handle to lower case
            handle = handle.strip().lower()

            # Get the game data
            game = get_game_by_no(game_no)

            if not game:
                self.send_error(404, "Game not found")
                return

            # Normalize stored handles to lower case
            white_handle = game[1].strip().lower()
            black_handle = game[2].strip().lower() if game[2] else None

            # Determine player's color
            if white_handle == handle:
                player_color = 'W'
            elif black_handle == handle:
                player_color = 'B'
            else:
                self.send_error(403, "You are not part of this game.")
                return

            # Get the latest move
            latest_move = get_latest_move(game_no)
            if not latest_move:
                self.send_error(500, "No moves found for this game.")
                return

            # Check if it's the player's turn
            if latest_move[2] == player_color:
                # It's the player's turn; redirect to player.html
                self.redirect_to_player(game_no, latest_move[1], handle)
                return

            # Use the latest EFEN
            board_state_efen = latest_move[3]
            standard_fen = board_state_efen.split(' ')[0]

            # Render opponent.html with both EFEN and standard FEN
            with open("opponent.html", "r") as f:
                content = f.read()
                # Replace placeholders with actual values
                content = content.replace("{{ game_no }}", str(game_no))
                content = content.replace("{{ turn_no }}", str(latest_move[1]))
                content = content.replace("{{ board_state }}", board_state_efen)
                content = content.replace("{{ standard_fen }}", standard_fen)
                content = content.replace("{{ handle }}", handle)
                content = content.replace("{{ white_handle }}", game[1])
                content = content.replace("{{ black_handle }}", game[2] or "")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in serve_opponent: %s", str(e))


    def redirect_to_player(self, game_no, turn_no, handle):
        content = f"""
        <html>
        <head>
            <title>Your Turn</title>
            <script>
                window.location.href = '/player.html?game_no={game_no}&turn_no={turn_no}&handle={handle}';
            </script>
        </head>
        <body>
            <p>Your turn! Redirecting...</p>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def redirect_to_opponent(self, game_no, turn_no, handle):
        content = f"""
        <html>
        <head>
            <title>Waiting for Opponent</title>
            <script>
                window.location.href = '/opponent.html?game_no={game_no}&turn_no={turn_no}&handle={handle}';
            </script>
        </head>
        <body>
            <p>Waiting for opponent's move...</p>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    # -------------------- POST Handlers --------------------

    def handle_login(self, parsed_url):
        try:
            # Handle POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)

            # Extract the handle
            handle = data.get('handle', [None])[0]

            if not handle:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing handle.")
                return

            # Normalize handle
            handle = handle.strip().lower()

            # Check if there's a game waiting for an opponent
            waiting_game = find_game_waiting_for_opponent()

            if waiting_game:
                print(f"Found waiting game: {waiting_game[0]}")
                # A game is waiting for an opponent
                game_no = waiting_game[0]  # GAME_NO
                # Update the BLACK_HANDLE
                update_black_handle(game_no, handle)

                # Initialize the game state
                # Add an entry to the boards table with the initial move
                turn_no = 1
                turn = 'W'  # White's turn
                board = hclib.newboard()
                board_state_efen = hclib.extended_fen(
                    board, "w", "KQkq", "-", 0, 1
                )
                real_time = int(time.time())
                white_time = GAME_TIME
                black_time = GAME_TIME

                add_move(game_no, turn_no, turn, board_state_efen, real_time, white_time, black_time)

                # Redirect the second player to opponent.html
                content = f"""
                <html>
                <head>
                    <title>Game Found</title>
                    <script>
                        window.location.href = '/opponent.html?game_no={game_no}&turn_no=1&handle={handle}';
                    </script>
                </head>
                <body>
                    <p>Game found! Redirecting to opponent page...</p>
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode())

            else:
                print("No waiting game found. Creating a new game.")
                # No game is waiting; create a new game
                game_no = add_game(handle)

                # Read waiting.html and replace placeholders
                with open("waiting.html", "r") as f:
                    content = f.read()
                    content = content.replace("{{ game_no }}", str(game_no))
                    content = content.replace("{{ handle }}", handle)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in handle_login: %s", str(e))

    def check_for_move(self):
        try:
            # Handle POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)

            game_no_str = data.get('game_no', [None])[0]
            current_turn_no_str = data.get('turn_no', [None])[0]

            if game_no_str is None or current_turn_no_str is None:
                self.send_error(400, "Missing game_no or turn_no")
                return

            try:
                game_no = int(game_no_str)
                current_turn_no = int(current_turn_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no or turn_no")
                return

            # Get the latest turn number from the database
            latest_turn_no = get_next_turn_no(game_no) - 1

            if latest_turn_no > current_turn_no:
                # New move has been made
                response = {'new_move': True}
            else:
                response = {'new_move': False}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in check_for_move: %s", str(e))

    def get_time_remaining(self):
        try:
            # Handle POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)

            game_no_str = data.get('game_no', [None])[0]

            if game_no_str is None:
                self.send_error(400, "Missing game_no")
                return

            try:
                game_no = int(game_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no")
                return

            # Get the latest move
            latest_move = get_latest_move(game_no)
            if not latest_move:
                self.send_error(404, "No moves found for this game.")
                return

            # Extract time information
            white_time = latest_move[5]  # WHITE_TIME
            black_time = latest_move[6]  # BLACK_TIME

            # Check if game is over
            game = get_game_by_no(game_no)
            if game[3]:  # RESULT is at index 3
                game_over = True
                result = game[3]
            else:
                game_over = False
                result = None

            response = {
                'white_time': max(0, white_time),
                'black_time': max(0, black_time),
                'game_over': game_over,
                'result': result
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in get_time_remaining: %s", str(e))

    def handle_check_for_opponent_get(self, parsed_url):
        try:
            query_params = parse_qs(parsed_url.query)
            game_no_str = query_params.get('game_no', [None])[0]

            if game_no_str is None:
                self.send_error(400, "Missing game_no")
                return

            try:
                game_no = int(game_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no")
                return

            # Check if BLACK_HANDLE is set
            game = get_game_by_no(game_no)
            if game and game[2]:  # Check if BLACK_HANDLE is not None
                # Opponent has joined
                response = {'opponent_joined': True}
            else:
                response = {'opponent_joined': False}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in handle_check_for_opponent_get: %s", str(e))

    def handle_check_for_opponent_post(self):
        try:
            # Handle POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)

            game_no_str = data.get('game_no', [None])[0]

            if game_no_str is None:
                self.send_error(400, "Missing game_no")
                return

            try:
                game_no = int(game_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no")
                return

            # Check if BLACK_HANDLE is set
            game = get_game_by_no(game_no)
            if game and game[2]:  # Check if BLACK_HANDLE is not None
                # Opponent has joined
                response = {'opponent_joined': True}
            else:
                response = {'opponent_joined': False}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in handle_check_for_opponent_post: %s", str(e))

    def process_player_move(self):
        try:
            # Handle POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)

            # Extract necessary data (game_no, turn_no, handle, efen)
            game_no_str = data.get('game_no', [None])[0]
            turn_no_str = data.get('turn_no', [None])[0]
            handle = data.get('handle', [None])[0]
            board_state_efen = data.get('efen', [None])[0]

            # Validate inputs
            if game_no_str is None or turn_no_str is None or handle is None or board_state_efen is None:
                self.send_error(400, "Missing game_no, turn_no, handle, or efen")
                return

            try:
                game_no = int(game_no_str)
                turn_no = int(turn_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no or turn_no")
                return

            # Normalize handle to lower case
            handle = handle.strip().lower()

            # Get the game data
            game = get_game_by_no(game_no)
            if not game:
                self.send_error(404, "Game not found")
                return

            # Extract player handles
            white_handle = game[1].strip().lower()
            black_handle = game[2].strip().lower() if game[2] else None

            # Determine player's color
            if white_handle == handle:
                player_color = 'W'
            elif black_handle == handle:
                player_color = 'B'
            else:
                self.send_error(403, "You are not part of this game.")
                return

            # Get the latest move
            latest_move = get_latest_move(game_no)
            if not latest_move:
                self.send_error(500, "No moves found for this game.")
                return

            # Ensure it's the player's turn
            if latest_move[2] != player_color:
                self.send_error(400, "It's not your turn.")
                return

            # Determine the new TURN_NO
            new_turn_no = get_next_turn_no(game_no)

            # Determine whose turn it is now
            new_turn = 'B' if player_color == 'W' else 'W'

            # Get previous times and timestamps
            previous_real_time = latest_move[4]
            previous_white_time = latest_move[5]
            previous_black_time = latest_move[6]

            # Get current server time
            current_real_time = int(time.time())

            # Calculate time difference
            time_diff = current_real_time - previous_real_time

            # Update player's time
            if player_color == 'W':
                new_white_time = previous_white_time - time_diff
                new_black_time = previous_black_time
            else:
                new_black_time = previous_black_time - time_diff
                new_white_time = previous_white_time

            # Check for time expiration
            game_over = False
            winner = None
            if new_white_time <= 0:
                update_game_result(game_no, "Black wins on time")
                game_over = True
                winner = "Black"
            elif new_black_time <= 0:
                update_game_result(game_no, "White wins on time")
                game_over = True
                winner = "White"

            # Validate and save the new move
            if not game_over:
                # Retrieve the previous board state
                previous_board_state_efen = latest_move[3]

                # Validate the move using hclib
                is_valid, move_game_over, move_winner = self.validate_move_hclib(
                    previous_board_state_efen, board_state_efen, player_color
                )

                if not is_valid:
                    # Illegal move detected
                    opponent_color = 'Black' if player_color == 'W' else 'White'
                    update_game_result(game_no, f"{opponent_color} wins by disqualification")
                    game_over = True
                    winner = opponent_color
                elif move_game_over:
                    # King captured
                    winner = "White" if player_color == 'W' else "Black"
                    update_game_result(game_no, f"{winner} wins by capturing the king")
                    game_over = True

                if not game_over:
                    # Save the move
                    add_move(
                        game_no,
                        new_turn_no,
                        new_turn,
                        board_state_efen,
                        current_real_time,
                        new_white_time,
                        new_black_time
                    )

            # Prepare redirection based on game_over status
            if game_over:
                # Determine the player's outcome
                if winner == ("White" if player_color == 'W' else "Black"):
                    # Player won
                    outcome = "won"
                    message = f"Congratulations! You ({winner}) won the game!"
                else:
                    # Player lost
                    outcome = "lost"
                    message = f"Sorry! You ({'White' if player_color == 'B' else 'Black'}) lost the game."

                # Redirect to gameover.html with winner, result, and player_color
                redirect_url = f"/gameover.html?winner={winner}&result={message}&player_color={player_color}"
                content = f"""
                <html>
                <head>
                    <title>Game Over</title>
                    <script>
                        window.location.href = '{redirect_url}';
                    </script>
                </head>
                <body>
                    <p>Game Over! Redirecting...</p>
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode())
                return  # Exit the function after redirecting

            else:
                # If game is not over, redirect to opponent.html
                redirect_url = f"/opponent.html?game_no={game_no}&turn_no={new_turn_no}&handle={handle}"
                content = f"""
                <html>
                <head>
                    <title>Move Submitted</title>
                    <script>
                        window.location.href = '{redirect_url}';
                    </script>
                </head>
                <body>
                    <p>Move submitted! Redirecting to opponent page...</p>
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in process_player_move: %s", str(e))

    # -------------------- Helper Methods --------------------

    def validate_move_hclib(self, previous_board_state_efen, new_board_state_efen, player_color):
        try:
            print("new state:", new_board_state_efen)
            # Ensure the new_board_state_efen is valid
            tokens = new_board_state_efen.split(' ')
            expected_fields = 10  # Standard FEN (6) + 4 EFEN fields
            if len(tokens) != expected_fields:
                print(f"Invalid board_state EFEN field count: {len(tokens)}")
                return False, False, None

            # Parse EFEN tokens
            piece_placement = tokens[0]
            active_color = tokens[1]
            castling = tokens[2]
            en_passant = tokens[3]
            halfmove_clock = tokens[4]
            fullmove_number = tokens[5]
            white_prisoners = tokens[6]
            black_prisoners = tokens[7]
            white_holdable = tokens[8]
            black_holdable = tokens[9]

            # Deserialize the EFEN strings
            previous_board = hclib.extended_boardstring(previous_board_state_efen)
            if previous_board is None:
                print("Failed to parse previous EFEN.")
                return False, False, None

            new_board = hclib.extended_boardstring(new_board_state_efen)
            if new_board is None:
                print("Failed to parse new EFEN.")
                return False, False, None

            # Initialize variables
            move_from_i = move_from_j = move_to_i = move_to_j = None
            moved_piece = None
            captured_piece = None
            promotion = ' '  # Default to space character
            hostage = ' '    # Default to space character

            # Collect differences
            differences = []
            for i in range(8):
                for j in range(8):
                    prev_piece = hclib.get_board_value(previous_board, i, j)
                    new_piece = hclib.get_board_value(new_board, i, j)
                    if prev_piece != new_piece:
                        differences.append({
                            'i': i,
                            'j': j,
                            'prev_piece': prev_piece,
                            'new_piece': new_piece
                        })

            # Process differences
            if len(differences) >= 2:
                for diff in differences:
                    if diff['prev_piece'] != ' ' and diff['new_piece'] == ' ':
                        if move_from_i is None:
                            # From-square
                            move_from_i = diff['i']
                            move_from_j = diff['j']
                            moved_piece = diff['prev_piece']
                    elif diff['prev_piece'] != diff['new_piece']:
                        # To-square
                        move_to_i = diff['i']
                        move_to_j = diff['j']
                        moved_piece_to = diff['new_piece']
                        if diff['prev_piece'] != ' ':
                            # Captured piece found
                            captured_piece = diff['prev_piece']
            elif len(differences) == 1:
                # Possible hostage drop
                diff = differences[0]
                if diff['prev_piece'] == ' ' and diff['new_piece'] != ' ':
                    # Hostage drop
                    move_from_i = -1  # No from-square
                    move_from_j = -1
                    move_to_i = diff['i']
                    move_to_j = diff['j']
                    moved_piece = diff['new_piece']
                    hostage = moved_piece  # Set hostage to the piece being dropped
                else:
                    print("Unexpected difference for hostage drop.")
                    return False, False, None
            else:
                print("Unexpected number of differences:", len(differences))
                return False, False, None

            # Set hostage to captured piece if a capture occurred
            if captured_piece:
                hostage = captured_piece

            # Check for promotion
            if moved_piece.lower() == 'p' and (move_to_i == 0 or move_to_i == 7):
                # Get the promoted piece
                promotion = moved_piece_to
                if len(promotion) != 1:
                    print("Invalid promotion piece.")
                    return False, False, None
            else:
                promotion = ' '  # No promotion

            print(f"Move from ({move_from_i}, {move_from_j}) to ({move_to_i}, {move_to_j})")
            print(f"Moved piece: {moved_piece}, Promotion: '{promotion}', Hostage: '{hostage}'")

            # Ensure promotion and hostage are single characters
            if not isinstance(promotion, str) or len(promotion) != 1:
                print("Promotion must be a single character.")
                return False, False, None
            if not isinstance(hostage, str) or len(hostage) != 1:
                print("Hostage must be a single character.")
                return False, False, None

            # Create a move_t object
            move = hclib.move_t()
            move.from_i = move_from_i
            move.from_j = move_from_j
            move.to_i = move_to_i
            move.to_j = move_to_j
            move.promotion = promotion  # Single character
            move.hostage = hostage      # Set to captured piece or ' ' if no capture

            # Map player_color to current_player_color
            current_player_color = 0 if player_color == 'W' else 1

            # Use is_move_valid to validate the move
            is_valid = hclib.is_move_valid(previous_board, move, current_player_color)
            print("Valid:", is_valid)
            if not is_valid:
                print("Move is not valid according to hclib.")
                return False, False, None

            # The move is valid; the game logic should now handle updating prisoners
            # Update the EFEN string if necessary (game logic should handle this)

            # Check for king capture
            move_game_over = self.is_king_captured(new_board)
            move_winner = None
            if move_game_over:
                # Determine which king was captured
                white_king_found = False
                black_king_found = False
                for i in range(8):
                    for j in range(8):
                        piece = hclib.get_board_value(new_board, i, j)
                        if piece == 'K':
                            white_king_found = True
                        if piece == 'k':
                            black_king_found = True
                if not white_king_found:
                    move_winner = "Black"
                elif not black_king_found:
                    move_winner = "White"

            return True, move_game_over, move_winner
        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in process_player_move: %s", str(e))

    def is_king_captured(self, board):
        try:
            white_king_found = False
            black_king_found = False
            for i in range(8):
                for j in range(8):
                    piece = hclib.get_board_value(board, i, j)
                    if piece == 'K':
                        white_king_found = True
                    elif piece == 'k':
                        black_king_found = True
            return not (white_king_found and black_king_found)
        except Exception as e:
            self.log_error("Error in is_king_captured: %s", str(e))
            return False

    # -------------------- Rendering Handlers --------------------

    def serve_history(self):
        try:
            # Retrieve all games
            games = get_all_games()

            # Start building the HTML content
            content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Game History - Hostage Chess</title>
                <!-- Include Bootstrap CSS -->
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
                <!-- Include Font Awesome for Icons -->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
                <style>
                    body { 
                        padding: 40px; 
                        background-color: #f8f9fa;
                    }
                    .table-hover tbody tr:hover {
                        background-color: #f1f1f1;
                    }
                    .btn-custom {
                        margin-right: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="mb-4">Game History</h1>
                    <table class="table table-hover">
                        <thead class="thead-dark">
                            <tr>
                                <th>Game No</th>
                                <th>White Player</th>
                                <th>Black Player</th>
                                <th>Result</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # Populate the table with game data
            for game in games:
                game_no, white_handle, black_handle, result = game
                black_player = black_handle if black_handle else "Waiting for Opponent"
                game_result = result if result else "In Progress"
                content += f"""
                            <tr>
                                <td>{game_no}</td>
                                <td>{white_handle}</td>
                                <td>{black_player}</td>
                                <td>{game_result}</td>
                                <td>
                                    <a href="/gamelog.html?game_no={game_no}" class="btn btn-primary btn-sm btn-custom">
                                        <i class="fas fa-eye"></i> View Details
                                    </a>
                                </td>
                            </tr>
                """

            # Close the table and add navigation buttons
            content += """
                        </tbody>
                    </table>
                    <a href="/index.html" class="btn btn-secondary">
                        <i class="fas fa-home"></i> Back to Home
                    </a>
                </div>

                <!-- Include jQuery and Bootstrap JS -->
                <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"></script>
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
            </body>
            </html>
            """

            # Send the response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in serve_history: %s", str(e))
    def serve_gamelog(self, parsed_url):
        try:
            # Parse query parameters
            query_params = parse_qs(parsed_url.query)
            game_no_str = query_params.get('game_no', [None])[0]

            if game_no_str is None:
                self.send_error(400, "Missing game_no parameter")
                return

            try:
                game_no = int(game_no_str)
            except ValueError:
                self.send_error(400, "Invalid game_no parameter")
                return

            # Retrieve game and moves from the database
            game = get_game_by_no(game_no)
            moves = get_moves_by_game_no(game_no)

            if not game:
                self.send_error(404, "Game not found")
                return

            # Determine the final result
            result = game[3] if game[3] else "In Progress"

            # Start building the HTML content with proper brace escaping
            content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Game Log - Game {game_no}</title>
                
                <!-- Include Bootstrap CSS -->
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <!-- Include Font Awesome for Icons -->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
                <!-- Include Chessboard.js CSS from CDN -->
                <link rel="stylesheet" href="css/chessboard-1.0.0.css">

                <style>
                body {{
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .board-container {{
                    margin-bottom: 20px; /* Adjust space below the chessboard */
                }}
                .navigation-links {{
                    margin-top: 20px; /* Add more space above the buttons */
                    display: flex; /* Arrange buttons horizontally */
                    gap: 10px; /* Add space between the buttons */
                    justify-content: center; /* Center the buttons */
                }}
                .move-list {{
                    max-height: 300px;
                    overflow-y: auto;
                    margin-left: 20px; /* Add space between the chessboard and the move list */
                }}
                .move-item {{
                    cursor: pointer;
                }}
                .move-item.active {{
                    background-color: #007bff;
                    color: white;
                }}
                #board {{
                    height: 250px; /* Chessboard size */
                    width: 250px; /* Matching width for scaling */
                    margin: auto; /* Center the chessboard */
                    display: block; /* Block-level element for centering */
                }}
            </style>


            </head>
            <body>
                <div class="container">
                    <h1 class="mb-4">Game Log - Game {game_no}</h1>
                    <p><strong>White Player:</strong> {white_handle} &nbsp;&nbsp; <strong>Black Player:</strong> {black_handle}</p>
                    <p><strong>Result:</strong> {result}</p>
                    <hr>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div id="board" class="board-container"></div>
                            <div class="navigation-links mt-3">
                                <button id="prevMove" class="btn btn-secondary">Previous Move</button>
                                <button id="nextMove" class="btn btn-secondary">Next Move</button>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5>Move List</h5>
                            <ul class="list-group move-list" id="moveList">
            """.format(
                game_no=game_no,
                white_handle=game[1],
                black_handle=game[2],
                result=result
            )

            # Populate the move list with standard FEN (first 6 fields)
            for idx, move in enumerate(moves, start=1):
                turn_no = move[1]
                turn = 'White' if move[2] == 'W' else 'Black'
                move_description = "Turn {} - {}".format(turn_no, turn)
                efen = move[3]
                # Extract the first 6 fields for standard FEN
                standard_fen = ' '.join(efen.split(' ')[:6]) if efen else 'start'
                content += """
                                <li class="list-group-item move-item" data-fen="{fen}">{description}</li>
                """.format(fen=standard_fen, description=move_description)

            # Close the move list and add navigation buttons
            content += """
                            </ul>
                        </div>
                    </div>

                    <div class="navigation-links mt-4">
                        <a href="/history.html" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Back to Game History
                        </a>
                        <a href="/index.html" class="btn btn-primary">
                            <i class="fas fa-home"></i> Back to Home
                        </a>
                    </div>
                </div>

                <!-- Include jQuery and Bootstrap JS -->
                <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                <!-- Include Chessboard.js JS from CDN -->
                <script src="js/chessboard-1.0.0.js"></script>
                
                <script>
                    $(document).ready(function() {
                        // Initialize the chessboard
                        var board = Chessboard('board', {
                            position: 'start',
                            draggable: false,
                            showNotation: true
                        });

                        // Get all move items
                        var moves = document.querySelectorAll('.move-item');
                        var currentMoveIndex = 0;

                        // Function to update the chessboard
                        function updateBoard(fen) {
                            try {
                                if (fen.toLowerCase() === 'start') {
                                    board.start();
                                } else {
                                    board.position(fen);
                                }
                                console.log("Board updated to FEN:", fen);
                            } catch (error) {
                                console.error("Error updating board:", error);
                            }
                        }

                        // Initialize with the first move
                        if (moves.length > 0) {
                            var initialFen = moves[0].getAttribute('data-fen');
                            console.log("Initializing chessboard with FEN:", initialFen);
                            updateBoard(initialFen);
                            $(moves[0]).addClass('active');
                        }

                        // Move list click event
                        $('.move-item').click(function() {
                            $('.move-item').removeClass('active');
                            $(this).addClass('active');
                            var fen = $(this).data('fen');
                            console.log("Move clicked. FEN:", fen);
                            updateBoard(fen);
                            currentMoveIndex = $(this).index();
                        });

                        // Next Move button
                        $('#nextMove').click(function() {
                            if (currentMoveIndex < moves.length - 1) {
                                currentMoveIndex++;
                                var nextMove = moves[currentMoveIndex];
                                $('.move-item').removeClass('active');
                                $(nextMove).addClass('active');
                                var fen = $(nextMove).data('fen');
                                console.log("Next Move. FEN:", fen);
                                updateBoard(fen);
                            }
                        });

                        // Previous Move button
                        $('#prevMove').click(function() {
                            if (currentMoveIndex > 0) {
                                currentMoveIndex--;
                                var prevMove = moves[currentMoveIndex];
                                $('.move-item').removeClass('active');
                                $(prevMove).addClass('active');
                                var fen = $(prevMove).data('fen');
                                console.log("Previous Move. FEN:", fen);
                                updateBoard(fen);
                            }
                        });
                    });
                </script>
            </body>
            </html>
"""

            # Send the response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())

        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in serve_gamelog: %s", str(e))

    def serve_gameover(self, parsed_url):
        try:
            # Parse query parameters
            query_params = parse_qs(parsed_url.query)
            winner = query_params.get('winner', [None])[0]
            result = query_params.get('result', [None])[0]
            player_color = query_params.get('player_color', [None])[0]

            # Read the gameover.html content
            with open("gameover.html", "r") as f:
                content = f.read()

            # Determine the result message based on parameters
            if winner and result and player_color:
                # Normalize input for case-insensitive comparison
                winner_normalized = winner.strip().lower()
                player_color_normalized = player_color.strip().upper()

                if (winner_normalized == 'white' and player_color_normalized == 'W') or \
                (winner_normalized == 'black' and player_color_normalized == 'B'):
                    # Player won
                    result_message = f"Congratulations! You won the game! ({result.replace('%20', ' ')})"
                else:
                    # Player lost
                    result_message = f"You lost the game. {result.replace('%20', ' ')}"
            elif result:
                # Only result provided
                result_message = result.replace('%20', ' ')
            else:
                # Default message
                result_message = "Game over!"

            # Replace the placeholder with the actual result message using .format()
            content = """<!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Game Over</title>
                    <!-- Include Bootstrap CSS -->
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <!-- Include Bootstrap Icons -->
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
                    <!-- Include Custom CSS -->
                    <link rel="stylesheet" href="/css/styles.css">
                    <style>
                        body {{ 
                            padding: 50px; 
                            text-align: center; 
                            background-color: #f8f9fa;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: auto;
                        }}
                        .result-message {{
                            font-size: 1.8em;
                            margin-bottom: 30px;
                            font-weight: bold;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Game Over</h1>
                        <p class="result-message" id="resultMessage">{result_message}</p>
                        <div class="d-flex justify-content-center flex-wrap">
                            <a href="/history.html" class="btn btn-primary btn-custom">
                                <i class="bi bi-clock-history"></i> View History
                            </a>
                            <a href="/index.html" class="btn btn-success btn-custom">
                                <i class="bi bi-plus-circle"></i> Start New Game
                            </a>
                        </div>
                    </div>

                    <!-- Include Bootstrap JS Bundle -->
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                </body>
                </html>
                """.format(result_message=result_message)

            # Send the response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in serve_gameover: %s", str(e))
            print(f"Error in serve_gameover: {str(e)}")  # For debugging purposes




    def serve_static(self, file_path, file_type):
        try:
            # Remove query parameters if any
            file_path = unquote(file_path.split('?')[0])

            # Prevent directory traversal attacks
            if '..' in file_path:
                self.send_error(403, "Forbidden")
                return

            # Construct the full path
            full_path = '.' + file_path  # Assuming server.py is in the root directory

            # Open and read the file
            with open(full_path, 'rb') as file:
                content = file.read()
                self.send_response(200)

                # Determine the MIME type based on file extension
                if file_path.endswith('.html'):
                    self.send_header("Content-type", "text/html")
                elif file_path.endswith('.css'):
                    self.send_header("Content-type", "text/css")
                elif file_path.endswith('.js'):
                    self.send_header("Content-type", "application/javascript")
                elif file_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    if file_path.endswith('.png'):
                        self.send_header("Content-type", "image/png")
                    elif file_path.endswith('.gif'):
                        self.send_header("Content-type", "image/gif")
                    elif file_path.endswith('.svg'):
                        self.send_header("Content-type", "image/svg+xml")
                    else:
                        self.send_header("Content-type", "image/jpeg")
                else:
                    self.send_header("Content-type", "application/octet-stream")

                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File not found")
            self.log_error("Static file not found: %s", file_path)
        except Exception as e:
            self.send_error(500, "Internal Server Error")
            self.log_error("Error in serve_static: %s", str(e))


# -------------------- Run the Server --------------------

def run(server_class=HTTPServer, handler_class=RequestHandler):
    if len(sys.argv) != 2:
        print("Usage: python3 server.py PORT")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Port must be an integer.")
        sys.exit(1)

    server_address = ('0.0.0.0', port)  # Listen on all network interfaces
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on {server_address[0]} port {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == '__main__':
    run()
