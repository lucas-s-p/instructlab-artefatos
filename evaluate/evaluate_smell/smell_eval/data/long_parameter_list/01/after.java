public boolean isValidMove(Position from, Position to)
{
    return !from.equals(to)
            && !(isPositionOutOfBounds(from) || isPositionOutOfBounds(to))
            && !isEmpty(from)
            && (isEmpty(to) || getPiece(from).getColor() != getPiece(to).getColor())
            && getPiece(from).isValidMove(from, to)
            && hasNoPieceInPath(from, to)
            && (!(getPiece(from) instanceof Pawn) || isValidPawnMove(from, to));
}

public void movePiece(Position from, Position to)
{
    updateIsKingDead(to);
    if (!getCell(to).isEmpty())
        getCell(to).removePiece();
    getCell(to).setPiece(getPiece(from));
    getCell(from).removePiece();
}