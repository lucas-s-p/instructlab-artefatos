// receive() CC = 2 (for + if) — lógica de rotação e deslocamento extraída
// via enum Direction com comportamento embutido
public class Rover {

    private Direction direction;
    private int y;
    private int x;

    public Rover(int x, int y, String dir) {
        this.direction = Direction.valueOf(dir);
        this.y = y;
        this.x = x;
    }

    public void receive(String commandsSequence) {
        for (int i = 0; i < commandsSequence.length(); ++i) {
            String command = commandsSequence.substring(i, i + 1);
            if (command.equals("l") || command.equals("r")) {
                direction = direction.rotate(command);
            } else {
                int displacement = command.equals("f") ? 1 : -1;
                x += direction.dx() * displacement;
                y += direction.dy() * displacement;
            }
        }
    }

    enum Direction {
        N { @Override Direction rotateRight() { return E; } @Override Direction rotateLeft() { return W; } @Override int dx() { return 0; } @Override int dy() { return 1; } },
        S { @Override Direction rotateRight() { return W; } @Override Direction rotateLeft() { return E; } @Override int dx() { return 0; } @Override int dy() { return -1; } },
        E { @Override Direction rotateRight() { return S; } @Override Direction rotateLeft() { return N; } @Override int dx() { return 1; } @Override int dy() { return 0; } },
        W { @Override Direction rotateRight() { return N; } @Override Direction rotateLeft() { return S; } @Override int dx() { return -1; } @Override int dy() { return 0; } };

        abstract Direction rotateRight();
        abstract Direction rotateLeft();
        abstract int dx();
        abstract int dy();

        Direction rotate(String command) {
            return command.equals("r") ? rotateRight() : rotateLeft();
        }
    }
}
