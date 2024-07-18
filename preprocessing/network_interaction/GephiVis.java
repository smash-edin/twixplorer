import org.gephi.filters.api.FilterController;
import org.gephi.filters.api.Query;
import org.gephi.filters.plugin.graph.GiantComponentBuilder.GiantComponentFilter;
import org.gephi.graph.api.*;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.exporter.plugin.ExporterJson;
import org.gephi.io.exporter.preview.PNGExporter;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDirectionDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.AutoLayout;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.statistics.plugin.Modularity;
import org.openide.util.Lookup;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class GephiVis {

    public static float[][] getPositions(DirectedGraph graph) {
        Node[] nodes = graph.getNodes().toArray();
        int nbNodes = nodes.length;
        float[][] positions = new float[nbNodes][2];
        for (int index = 0; index < nbNodes; index++) {
            positions[index][0] = nodes[index].x();
            positions[index][1] = nodes[index].y();
        }
        return positions;
    }
    public static double calculateDisplacement(float[][] previousPositions, float[][] newPositions) {
        double displacementSum = 0.0;
        int nodeCount = previousPositions.length;
        for (int i = 0; i < previousPositions.length; i++) {
            float x = newPositions[i][0];
            float y = newPositions[i][1];
            float previousX = previousPositions[i][0];
            float previousY = previousPositions[i][1];
            double displacement = Math.sqrt(Math.pow(x - previousX, 2) + Math.pow(y - previousY, 2));
            displacementSum += displacement;
        }
        return displacementSum / nodeCount;
    }

    public void script(int duration, String sourceFile) throws FileNotFoundException {

        // Define outfile names
        String outFile = sourceFile.replace(".csv", "_GRAPH.json");
        String imgFile = sourceFile.replace(".csv", ".png");

        // Initialise project
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        //Get models and controllers for this new workspace - will be useful later
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel();
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        PNGExporter pngExporter = (PNGExporter) ec.getExporter("png");

        Container container;
        System.out.println("Loading data...");
        try {
            File file = new File(getClass().getResource(sourceFile).toURI());
            container = importController.importFile(file);
            container.getLoader().setEdgeDefault(EdgeDirectionDefault.DIRECTED);   //Force DIRECTED
        } catch (Exception ex) {
            ex.printStackTrace();
            return;
        }

        //Append imported data to GraphAPI
        importController.process(container, new DefaultProcessor(), workspace);

        //See if graph is well imported
        DirectedGraph graph = graphModel.getDirectedGraphVisible();
        int nbNodes = graph.getNodeCount();
        int nbEdges = graph.getEdgeCount();
        System.out.println("Nb nodes: " + nbNodes);
        System.out.println("Nb edges: " + nbEdges);

        // Preview
        PreviewModel previewModel = Lookup.getDefault().lookup(PreviewController.class).getModel();
        previewModel.getProperties().putValue(PreviewProperty.SHOW_EDGES, Boolean.FALSE);

        // Filter out nodes
        System.out.println("Filtering out nodes that are not in Giant Component");
        FilterController filterController = Lookup.getDefault().lookup(FilterController.class);
        GiantComponentFilter giantComponentFiler = new GiantComponentFilter();
        giantComponentFiler.init(graph);
        Query query = filterController.createQuery(giantComponentFiler);
        GraphView view = filterController.filter(query);
        graphModel.setVisibleView(view);

        graph = graphModel.getDirectedGraphVisible();
        nbNodes = graph.getNodeCount();
        nbEdges = graph.getEdgeCount();
        System.out.println("New nb nodes: " + nbNodes);
        System.out.println("New nb edges: " + nbEdges);

        //Layout
        System.out.println("Running layout algorithm...");
        float[][] initialPositions = getPositions(graph);
        AutoLayout autoLayout = new AutoLayout(duration, TimeUnit.MINUTES);
        autoLayout.setGraphModel(graphModel);
        ForceAtlas2 layout = new ForceAtlas2(null);
        if (nbNodes > 10000) {
            layout.setBarnesHutOptimize(Boolean.TRUE);
        }
        layout.setLinLogMode(Boolean.TRUE);
        AutoLayout.DynamicProperty adjustBySizeProperty = AutoLayout.createDynamicProperty("forceAtlas2.adjustSizes.name", Boolean.TRUE, 0.1f);
        autoLayout.addLayout(layout, 1f, new AutoLayout.DynamicProperty[]{adjustBySizeProperty});
        autoLayout.execute();
        float[][] newPositions = getPositions(graph);
        double displacement = calculateDisplacement(initialPositions, newPositions);
        System.out.println("Observed displacement: " + displacement);

        //Run modularity algorithm - community detection
        System.out.println("Running modularity class...");
        Modularity modularity = new Modularity();
        modularity.execute(graphModel);



        //Export only visible graph
        ExporterJson exporter = (ExporterJson) ec.getExporter("json");     //Get JSON exporter
        exporter.setExportVisible(true);  //Only exports the visible (filtered) graph
        exporter.setWorkspace(workspace);
        try {
            ec.exportFile(new File(outFile), exporter);
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        System.out.println("DONE!");
    }
}
