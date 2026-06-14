import os
import sys
import vtk

# 1. Parse command-line arguments as requested by the assignment profile
if len(sys.argv) < 2:
    print("Error: Missing argument.")
    print("Usage: python volume_render.py <yes/no>")
    sys.exit(1)

use_phong = sys.argv[1].strip().lower()
if use_phong not in ["yes", "no"]:
    print("Error: Invalid argument. Use 'yes' or 'no'.")
    sys.exit(1)

# 2.look inside the "Data" subfolder
here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, "Data", "Isabel_3D.vti")

# 3. Read Data
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(filename)
reader.Update()

# 4. Transfer Functions
colorTF = vtk.vtkColorTransferFunction()
colorTF.AddRGBPoint(-4931.54, 0, 1, 1)
colorTF.AddRGBPoint(-2508.95, 0, 0, 1)
colorTF.AddRGBPoint(-1873.90, 0, 0, 0.5)
colorTF.AddRGBPoint(-1027.16, 1, 0, 0)
colorTF.AddRGBPoint(-298.031, 1, 0.4, 0)
colorTF.AddRGBPoint(2594.97, 1, 1, 0)

opacityTF = vtk.vtkPiecewiseFunction()
opacityTF.AddPoint(-4931.54, 1.0)
opacityTF.AddPoint(101.815, 0.002)
opacityTF.AddPoint(2594.97, 0.0)

# 5. Mapper
mapper = vtk.vtkSmartVolumeMapper()
mapper.SetInputConnection(reader.GetOutputPort())

# 6. Volume Property
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTF)
volumeProperty.SetScalarOpacity(opacityTF)
volumeProperty.SetInterpolationTypeToLinear()

if use_phong == "yes":
    volumeProperty.ShadeOn()
    volumeProperty.SetAmbient(0.5)
    volumeProperty.SetDiffuse(0.5)
    volumeProperty.SetSpecular(0.5)
    front_name = "front_with_phong.png"
    back_name = "back_with_phong.png"
else:
    volumeProperty.ShadeOff()
    front_name = "front_without_phong.png"
    back_name = "back_without_phong.png"

# 7. Volume
volume = vtk.vtkVolume()
volume.SetMapper(mapper)
volume.SetProperty(volumeProperty)

# 8. Outline
outline = vtk.vtkOutlineFilter()
outline.SetInputConnection(reader.GetOutputPort())
outlineMapper = vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection(outline.GetOutputPort())
outlineActor = vtk.vtkActor()
outlineActor.SetMapper(outlineMapper)
outlineActor.GetProperty().SetColor(0, 0, 0)
outlineActor.GetProperty().SetLineWidth(2)

# 9. Renderer
renderer = vtk.vtkRenderer()
renderer.AddVolume(volume)
renderer.AddActor(outlineActor)
renderer.SetBackground(0.96, 0.93, 0.85)

# 10. Window
renderWindow = vtk.vtkRenderWindow()
renderWindow.SetOffScreenRendering(1)
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(1000, 1000)


# 11. Save Function
def save_png(name):
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renderWindow)
    w2if.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(name)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()


# BACK VIEW
renderer.ResetCamera()
renderWindow.Render()
save_png(back_name)

# FRONT VIEW (after 180° rotation)
camera = renderer.GetActiveCamera()
camera.Azimuth(180)
renderer.ResetCameraClippingRange()
renderWindow.Render()
save_png(front_name)

# Output
print("\nFRONT VIEW SAVED AS:")
print(front_name)
print("\nBACK VIEW SAVED AS:")
print(back_name)