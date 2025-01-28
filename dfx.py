import ezdxf
import pandas as pd
from fpdf import FPDF
from math import sqrt, pi
import os

# Utility function to calculate 2D distance between points
def calculate_distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    if point1 is None or point2 is None:
        return 0
    return sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
# Utility function to calculate the volume of 3D solids (simple method for now)
def calculate_volume(points):
    """Calculate the volume of a 3D solid from its vertices (simplified for polygons)."""
    # Placeholder for volume calculation.
    if len(points) < 3:
        return 0
    base_area = 0  # Simplified: calculate area from points
    height = points[0][2] if len(points[0]) > 2 else 0
    return base_area * height
# Utility function to calculate the area of a polygon using the Shoelace formula
def calculate_polygon_area(vertices):
    """Calculate the area of a polygon using the Shoelace formula."""
    if len(vertices) < 3:  # Not a valid polygon
        return 0
    n = len(vertices)
    area = 0
    for i in range(n):
        x1, y1 = vertices[i][0], vertices[i][1]
        x2, y2 = vertices[(i + 1) % n][0], vertices[(i + 1) % n][1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2
# Input Module: Validate DXF file
def validate_dxf(file_path):
    """Validate the DXF file format."""
    try:
        doc = ezdxf.readfile(file_path)
        print(f"Validated DXF file: {file_path}")
        return doc
    except IOError:
        print(f"Error: Cannot open file {file_path}.")
        return None
    except ezdxf.DXFStructureError as e:
        print(f"Error: Invalid DXF file structure. {e}")
        return None
# Data Extraction Module: Extract entities and organize by type and layer
def extract_entities(doc):
    """Extract DXF entities and organize them by type and layer."""
    msp = doc.modelspace()
    entities = []
    for entity in msp:
        if entity.dxftype() in ["LINE", "CIRCLE", "LWPOLYLINE", "ARC", "3DSOLID", "POLYFACE"]:
            data = {
                "type": entity.dxftype(),
                "layer": entity.dxf.layer,
                "start_point": getattr(entity.dxf, 'start', None),
                "end_point": getattr(entity.dxf, 'end', None),
                "radius": getattr(entity.dxf, 'radius', None),
                "vertices": [list(vertex) for vertex in getattr(entity, 'vertices', [])],  # For LWPOLYLINE
                "is_closed": getattr(entity, 'closed', False),  # For LWPOLYLINE
                "points": getattr(entity.dxf, 'points', None)  # For 3D solids
            }
            entities.append(data)
    return entities
# Calculation Module: Calculate quantities (lengths, areas, volumes)
def calculate_quantities(entities):
    """Calculate lengths, areas, and volumes from extracted entities."""
    results = []
    for entity in entities:
        if entity["type"] == "LINE":
            length = calculate_distance(entity["start_point"], entity["end_point"])
            results.append({"type": "LINE", "layer": entity["layer"], "length": length, "area": None, "volume": None})
        elif entity["type"] == "CIRCLE":
            area = pi * (entity["radius"]**2)
            results.append({"type": "CIRCLE", "layer": entity["layer"], "length": None, "area": area, "volume": None})
        elif entity["type"] == "LWPOLYLINE" and entity["vertices"]:
            if entity["is_closed"]:
                area = calculate_polygon_area(entity["vertices"])
                results.append({"type": "LWPOLYLINE", "layer": entity["layer"], "length": None, "area": area, "volume": None})
            else:
                results.append({"type": "LWPOLYLINE", "layer": entity["layer"], "length": None, "area": None, "volume": None})
        elif entity["type"] == "3DSOLID" and entity["points"]:
            volume = calculate_volume(entity["points"])
            results.append({"type": "3DSOLID", "layer": entity["layer"], "length": None, "area": None, "volume": volume})
        elif entity["type"] == "POLYFACE" and entity["points"]:
            volume = calculate_volume(entity["points"])
            results.append({"type": "POLYFACE", "layer": entity["layer"], "length": None, "area": None, "volume": volume})
    return results
# Reporting Module: Generate CSV and PDF reports
def generate_csv_report(data, output_path):
    """Generate a CSV report."""
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"CSV report generated at {output_path}")
def generate_pdf_report(data, output_path):
    """Generate a PDF report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="DXF Quantity Analysis Report", ln=True, align='C')
    pdf.ln(10)
    for item in data:
        pdf.cell(0, 10, txt=str(item), ln=True)
    pdf.output(output_path)
    print(f"PDF report generated at {output_path}")
# Error Handling Module
def handle_errors(errors):
    """Log errors to a file."""
    with open("error_log.txt", "w") as log:
        for error in errors:
            log.write(f"{error}\n")
    print("Errors logged in error_log.txt")
# Main Workflow: Process DXF file and generate reports
def process_dxf(file_path, output_dir):
    errors = []
    # Step 1: Validate DXF
    doc = validate_dxf(file_path)
    if not doc:
        errors.append(f"Invalid or unreadable DXF file: {file_path}")
        handle_errors(errors)
        return
    # Step 2: Extract Entities
    entities = extract_entities(doc)
    if not entities:
        print("No entities found in the DXF file.")
        return
    # Step 3: Calculate Quantities
    quantities = calculate_quantities(entities)
    if not quantities:
        print("No measurable entities found in the DXF file.")
        return
    # Step 4: Generate Reports
    csv_path = os.path.join(output_dir, "quantities_report.csv")
    pdf_path = os.path.join(output_dir, "quantities_report.pdf")
    generate_csv_report(quantities, csv_path)
    generate_pdf_report(quantities, pdf_path)
    print("Processing complete. Reports are ready.")
# Example Usage
if __name__ == "__main__":
    dxf_path = "C:/Users/Arkadeep Pramanik/Downloads/diamond.dxf" # Replace with your DXF file path
    output_directory = "output"  # Replace with your desired output directory
    os.makedirs(output_directory, exist_ok=True)
    process_dxf(dxf_path, output_directory)
