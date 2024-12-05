#include "hclib.h"

// Creates a new baord
exboard_t *newboard(void)
{
    // Malloc space for a board
    exboard_t *board = calloc(1, sizeof(exboard_t));
    // Loop to add pieces to the table
    for (int i = 0; i < TABLE_SIZE; i++)
    {
        for (int j = 0; j < TABLE_SIZE; j++)
        {
            if (i == 0)
            {
                if (j == 0 || j == 7)
                {
                    board->board[i][j] = 'R';
                }
                if (j == 1 || j == 6)
                {
                    board->board[i][j] = 'N';
                }
                if (j == 2 || j == 5)
                {
                    board->board[i][j] = 'B';
                }
                if (j == 3)
                {
                    board->board[i][j] = 'Q';
                }
                if (j == 4)
                {
                    board->board[i][j] = 'K';
                }
            }
            else if (i == 1)
            {
                board->board[i][j] = 'P';
            }
            else if (i == 6)
            {
                board->board[i][j] = 'p';
            }
            else if (i == 7)
            {
                if (j == 0 || j == 7)
                {
                    board->board[i][j] = 'r';
                }
                if (j == 1 || j == 6)
                {
                    board->board[i][j] = 'n';
                }
                if (j == 2 || j == 5)
                {
                    board->board[i][j] = 'b';
                }
                if (j == 3)
                {
                    board->board[i][j] = 'q';
                }
                if (j == 4)
                {
                    board->board[i][j] = 'k';
                }
            }
            else
            {
                board->board[i][j] = ' ';
            }
        }
    }
    // Adding a null terminator to the other fields
    board->bprison[0] = '\0';
    board->bairfield[0] = '\0';
    board->wprison[0] = '\0';
    board->wairfield[0] = '\0';

    // Returning board
    return board;
}
// Creating a deep copy of the board
exboard_t *copyboard(exboard_t *board)
{
    if (board == NULL)
    {
        return NULL;
    }
    else
    {
        // Allocating enough space for one board
        exboard_t *cpyBoard = calloc(1, sizeof(exboard_t));
        if (cpyBoard == NULL)
        {
            return NULL;
        }
        else
        {
            // copying board to cpyboard
            memcpy(cpyBoard, board, sizeof(exboard_t));
        }
        // Returning the copied board
        return cpyBoard;
    }
}
// Function to serialize the exboard_t structure into a 162-character string
char *stringboard(exboard_t *board) {
    if (board == NULL) {
        return NULL;
    }

    // Allocate 162 characters (161 data + 1 null terminator)
    char *boardString = (char *)malloc(162);
    if (boardString == NULL) {
        return NULL;
    }

    // Initialize all characters to spaces
    for (int i = 0; i < 161; i++) {
        boardString[i] = ' ';
    }

    // Insert newline characters at every 9th index
    for (int i = 8; i < 161; i += 9) {
        boardString[i] = '\n';
    }

    for (int i = 0; i < 16; i++) {
        int dest_index;
        if (i < 8) {
            dest_index = i;
        } else {
            dest_index = 9 + (i - 8);
        }

        if (i < strlen(board->bprison)) {
            boardString[dest_index] = board->bprison[i];
        } else {
            boardString[dest_index] = ' ';
        }
    }

    for (int i = 0; i < 16; i++) {
        int dest_index;
        if (i < 8) {
            dest_index = 18 + i;
        } else {
            dest_index = 27 + (i - 8);
        }

        if (i < strlen(board->bairfield)) {
            char c = board->bairfield[i];
            boardString[dest_index] = isalnum(c) ? c : ' ';
        } else {
            boardString[dest_index] = ' ';
        }
    }

    for (int i = 36; i < 44; i++) {
        boardString[i] = '-';
    }

    for (int row = 7; row >= 0; row--) {
        int base_index;
        switch (row) {
            case 7:
                base_index = 45;
                break;
            case 6:
                base_index = 54;
                break;
            case 5:
                base_index = 63;
                break;
            case 4:
                base_index = 72;
                break;
            case 3:
                base_index = 81;
                break;
            case 2:
                base_index = 90;
                break;
            case 1:
                base_index = 99;
                break;
            case 0:
                base_index = 108;
                break;
            default:
                base_index = 0; // Should not happen
        }

        for (int col = 0; col < TABLE_SIZE; col++) {
            boardString[base_index + col] = board->board[row][col];
        }
    }

    for (int i = 117; i < 125; i++) {
        boardString[i] = '-';
    }

    for (int i = 0; i < 16; i++) {
        int dest_index;
        if (i < 8) {
            dest_index = 126 + i;
        } else {
            dest_index = 135 + (i - 8);
        }

        if (i < strlen(board->wairfield)) {
            char c = board->wairfield[i];
            boardString[dest_index] = isalnum(c) ? c : ' ';
        } else {
            boardString[dest_index] = ' ';
        }
    }

    for (int i = 0; i < 16; i++) {
        int dest_index;
        if (i < 8) {
            dest_index = 144 + i;
        } else {
            dest_index = 153 + (i - 8);
        }

        if (i < strlen(board->wprison)) {
            boardString[dest_index] = board->wprison[i];
        } else {
            boardString[dest_index] = ' ';
        }
    }

    boardString[161] = '\0';

    return boardString;
}

