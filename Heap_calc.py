# Import modules 
from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber
from qgis.core import QgsProcessingUtils
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import processing

# Defining the Algorithm Class
class VolumeCalculation(QgsProcessingAlgorithm):
    INPUT_DEM = 'INPUT_DEM'
    INPUT_HEAP = 'INPUT_HEAP'
    OUTPUT_CUT = 'OUTPUT_CUT'
    OUTPUT_FILL = 'OUTPUT_FILL'
    OUTPUT_NET = 'OUTPUT_NET'

#Initializing the Algorithm
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_DEM, 'Input DEM', "C:/Users/lenovo/Desktop/heap-dem.tif"))
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT_HEAP, 'Input Heap', "C:/Users/lenovo/Desktop/heap.shp", [QgsProcessingParameterVectorLayer.GeometryType.Polygon]))
        self.addParameter(QgsProcessingParameterNumber(self.OUTPUT_CUT, 'Cut Volume', defaultValue=0, optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.OUTPUT_FILL, 'Fill Volume', defaultValue=0, optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.OUTPUT_NET, 'Net Volume', defaultValue=0, optional=True))

# Proceesing the Algorithm
    def processAlgorithm(self, parameters, context, feedback):
        dem = self.parameterAsRasterLayer(parameters, self.INPUT_DEM, context)
        heap = self.parameterAsVectorLayer(parameters, self.INPUT_HEAP, context)

        # Calculate the volume of the heap
        heap_extent = heap.extent()
        feedback.pushInfo(f"Heap extent: {heap_extent}")

        # Create a mask from the heap
        mask = QgsProcessingUtils.createTemporaryLayer('Polygon', heap)

        # Calculate the cut volume
        cut_volume = self.calculate_volume(dem, mask, feedback, 'cut')
        fill_volume = self.calculate_volume(dem, mask, feedback, 'fill')

        # Calculate net volume
        net_volume = cut_volume - fill_volume

        # Set output values
        self.setOutputValue(parameters, self.OUTPUT_CUT, cut_volume)
        self.setOutputValue(parameters, self.OUTPUT_FILL, fill_volume)
        self.setOutputValue(parameters, self.OUTPUT_NET, net_volume)

        return {self.OUTPUT_CUT: cut_volume, self.OUTPUT_FILL: fill_volume, self.OUTPUT_NET: net_volume}

    def calculate_volume(self, dem, mask, feedback, operation):
        # Create raster calculator entries
        entries = []
        entry = QgsRasterCalculatorEntry()
        entry.ref = 'dem_1'
        entry.raster = dem
        entry.bandNumber = 1
        entries.append(entry)

        # Define the calculation based on operation
        if operation == 'cut':
            expression = 'dem_1 * (1 - mask_1)'
        else:  # fill
            expression = 'mask_1 * dem_1'

        # Perform the calculation
        calc = QgsRasterCalculator(expression, 'TEMPORARY_OUTPUT', 'GTiff', dem.extent(), dem.width(), dem.height(), entries)
        result = calc.processCalculation()

        # Calculate the volume
        volume = processing.run("native:polygonstolines", {'INPUT': result, 'OUTPUT': 'TEMPORARY_OUTPUT'})
        return volume
# Setting Output Values Method

    def setOutputValue(self, parameters, output_param, value):
        self.setParameterValue(parameters, output_param, value)
# Metadata 

    def name(self):
        return 'Volume Calculation'

    def displayName(self):
        return 'Cut, Fill, and Net Volume Calculation'

    def createInstance(self):
        return VolumeCalculation()