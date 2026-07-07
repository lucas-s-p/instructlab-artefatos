public boolean isValidMove(int fromRow, int fromColumn, int toRow, int toColumn)
{
    Position from = new Position(fromRow, fromColumn);
    Position to = new Position(toRow, toColumn);
    return !from.equals(to)
            && !(isPositionOutOfBounds(from) || isPositionOutOfBounds(to))
            && !isEmpty(from)
            && (isEmpty(to) || getPiece(from).getColor() != getPiece(to).getColor())
            && getPiece(from).isValidMove(from, to)
            && hasNoPieceInPath(from, to)
            && (!(getPiece(from) instanceof Pawn) || isValidPawnMove(from, to));
}

public void movePiece(int fromRow, int fromColumn, int toRow, int toColumn)
{
    Position from = new Position(fromRow, fromColumn);
    Position to = new Position(toRow, toColumn);
    updateIsKingDead(toRow, toColumn);
    if (!getCell(to).isEmpty())
        getCell(to).removePiece();
    getCell(to).setPiece(getPiece(from));
    getCell(from).removePiece();
}