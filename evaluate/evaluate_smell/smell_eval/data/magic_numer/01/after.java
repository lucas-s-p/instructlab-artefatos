public class ChessBoard {
    private static final int BOARD_SIZE    = 8;
    private static final int BACK_RANK_BLACK = 0;
    private static final int BACK_RANK_WHITE = 7;
    private static final int ROOK_LEFT    = 0;
    private static final int KNIGHT_LEFT  = 1;
    private static final int BISHOP_LEFT  = 2;
    private static final int QUEEN_COL    = 3;
    private static final int KING_COL     = 4;
    private static final int BISHOP_RIGHT = 5;
    private static final int KNIGHT_RIGHT = 6;
    private static final int ROOK_RIGHT   = BOARD_SIZE - 1;

    public void setupBackRank(int row, Color color)
    {
        if (row == BACK_RANK_BLACK || row == BACK_RANK_WHITE) {
            placePiece(row, ROOK_LEFT,    new Rook(color));
            placePiece(row, ROOK_RIGHT,   new Rook(color));
            placePiece(row, KNIGHT_LEFT,  new Knight(color));
            placePiece(row, KNIGHT_RIGHT, new Knight(color));
            placePiece(row, BISHOP_LEFT,  new Bishop(color));
            placePiece(row, BISHOP_RIGHT, new Bishop(color));
            placePiece(row, QUEEN_COL,    new Queen(color));
            placePiece(row, KING_COL,     new King(color));
        }
    }
}