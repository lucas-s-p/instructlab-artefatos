public void resetBoard()
{
for (int column = 0; column < 8; column++) {
    if (column == 0) {
        _chessBoard.getBoard()[7][column].setPiece(new LeftRook(Color.WHITE));
    } else if (column == 1) {
        _chessBoard.getBoard()[7][column].setPiece(new LeftKnight(Color.WHITE));
    } else if (column == 2) {
        _chessBoard.getBoard()[7][column].setPiece(new LeftBishop(Color.WHITE));
    } else if (column == 3) {
        _chessBoard.getBoard()[7][column].setPiece(new King(Color.WHITE));
    } else if (column == 4) {
        _chessBoard.getBoard()[7][column].setPiece(new Queen(Color.WHITE));
    } else if (column == 5) {
        _chessBoard.getBoard()[7][column].setPiece(new RightBishop(Color.WHITE));
    } else if (column == 6) {
        _chessBoard.getBoard()[7][column].setPiece(new RightKnight(Color.WHITE));
    } else if (column == 7) {
        _chessBoard.getBoard()[7][column].setPiece(new RightRook(Color.WHITE));
    }
}
for (int column = 0; column < 8; column++) {
    _chessBoard.getBoard()[6][column].setPiece(new Pawn(Color.WHITE));
}
for (int column = 0; column < 8; column++) {
    if (column == 0) {
        _chessBoard.getBoard()[0][column].setPiece(new LeftRook(Color.BLACK));
    } else if (column == 1) {
        _chessBoard.getBoard()[0][column].setPiece(new LeftKnight(Color.BLACK));
    } else if (column == 2) {
        _chessBoard.getBoard()[0][column].setPiece(new LeftBishop(Color.BLACK));
    } else if (column == 3) {
        _chessBoard.getBoard()[0][column].setPiece(new King(Color.BLACK));
    } else if (column == 4) {
        _chessBoard.getBoard()[0][column].setPiece(new Queen(Color.BLACK));
    } else if (column == 5) {
        _chessBoard.getBoard()[0][column].setPiece(new RightBishop(Color.BLACK));
    } else if (column == 6) {
        _chessBoard.getBoard()[0][column].setPiece(new RightKnight(Color.BLACK));
    } else if (column == 7) {
        _chessBoard.getBoard()[0][column].setPiece(new RightRook(Color.BLACK));
    }
}
for (int column = 0; column < 8; column++) {
    _chessBoard.getBoard()[1][column].setPiece(new Pawn(Color.BLACK));
}
_chessBoard._kingDead = false;
}