exboard_t *apply_move(exboard_t *board, move_t *move)
{
    char caputured = ' ';
    char piece = ' ';
    char castling = ' ';
    board->board[move->from_i][move->from_j] = ' ';
    if (move->from_i > -1 && move->from_i < 8)
    {
        if (board->board[move->to_i][move->to_j] == ' ')
        {
            piece = board->board[move->from_i][move->from_j];
            board->board[move->to_i][move->to_j] = piece;
        }
        // Completed Code for castling
        if (tolower(board->board[move->from_i][move->from_j]) == 'k' && calcStep(move->from_j, move->to_j) > 1)
        {
            piece = board->board[move->from_i][move->from_j];
            if (move->to_j - move->from_j > 0)
            {
                /* King has moved right */
                for (int i = move->to_j; i < TABLE_SIZE; i++)
                {
                    if (isalnum(board->board[move->to_i][i]))
                    {
                        board->board[move->to_i][move->to_j] = piece;        // Moves King to new spot
                        castling = board->board[move->to_i][i];              // Find the character that needs to castle
                        board->board[move->to_i][i] = ' ';                   // Empties the spot the castling game object moved from
                        board->board[move->to_i][move->to_j - 1] = castling; // Moves castled game object to new spot
                        break;
                    }
                }
            }
            else
            {
                /* King has moved left */
                for (int i = move->to_j; i >= 0; i--)
                {
                    if (isalnum(board->board[move->to_i][i]))
                    {
                        board->board[move->to_i][move->to_j] = piece;        // Moves King to new spot
                        castling = board->board[move->to_i][i];              // Find the character that needs to castle
                        board->board[move->to_i][i] = ' ';                   // Empties the spot the castling game object moved from
                        board->board[move->to_i][move->to_j + 1] = castling; // Moves castled game object to new spot
                        break;
                    }
                }
            }
        }
        // Completed Code for En passant
        else if (tolower(board->board[move->from_i][move->from_j]) == 'p' && calcStep(move->from_j, move->to_j) == 1 && calcStep(move->from_i, move->to_i) == 1)
        {
            piece = board->board[move->from_i][move->from_j];
            board->board[move->to_i][move->to_j] = piece;
            caputured = board->board[move->to_i - 1][move->to_j];
            if (islower(board->board[move->to_i][move->to_j]))
            {
                board->wprison[strlen(board->wprison)] = caputured;
                board->wprison[strlen(board->wprison) + 1] = '\0';
            }
            else
            {
                board->bprison[strlen(board->bprison)] = caputured;
                board->bprison[strlen(board->bprison) + 1] = '\0';
            }
        }
        else
        {
            caputured = board->board[move->to_i][move->to_j];
            piece = board->board[move->from_i][move->from_j];
            board->board[move->to_i][move->to_j] = piece;
            if (islower(board->board[move->to_i][move->to_j]))
            {
                board->wprison[strlen(board->wprison)] = caputured;
                board->wprison[strlen(board->wprison) + 1] = '\0';
            }
            else
            {
                board->bprison[strlen(board->wprison)] = caputured;
                board->bprison[strlen(board->wprison) + 1] = '\0';
            }
        }
    }

    else if (move->from_i == -2)
    {
        int found = 0;
        // Looping through the prison til we find the piece that needs to be promoted
        for (int i = 0; i < strlen(board->wprison); i++)
        {
            if (board->wprison[i] == move->promotion)
            {
                found = i;
                piece = board->wprison[i];
                // adding piece to the board
                board->board[move->to_i][move->from_j] = piece;
                break;
            }
        }
        // Shifting wprison over one to the left
        for (int i = found; i < strlen(board->wprison) - 1; i++)
        {
            board->wprison[i] = board->wprison[i + 1];
        }
        // Looping through the prison til we find the piece that needs to be moved to the airfield
        for (int i = 0; i < strlen(board->bprison); i++)
        {
            if (board->bprison[i] == move->hostage)
            {
                found = i;
                piece = board->bprison[i];
                break;
            }
        }
        // Shifting bprison over one to the left
        for (int i = found; i < strlen(board->bprison) - 1; i++)
        {
            board->bprison[i] = board->bprison[i + 1];
        }
        // Adding piece to the wairfield
        board->wairfield[strlen(board->wairfield)] = piece;
        board->wairfield[strlen(board->wairfield) + 1] = '\0';
    }
    else if (move->from_i == -1)
    {
        int found = 0;
        // Looping through air field to find the piece that should be moved to the board
        for (int i = 0; i < strlen(board->wairfield); i++)
        {
            if (board->wairfield[i] == move->promotion)
            {
                found = i;
                piece = board->wairfield[i];
                break;
            }
        }
        // Shifting every element of the array over by 1
        for (int i = found; i < strlen(board->wairfield) - 1; i++)
        {
            board->wairfield[i] = board->wairfield[i + 1];
        }
        // Adding piece to the board
        board->board[move->to_i][move->to_j] = piece;
    }
    else if (move->from_i == 8)
    {
        int found = 0;
        // Looping through air field to find the piece that should be moved to the board
        for (int i = 0; i < strlen(board->bairfield); i++)
        {
            if (board->bairfield[i] == move->promotion)
            {
                found = i;
                piece = board->bairfield[i];
                break;
            }
        }
        // Shifting every element of the array over by 1
        for (int i = found; i < strlen(board->bairfield) - 1; i++)
        {
            board->bairfield[i] = board->bairfield[i + 1];
        }
        // Adding piece to the board
        board->board[move->to_i][move->to_j] = piece;
    }
    else if (move->from_i == 9)
    {
        int found = 0;
        // Looping through the prison til we find the piece that needs to be promoted
        for (int i = 0; i < strlen(board->bprison); i++)
        {
            if (board->bprison[i] == move->promotion)
            {
                found = i;
                piece = board->bprison[i];
                // adding piece to the board
                board->board[move->to_i][move->from_j] = piece;
                break;
            }
        }
        // Shifting every element of the array over by 1
        for (int i = found; i < strlen(board->bprison) - 1; i++)
        {
            board->bprison[i] = board->bprison[i + 1];
        }
        // Looping through the prison til we find the piece that needs to be moved to the airfield
        for (int i = 0; i < strlen(board->wprison); i++)
        {
            if (board->wprison[i] == move->hostage)
            {
                found = i;
                piece = board->wprison[i];
                break;
            }
        }
        // Shifting every element of the array over by 1
        for (int i = found; i < strlen(board->wprison) - 1; i++)
        {
            board->wprison[i] = board->wprison[i + 1];
        }
        // Adding piece to the bairfield
        board->bairfield[strlen(board->bairfield)] = piece;
        board->bairfield[strlen(board->bairfield) + 1] = '\0';
    }
    return board;
}

