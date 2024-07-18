import java.io.FileNotFoundException;

public class Main {
    public static void main(String[] args) throws FileNotFoundException {
        GephiVis gephiVis = new GephiVis();
        System.out.println("Layout duration: " + args[0]);
        System.out.println("Input file: " + args[1]);
        gephiVis.script(Integer.valueOf(args[0]), args[1]);
        System.exit(0);
    }
}