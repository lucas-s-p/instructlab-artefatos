public abstract class Piece
{
    public abstract boolean isValidMove(Position from, Position to);
}

public class Knight extends Piece
{
    @Override
    public boolean isValidMove(Position from, Position to)
    {
        int columnDiff = Math.abs(to.getColumn() - from.getColumn());
        int rowDiff    = Math.abs(to.getRow() - from.getRow());
        return (columnDiff == 2 && rowDiff == 1)
                || (columnDiff == 1 && rowDiff == 2);
    }
}

public class King extends Piece
{
    @Override
    public boolean isValidMove(Position from, Position to)
    {
        return (Math.abs(from.getRow() - to.getRow()) == 1)
                && (Math.abs(from.getColumn() - to.getColumn()) == 1);
    }
}

public class Bishop extends Piece
{
    @Override
    public boolean isValidMove(Position from, Position to)
    {
        return Math.abs(from.getRow() - to.getRow())
                == Math.abs(from.getColumn() - to.getColumn());
    }
}

public class Rook extends Piece
{
    @Override
    public boolean isValidMove(Position from, Position to)
    {
        return from.getRow() == to.getRow()
                || from.getColumn() == to.getColumn();
    }
}

public class Queen extends Piece
{
    @Override
    public boolean isValidMove(Position from, Position to)
    {
        return Math.abs(from.getRow() - to.getRow())
                    == Math.abs(from.getColumn() - to.getColumn())
                || from.getRow() == to.getRow()
                || from.getColumn() == to.getColumn();
    }
}