// Depending on which piece we are looking at it will return a list of possible movements for particular piece on the board
move_t **moves(board_t *board, int from_i, int from_j)
{
    printf("Start pos: %d %d\n", from_i, from_j);
    if ((*board)[from_i][from_j] == 'N' || (*board)[from_i][from_j] == 'n')
    {
        return knightmoves(board, from_i, from_j, findColour((*board)[from_i][from_j]));
    }
    else if ((*board)[from_i][from_j] == 'B' || (*board)[from_i][from_j] == 'b')
    {
        return bishopmoves(board, from_i, from_j, findColour((*board)[from_i][from_j]));
    }
    else if ((*board)[from_i][from_j] == 'R' || (*board)[from_i][from_j] == 'r')
    {
        return rookmoves(board, from_i, from_j, findColour((*board)[from_i][from_j]));
    }
    else if ((*board)[from_i][from_j] == 'Q' || (*board)[from_i][from_j] == 'q')
    {
        return queenmoves(board, from_i, from_j, findColour((*board)[from_i][from_j]));
    }
    else if ((*board)[from_i][from_j] == 'P' || (*board)[from_i][from_j] == 'p')
    {
        return pawn_moves(board, from_i, from_j, findColour((*board)[from_i][from_j]));
    }
    else if ((*board)[from_i][from_j] == 'K' || (*board)[from_i][from_j] == 'k')
    {
        return king_moves(board, from_i, from_j, findColour((*board)[from_i][from_j]));
    }
    return NULL;
}
// Array of possible movements for the knight piece
move_t **knightmoves(board_t *board, int from_i, int from_j, int colour)
{
    printf("Knight Start Moves: %d %d\n", from_i, from_j);
    // Movements that a knight could possibly have
    movement knight_movements[] = {{2, 1}, {2, -1}, {-2, 1}, {-2, -1}, {1, 2}, {1, -2}, {-1, 2}, {-1, -2}};

    // Allocate enough space for all the knight moves
    move_t **moves = malloc(10 * sizeof(move_t *));

    // Keep track of all posssible moves for the knight given the current board
    int move_count = 0;

    // Looping through all eight possible moves to the knight
    for (int k = 0; k < 8; k++)
    {
        // Selecting the possible space on the board the knight could move to based on the fixed movement pattern provided
        int move_to_i = from_i + knight_movements[k].y_movement;
        int move_to_j = from_j + knight_movements[k].x_movement;

        // Check if the move is on the board
        if (move_to_i > -1 && move_to_i < 8 && move_to_j > -1 && move_to_j < 8)
        {
            // Character to keep track of whats at the current position
            char spot = (*board)[move_to_i][move_to_j];

            // Checking if the spot is empty or if it has a piece if the opposite colour
            if (spot == ' ' || (colour == 0 && islower(spot)) || (colour == 1 && isupper(spot)))
            {
                move_t *move = setMove(from_i, from_j, move_to_i, move_to_j, ' ', spot);
                // Added to the move array as a possible move
                moves[move_count] = move;
                // Increment the array
                move_count++;
            }
        }
    }

    // Resize the array
    moves = realloc(moves, (move_count + 1) * sizeof(move_t *));
    // Set the last element to NULL
    moves[move_count] = NULL;

    return moves;
}
move_t **bishopmoves(board_t *board, int from_i, int from_j, int colour)
{
    // Directions that a bishop could possibly move in
    movement bishop_directions[] = {{1, 1}, {1, -1}, {-1, 1}, {-1, -1}};
    // Allocate enough space for all the bishop moves
    move_t **moves = malloc(16 * sizeof(move_t *));
    int move_count = 0;
    // Loop through all 4 diagonal directions
    for (int k = 0; k < 4; k++)
    {
        // Loop through the maximum number movements in a diagonal direction
        for (int l = 1; l < 8; l++)
        {
            // Selecting the possible space on the board the bishop could move to based on the fixed movement pattern provided
            int move_to_i = from_i + l * bishop_directions[k].y_movement;
            int move_to_j = from_j + l * bishop_directions[k].x_movement;

            // Check if the move is on the board
            if (move_to_i > -1 && move_to_i < 8 && move_to_j > -1 && move_to_j < 8)
            {
                // Character to keep track of whats at the current position
                char spot = (*board)[move_to_i][move_to_j];
                printf("Piece at spot: %c\n", spot);
                // Checking if the spot is the same colour and if it is then we exit the inner for loop
                if ((colour == 1 && islower(spot)) || (colour == 0 && isupper(spot)))
                {
                    printf("same colour\n");
                    break;
                }
                else
                {
                    // Adding a move
                    moves[move_count] = setMove(from_i, from_j, move_to_i, move_to_j, ' ', spot);
                    move_count++;
                }
            }
        }
    }
    // Resize the array
    moves = realloc(moves, (move_count + 1) * sizeof(move_t *));
    // Set the last element to NULL
    moves[move_count] = NULL;
    return moves;
}

