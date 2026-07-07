public void resetBoard()
{
    placePieces(Color.WHITE);
    placePieces(Color.BLACK);
    _kingDead = false;
}

private void placePieces(Color color)
{
    int pawnsRow, otherPiecesRow;
    switch (color) {
        case WHITE: pawnsRow = BOARD_SIZE - 2; otherPiecesRow = BOARD_SIZE - 1; break;
        case BLACK: pawnsRow = 1; otherPiecesRow = 0; break;
        default: return;
    }
    placeOtherPieces(otherPiecesRow, color);
    placePawns(pawnsRow, color);
}

private void placePawns(int row, Color color)
{
    for (int column = 0; column < BOARD_SIZE; column++) {
        _board[row][column].setPiece(new Pawn(color));
    }
}

private void placeOtherPieces(int row, Color color)
{
    for (int column = 0; column < BOARD_SIZE; column++) {
        Piece piece = null;
        if (column == 0 || column == BOARD_SIZE - 1)      piece = new Rook(color);
        else if (column == 1 || column == BOARD_SIZE - 2) piece = new Knight(color);
        else if (column == 2 || column == BOARD_SIZE - 3) piece = new Bishop(color);
        else if (column == 3)                             piece = new King(color);
        else if (column == 4)                             piece = new Queen(color);
        _board[row][column].setPiece(piece);
    }
}