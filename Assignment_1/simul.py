import sys
import os
import vtk

# Checking if the user entered the correct number of arguments
if len(sys.argv) != 2:
    print("You must provide an isovalue along when running the program.\nFor example: python simul.py 100") # Relevant message to the user
    sys.exit(1) # Exit the program with a non-zero status to indicate an error

# Extracting the isovalue from the command line argument and converting it to a float
iso = float(sys.argv[1])

# Loading the VTI file using VTK's XML image data reader. 
# The file is expected to be in a "Data" subdirectory relative to the script's location. 
# If the file is not found, a FileNotFoundError is raised
reader = vtk.vtkXMLImageDataReader()
here = os.path.dirname(__file__)
file_path = os.path.join(here, "Data", "Isabel_2D.vti")
if not os.path.exists(file_path):
	raise FileNotFoundError(f"Data file not found: {file_path}")
reader.SetFileName(file_path)
reader.Update()

# Get the output of the reader, which is a vtkImageData object containing the loaded data from the VTI file
data = reader.GetOutput()

# Accessing the scalar data associated with the points in the dataset.
# The scalars are typically used for visualization and analysis, and
# they represent the value of the pressure at each point in the dataset.
scalars = data.GetPointData().GetScalars() 
points = vtk.vtkPoints()
lines = vtk.vtkCellArray()

nx, ny, nz = data.GetDimensions()


for j in range(ny-1):
    for i in range(nx-1):
        p0 = j*nx + i
        p1 = j*nx + (i+1)
        p2 = (j+1)*nx + (i+1)
        p3 = (j+1)*nx + i

        s0 = scalars.GetTuple1(p0)
        s1 = scalars.GetTuple1(p1)
        s2 = scalars.GetTuple1(p2)
        s3 = scalars.GetTuple1(p3)

        edges = [
            (p0, p1, s0, s1),  # Bottom
            (p1, p2, s1, s2),  # Right
            (p2, p3, s2, s3),  # Top
            (p3, p0, s3, s0)   # Left
        ]

        intersections = []

        for a, b, sa, sb in edges:

            # Checking if contour crosses this edge
            if (sa - iso) * (sb - iso) < 0:

                x0, y0, z0 = data.GetPoint(a)
                x1, y1, z1 = data.GetPoint(b)

                t = (iso - sa) / (sb - sa)

                x = x0 + t * (x1 - x0)
                y = y0 + t * (y1 - y0)
                z = z0 + t * (z1 - z0)

                intersections.append((x, y, z))

                if len(intersections) == 2:

                    id0 = points.InsertNextPoint(intersections[0])
                    id1 = points.InsertNextPoint(intersections[1])

                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, id0)
                    line.GetPointIds().SetId(1, id1)

                    lines.InsertNextCell(line)
                elif len(intersections) == 4:

                    pairs = [(0,1), (2,3)]

                    for a,b in pairs:

                        id0 = points.InsertNextPoint(intersections[a])
                        id1 = points.InsertNextPoint(intersections[b])

                        line = vtk.vtkLine()
                        line.GetPointIds().SetId(0, id0)
                        line.GetPointIds().SetId(1, id1)

                        lines.InsertNextCell(line)

poly = vtk.vtkPolyData()
poly.SetPoints(points)
poly.SetLines(lines)

writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(f"contour_{iso}.vtp")
writer.SetInputData(poly)
writer.Write()

print("Saved contour")

                
            
                