move_t **rookmoves(board_t *board, int from_i, int from_j, int colour)
{
    // Directions that a rook could possibly move in
    movement rook_directions[] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    // Allocate enough space for all the rook moves
    move_t **moves = malloc(16 * sizeof(move_t *));
    int move_count = 0;

    // Loop through the maximum number movements in a direction
    for (int k = 0; k < 4; k++)
    {
        for (int l = 1; l < 8; l++)
        {
            // Selecting the possible space on the board the rook could move to based on the fixed movement pattern provided
            int move_to_i = from_i + l * rook_directions[k].y_movement;
            int move_to_j = from_j + l * rook_directions[k].x_movement;

            // Check if the move is on the board
            if (move_to_i > -1 && move_to_i < 8 && move_to_j > -1 && move_to_j < 8)
            {
                // Character to keep track of whats at the current position
                char spot = (*board)[move_to_i][move_to_j];

                // Checking if the spot is the same colour and if it is then we exit the inner for loop
                if ((colour == 1 && islower(spot)) || (colour == 0 && isupper(spot)))
                {
                    break;
                }
                else
                {
                    // Adding a move
                    moves[move_count] = setMove(from_i, from_j, move_to_i, move_to_j, ' ', spot);
                    move_count++;
                }
            }
        }
    }
    // Resize the array
    moves = realloc(moves, (move_count + 1) * sizeof(move_t *));
    // Setting the last element as Null
    moves[move_count] = NULL;

    return moves;
}
move_t **queenmoves(board_t *board, int from_i, int from_j, int colour)
{
    // Gets the array of possible bishop and rook moves
    move_t **bishop_moves = bishopmoves(board, from_i, from_j, colour);
    move_t **rook_moves = rookmoves(board, from_i, from_j, colour);

    int rook_move = 0;
    int bishop_move = 0;
    int total_moves = 0;

    // Count rook moves
    while (rook_moves[rook_move] != NULL)
    {
        rook_move++;
    }
    // Count bishop moves
    while (bishop_moves[bishop_move] != NULL)
    {
        bishop_move++;
    }
    total_moves = rook_move + bishop_move;
    // Mallocing enough space for all the queen moves
    move_t **moves = malloc((total_moves + 1) * sizeof(move_t *));

    // Adding all if the bishop and rook moves to the array of moves for the queen
    for (int i = 0; i < bishop_move; i++)
    {
        moves[i] = bishop_moves[i];
    }
    for (int i = 0; i < rook_move; i++)
    {
        moves[bishop_move + i] = rook_moves[i];
    }
    // setting the last index of the array equal to null
    moves[total_moves] = NULL;
    // Freeing the memory used for the rook and bishop
    free(rook_moves);
    free(bishop_moves);

    return moves;
}
move_t **king_moves(board_t *board, int from_i, int from_j, int colour)
{

    // Movements that a knight could possibly have
    movement king_movements[] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {1, -1}, {-1, 1}, {-1, -1}};
    // Mallocing enough space for all of the kings moves
    move_t **moves = malloc(10 * sizeof(move_t *));
    int move_count = 0;

    for (int k = 0; k < 8; k++)
    {
        // Selecting the possible space on the board the rook could move to based on the fixed movement pattern provided
        int move_to_i = from_i + king_movements[k].y_movement;
        int move_to_j = from_j + king_movements[k].x_movement;

        // Check if the move is on the board
        if (move_to_i > -1 && move_to_i < 8 && move_to_j > -1 && move_to_j < 8)
        {
            char spot = (*board)[move_to_i][move_to_j];

            // Checking if the spot is empty or if it has a piece if the opposite colour
            if (spot == ' ' || (colour == 0 && islower(spot)) || (colour == 1 && isupper(spot)))
            {
                move_t *move = setMove(from_i, from_i, move_to_i, move_to_j, ' ', spot);
                moves[move_count] = move;
                move_count++;
            }
        }
    }

    // Resize the array to fit exactly move_count + 1 elements
    moves = realloc(moves, (move_count + 1) * sizeof(move_t *));
    // setting the last index of the array equal to null
    moves[move_count] = NULL;

    return moves;
}
move_t **pawn_moves(board_t *board, int from_i, int from_j, int colour)
{
    movement pawn_movements[] = {{0, 1}, {0, 2}, {1, 1}, {-1, 1}};
    move_t **moves = malloc(5 * sizeof(move_t *));
    int move_count = 0;
    int direction = 0;
    if (colour == 0)
    {
        direction = 1;
    }
    else
    {
        direction = -1;
    }

    // Move forward one step
    if ((*board)[from_i + direction * pawn_movements[0].y_movement][from_j] == ' ')
    {
        moves[move_count] = setMove(from_i, from_j, from_i + direction * pawn_movements[0].y_movement, from_j, ' ', ' ');
        move_count++;

        // Check if the pawn is in the starting position
        if ((from_i == 1 && colour == 0) || (from_i == 6 && colour == 1))
        {
            if ((*board)[from_i + direction * pawn_movements[1].y_movement][from_j] == ' ')
            {
                moves[move_count] = setMove(from_i, from_j, from_i + direction * pawn_movements[1].y_movement, from_j, ' ', ' ');
                move_count++;
            }
        }
    }

    // Diagonal capture to the left
    if (from_j > 0)
    {
        char spot = (*board)[from_i + direction * pawn_movements[2].y_movement][from_j + pawn_movements[2].x_movement];
        if ((colour == 0 && islower(spot)) || (colour == 1 && isupper(spot)))
        {
            moves[move_count] = setMove(from_i, from_j, from_i + direction * pawn_movements[2].y_movement, from_j + pawn_movements[2].x_movement, ' ', spot);
            move_count++;
        }
    }

    // Diagonal capture to the right
    if (from_j < 7)
    {
        char spot = (*board)[from_i + direction * pawn_movements[3].y_movement][from_j + pawn_movements[3].x_movement];
        if ((colour == 0 && islower(spot)) || (colour == 1 && isupper(spot)))
        {
            moves[move_count] = setMove(from_i, from_j, from_i + direction * pawn_movements[3].y_movement, from_j + pawn_movements[3].x_movement, ' ', spot);
            move_count++;
        }
    }

    // setting the last index of the array equal to null
    moves[move_count] = NULL;
    return moves;
}
char *fen(exboard_t *board, char *active, char *castling, char *enpassant, int half, int full) {
    if (board == NULL || active == NULL || castling == NULL || enpassant == NULL) {
        return NULL;
    }

    char *fenStr = (char *)malloc(71);
    if (fenStr == NULL) {
        return NULL;
    }

    int pos = 0;

    for (int i = TABLE_SIZE - 1; i > -1; i--) {
        int empty = 0;
        for (int j = 0; j < TABLE_SIZE; j++) {
            char piece = board->board[i][j];
            if (piece == ' ') {
                empty++;
            } else {
                if (empty > 0) {
                    pos += sprintf(fenStr + pos, "%d", empty);
                    empty = 0;
                }
                fenStr[pos++] = piece;
            }
        }
        if (empty > 0) {
            pos += sprintf(fenStr + pos, "%d", empty);
        }
        if (i > 0) {
            fenStr[pos++] = '/';
        }
    }

    fenStr[pos++] = ' ';
    if (strcmp(active, "w") == 0 || strcmp(active, "W") == 0) {
        fenStr[pos++] = 'w';
    } else {
        fenStr[pos++] = 'b';
    }

    fenStr[pos++] = ' ';
    if (strlen(castling) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(castling); i++) {
            fenStr[pos++] = castling[i];
        }
    }

    fenStr[pos++] = ' ';
    if (strlen(enpassant) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(enpassant); i++) {
            fenStr[pos++] = enpassant[i];
        }
    }

    fenStr[pos++] = ' ';
    pos += sprintf(fenStr + pos, "%d", half);

    fenStr[pos++] = ' ';
    pos += sprintf(fenStr + pos, "%d", full);

    fenStr[pos++] = '\0';

    return fenStr;
}

