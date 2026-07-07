public class ChessBoard
{
    private String getPlayerName(Position pos) {
        return pos.toString();
    }

    private Object getPiece(Position pos) {
        return null;
    }

    private void printMove(Position from, Position to)
    {
        System.out.println(getPlayerName(from) + " moved " + getPiece(from)
            + " from " + from + " to " + to);
        if (getPiece(from) != null) {
            System.out.println("Captured piece at " + to);
        }
    }

    public void movePiece(Position from, Position to) {
        // move logic — printMove nunca é chamado aqui
    }
}