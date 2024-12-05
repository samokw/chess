#ifndef HCLIB_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#define TABLE_SIZE 8
typedef char board_t[8][8];

typedef struct
{
    char bprison[16];
    char bairfield[16];
    board_t board;
    char wprison[16];
    char wairfield[16];
} exboard_t;
typedef struct
{
    int from_i, from_j;
    int to_i, to_j;
    char promotion;
    char hostage;
} move_t;
typedef struct
{
    int x_movement;
    int y_movement;
} movement;

exboard_t *newboard(void);
exboard_t *copyboard(exboard_t *board);
char *stringboard(exboard_t *board);
exboard_t *apply_move(exboard_t *board, move_t *move);
move_t **moves(board_t *board, int from_i, int from_j);
move_t **knightmoves(board_t *board, int from_i, int from_j, int colour);
move_t **bishopmoves(board_t *board_t, int from_i, int from_j, int colour);
move_t **rookmoves(board_t *board_t, int from_i, int from_j, int colour);
move_t **queenmoves(board_t *board_t, int from_i, int from_j, int colour);
move_t **king_moves(board_t *board_t, int from_i, int from_j, int colour);
move_t **pawn_moves(board_t *board, int from_i, int from_j, int colour);
char *fen(exboard_t *board, char *active, char *castling, char *enpassant,int half, int full );
char *extended_fen(exboard_t *board, char *active, char *castling, char *enpassant, int half, int full);
exboard_t *boardstring(char *string);
exboard_t *extended_boardstring(char *string);
int is_move_valid(exboard_t *board, move_t *move, int current_player_color);
// Helper Functions
int digitCount(int number);
int findColour(char c);
int calcStep(int move_from, int move_to);
move_t *setMove(int from_i, int from_j, int move_to_i, int move_to_j, char promotion, char hostage);
char get_board_value(exboard_t *board, int i, int j);

#endif