exboard_t *boardstring(char *string) {
    if (string == NULL) {
        return NULL;
    }

    if (strlen(string) != 161) {
        return NULL;
    }

    exboard_t *board = (exboard_t *)calloc(1, sizeof(exboard_t));
    if (board == NULL) {
        return NULL;
    }

    int bprison_len = 0;
    for (int i = 0; i < 16; i++) {
        int src_index;
        if (i < 8) {
            src_index = i;
        } else {
            src_index = 9 + (i - 8);
        }

        char c = string[src_index];
        if (c != ' ' && bprison_len < 15) { 
            board->bprison[bprison_len++] = c;
        } else {
            board->bprison[bprison_len] = '\0';
            break;
        }
    }
    board->bprison[15] = '\0'; 

    int bairfield_len = 0;
    for (int i = 0; i < 16; i++) {
        int src_index;
        if (i < 8) {
            src_index = 18 + i;
        } else {
            src_index = 27 + (i - 8);
        }

        char c = string[src_index];
        if (isalnum(c) && bairfield_len < 15) {
            board->bairfield[bairfield_len++] = c;
        } else {
            board->bairfield[bairfield_len++] = ' ';
        }
    }
    board->bairfield[15] = '\0'; 

    for (int row = 7; row >= 0; row--) {
        int base_index;
        switch (row) {
            case 7:
                base_index = 45;
                break;
            case 6:
                base_index = 54;
                break;
            case 5:
                base_index = 63;
                break;
            case 4:
                base_index = 72;
                break;
            case 3:
                base_index = 81;
                break;
            case 2:
                base_index = 90;
                break;
            case 1:
                base_index = 99;
                break;
            case 0:
                base_index = 108;
                break;
            default:
                base_index = 0;
        }

        for (int col = 0; col < TABLE_SIZE; col++) {
            board->board[row][col] = string[base_index + col];
        }
    }

    int wairfield_len = 0;
    for (int i = 0; i < 16; i++) {
        int src_index;
        if (i < 8) {
            src_index = 126 + i;
        } else {
            src_index = 135 + (i - 8);
        }

        char c = string[src_index];
        if (isalnum(c) && wairfield_len < 15) {
            board->wairfield[wairfield_len++] = c;
        } else {
            board->wairfield[wairfield_len++] = ' ';
        }
    }
    board->wairfield[15] = '\0';

    int wprison_len = 0;
    for (int i = 0; i < 16; i++) {
        int src_index;
        if (i < 8) {
            src_index = 144 + i;
        } else {
            src_index = 153 + (i - 8);
        }

        char c = string[src_index];
        if (c != ' ' && wprison_len < 15) {
            board->wprison[wprison_len++] = c;
        } else {
            board->wprison[wprison_len] = '\0';
            break;
        }
    }
    board->wprison[15] = '\0';

    return board;
}
// Finding the colour associated with the character
int findColour(char c)
{
    if (islower(c))
    {
        return 1;
    }
    return 0;
}
// Find the distance between where we currently are and where we are moving to
int calcStep(int move_from, int move_to)
{
    return abs(move_to - move_from);
}
// Basically a constructor for moves
move_t *setMove(int from_i, int from_j, int move_to_i, int move_to_j, char promotion, char hostage)
{
    move_t *move = malloc(sizeof(move_t));

    if (move == NULL)
    {
        return NULL;
    }
    move->from_i = from_i;
    move->from_j = from_j;
    move->to_i = move_to_i;
    move->to_j = move_to_j;
    move->promotion = promotion;
    move->hostage = hostage;

    return move;
}
int digitCount(int number)
{
    int digits = 0;
    if (number == 0)
    {
        return 1;
    }
    while (number > 0)
    {
        digits++;
        number = number / 10;
    }
    return digits;
}

