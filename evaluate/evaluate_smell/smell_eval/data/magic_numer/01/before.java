public class ChessBoard {
    public void setupBackRank(int row, Color color)
    {
        if (row == 0 || row == 7) {
            placePiece(row, 0, new Rook(color));
            placePiece(row, 7, new Rook(color));
        }
        if (row == 0 || row == 7) {
            placePiece(row, 1, new Knight(color));
            placePiece(row, 6, new Knight(color));
        }
        if (row == 0 || row == 7) {
            placePiece(row, 2, new Bishop(color));
            placePiece(row, 5, new Bishop(color));
        }
        if (row == 0 || row == 7) {
            placePiece(row, 3, new Queen(color));
            placePiece(row, 4, new King(color));
        }
    }
}