// Function to create an Extended FEN string from exboard_t
char *extended_fen(exboard_t *board, char *active, char *castling, char *enpassant, int half, int full) {
    if (board == NULL || active == NULL || castling == NULL || enpassant == NULL) {
        return NULL;
    }

    // Calculate the maximum length needed
    // Standard FEN: up to 71 characters
    // Additional fields: up to 15 each for bprison, bairfield, wprison, wairfield
    // Plus 4 spaces and null terminator
    int max_length = 136;
    char *fenStr = (char *)malloc(max_length);
    if (fenStr == NULL) {
        return NULL;
    }

    int pos = 0;

    // Serialize the board position (standard FEN part)
    for (int i = TABLE_SIZE - 1; i >= 0; i--) {
        int empty = 0;
        for (int j = 0; j < TABLE_SIZE; j++) {
            char piece = board->board[i][j];
            if (piece == ' ') {
                empty++;
            } else {
                if (empty > 0) {
                    pos += sprintf(fenStr + pos, "%d", empty);
                    empty = 0;
                }
                fenStr[pos++] = piece;
            }
        }
        if (empty > 0) {
            pos += sprintf(fenStr + pos, "%d", empty);
        }
        if (i > 0) {
            fenStr[pos++] = '/';
        }
    }

    // Active color
    fenStr[pos++] = ' ';
    if (strcmp(active, "w") == 0 || strcmp(active, "W") == 0) {
        fenStr[pos++] = 'w';
    } else {
        fenStr[pos++] = 'b';
    }

    // Castling availability
    fenStr[pos++] = ' ';
    if (strlen(castling) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(castling); i++) {
            fenStr[pos++] = castling[i];
        }
    }

    // En passant target square
    fenStr[pos++] = ' ';
    if (strlen(enpassant) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(enpassant); i++) {
            fenStr[pos++] = enpassant[i];
        }
    }

    // Halfmove clock
    fenStr[pos++] = ' ';
    pos += sprintf(fenStr + pos, "%d", half);

    // Fullmove number
    fenStr[pos++] = ' ';
    pos += sprintf(fenStr + pos, "%d", full);

    // Black Prison
    fenStr[pos++] = ' ';
    if (strlen(board->bprison) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(board->bprison); i++) {
            fenStr[pos++] = board->bprison[i];
        }
    }

    // Black Airfield
    fenStr[pos++] = ' ';
    if (strlen(board->bairfield) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(board->bairfield); i++) {
            fenStr[pos++] = board->bairfield[i];
        }
    }

    // White Prison
    fenStr[pos++] = ' ';
    if (strlen(board->wprison) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(board->wprison); i++) {
            fenStr[pos++] = board->wprison[i];
        }
    }

    // White Airfield
    fenStr[pos++] = ' ';
    if (strlen(board->wairfield) == 0) {
        fenStr[pos++] = '-';
    } else {
        for (int i = 0; i < strlen(board->wairfield); i++) {
            fenStr[pos++] = board->wairfield[i];
        }
    }

    // Null terminator
    fenStr[pos++] = '\0';

    return fenStr;
}

exboard_t *extended_boardstring(char *string) {
    if (string == NULL) {
        return NULL;
    }

    // Manually allocate memory for the copy of the string
    size_t string_len = strlen(string);
    char *string_copy = (char *)malloc(string_len + 1);  // +1 for the null terminator
    if (string_copy == NULL) {
        return NULL;
    }
    strcpy(string_copy, string);

    // Tokenize the string by spaces
    char *tokens[10];
    int token_count = 0;
    char *token = strtok(string_copy, " ");
    while (token != NULL && token_count < 10) {
        tokens[token_count++] = token;
        token = strtok(NULL, " ");
    }

    if (token_count != 10) {
        // Invalid EFEN format
        free(string_copy);
        return NULL;
    }

    exboard_t *board = (exboard_t *)calloc(1, sizeof(exboard_t));
    if (board == NULL) {
        free(string_copy);
        return NULL;
    }

    // Parse the board position
    char *position = tokens[0];
    int row = TABLE_SIZE - 1;
    int col = 0;
    size_t pos_len = strlen(position);
    for (size_t i = 0; i < pos_len; i++) {
        char c = position[i];
        if (c == '/') {
            row--;
            col = 0;
            continue;
        }
        if (isdigit((unsigned char)c)) {
            int empty = c - '0';
            for (int j = 0; j < empty; j++) {
                if (col < TABLE_SIZE) {
                    board->board[row][col++] = ' ';
                } else {
                    // Handle error: column out of bounds
                    free(string_copy);
                    free(board);
                    return NULL;
                }
            }
        } else {
            if (col < TABLE_SIZE) {
                board->board[row][col++] = c;
            } else {
                // Handle error: column out of bounds
                free(string_copy);
                free(board);
                return NULL;
            }
        }
    }

    // Black Prison
    if (strcmp(tokens[6], "-") != 0) {
        strncpy(board->bprison, tokens[6], sizeof(board->bprison) - 1);
        board->bprison[sizeof(board->bprison) - 1] = '\0';
    } else {
        board->bprison[0] = '\0';
    }

    // Black Airfield
    if (strcmp(tokens[7], "-") != 0) {
        strncpy(board->bairfield, tokens[7], sizeof(board->bairfield) - 1);
        board->bairfield[sizeof(board->bairfield) - 1] = '\0';
    } else {
        board->bairfield[0] = '\0';
    }

    // White Prison
    if (strcmp(tokens[8], "-") != 0) {
        strncpy(board->wprison, tokens[8], sizeof(board->wprison) - 1);
        board->wprison[sizeof(board->wprison) - 1] = '\0';
    } else {
        board->wprison[0] = '\0';
    }

    // White Airfield
    if (strcmp(tokens[9], "-") != 0) {
        strncpy(board->wairfield, tokens[9], sizeof(board->wairfield) - 1);
        board->wairfield[sizeof(board->wairfield) - 1] = '\0';
    } else {
        board->wairfield[0] = '\0';
    }

    // Free the copied string
    free(string_copy);

    return board;
}
int is_move_valid(exboard_t *board, move_t *move, int current_player_color) {
    char piece = board->board[move->from_i][move->from_j];
    if (piece == ' ') {
        // No piece at the source position
        return 0;
    }
    int piece_color = findColour(piece);
    if (piece_color != current_player_color) {
        // Not the player's own piece
        return 0;
    }

    // Generate possible moves
    move_t **possible_moves = moves(&(board->board), move->from_i, move->from_j);
    if (possible_moves == NULL) {
        return 0;
    }

    int is_valid = 0;
    for (int i = 0; possible_moves[i] != NULL; i++) {
        move_t *possible_move = possible_moves[i];
        printf("Start Move: %d %d\n", move->from_i ,move->from_j);
        printf("Proposed Move: %d %d\n", move->to_i ,move->to_j);
        printf("Possible Start Move: %d %d\n", possible_move->from_i, possible_move->from_j);
        printf("Possible Move: %d %d\n", possible_move->to_i, possible_move->to_j);
        printf("%d\n", possible_move->from_i == move->from_i);
        printf("%d\n", possible_move->from_j == move->from_j);
        printf("%d\n", possible_move->to_i == move->to_i);
        printf("%d\n", possible_move->to_j == move->to_j);
        printf("%d\n", possible_move->promotion == move->promotion);
        printf("%d\n", possible_move->hostage == move->hostage);
        // Compare all relevant fields
        if (possible_move->from_i == move->from_i &&
            possible_move->from_j == move->from_j &&
            possible_move->to_i == move->to_i &&
            possible_move->to_j == move->to_j &&
            possible_move->promotion == move->promotion &&
            possible_move->hostage == move->hostage) {
            is_valid = 1;
            break;
        }
    }

    // Free allocated memory
    for (int i = 0; possible_moves[i] != NULL; i++) {
        free(possible_moves[i]);
    }
    free(possible_moves);

    return is_valid;
}
char get_board_value(exboard_t *board, int i, int j) {
    return board->board[i][j];
}
