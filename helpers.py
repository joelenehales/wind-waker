# Helper functions used across multiple modules.
# Author:  Joelene Hales

import os
import struct
import numpy as np
import warnings


def matrix_to_array(matrix, dimensions):
    """ Converts a square matrix to an array. 
    
    Parameters
    ----------
    matrix : glm.mat4
        Matrix to convert to an array
    dimensions : int
        Number of rows and columns in the square matrix.

    Returns
    -------
    matrix_array : np.ndarray
        Matrix converted to an array.
    
    """
    
    matrix_array = np.array([matrix[i][j] for i in range(dimensions) for j in range(dimensions)])

    return matrix_array


def clamp(number, a, b):
    """ Clamps a number within the range [a, b]. 
    
    Parameters
    ----------
    number : float
        Matrix to convert to an array
    a : int
        Minimum of range (inclusive).
    b : int
        Maximum of range (inclusive).

    Returns
    -------
    clamped_number : float
        Number clamped within the range [a, b].
    
    """

    clamped_number = max(min(number, max(a, b)), min(a, b))

    return clamped_number


def read_bitmap(filename):
    """ Reads a bitmap image file.

    Parameters
    ----------
    filename : str
        Filepath to the bitmap image file to read.

    Returns
    -------
    bitmap_image : array[float]
        Bitmap image
    width : int
        Width of image, in bytes
    height : int
        Height of image, in bytes

    """

    # Get filepath to file
    directory = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(directory, filename)

    with open(filepath, 'rb') as bmp:  # Open file

        # Unpack all header data
        type = bmp.read(2).decode()                              # Type of image file
        image_size = struct.unpack('I', bmp.read(4))[0]          # Filesize in bytes
        struct.unpack('xxxxxxxx', bmp.read(8))                   # Skip 8 bytes
        header_size = struct.unpack('I', bmp.read(4))[0]         # Header size, in bytes
        width = struct.unpack('I', bmp.read(4))[0]               # Image width, in bytes
        height = struct.unpack('I', bmp.read(4))[0]              # Image height, in bytes
        struct.unpack('xx', bmp.read(2))                         # Skip 2 bytes
        bits_per_pixel = struct.unpack('H', bmp.read(2))[0]      # Bits per pixel
        struct.unpack('xxxxxxxxxxxxxxxxxxxxxxxx', bmp.read(24))  # Skip 24 bytes

        # Error handling
        if (type != "BM"):  # Bitmap image files always begin with "BM"
            raise ValueError("Incorrect file format. Must be a .bmp file.")

        if (image_size == 0):  # Misformatted image size
            image_size = width * height * 4   # x4 for each channel (R, G, B, A)

        # Read image data
        image_data = []
        for byte in range(image_size):
            image_data.append(int.from_bytes(bmp.read(1)))  # Read one byte

    return image_data, width, height


def read_ply(filename):
    """ Reads a PLY file.

    Parameters
    ----------
    filename : str
        Filepath to a PLY file.

    Returns
    -------
    positions : np.ndarray, dtype=np.float32
        Vertex positions
    normals : np.ndarray, dtype=np.float32
        Vertex normals
    colors : np.ndarray, dtype=np.uint32
        Vertex colors
    texture_coords : np.ndarray, dtype=np.float32
        Vertex texture coordinates
    indices : np.ndarray, dtype=np.uint32
        Indices of each face in the mesh.

    """

    # Get filepath to file
    directory = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(directory, filename)

    with open(filepath, "r") as file:

        # Read formatting and comments
        filetype = file.readline().strip("\n")
        format = file.readline().strip("\n")
        comment = file.readline().strip("\n")

        # Read number of vertices
        line = file.readline().strip().split(" ")
        num_vertices = int(line[2])

        # Create empty arrays to store each vertex's attributes
        vertex_data = {"x" : np.empty(num_vertices),
                       "y" : np.empty(num_vertices),
                       "z" : np.empty(num_vertices),
                       "nx" : np.empty(num_vertices),
                       "ny" : np.empty(num_vertices),
                       "nz" : np.empty(num_vertices),
                       "r" : np.empty(num_vertices),
                       "g" : np.empty(num_vertices),
                       "b" : np.empty(num_vertices),
                       "u" : np.empty(num_vertices),
                       "v" : np.empty(num_vertices)}

        # Determine which value in each vertex data line corresponds to each attribute
        attribute_indices = {}  # Stores each index in the line and the attribute it corresponds to
        line_num = 0  # Used to iterate until the end of the vertex property information
        while (line_num < len(vertex_data)): 

            line = file.readline().strip().split()  # Split the line's data into components

            if (line[0] == "element"):  # Beginning of triangle face properties begin
                break
            else:
                # Store the current position and its corresponding attribute
                attribute_indices[line_num] = line[2]
                line_num += 1

        # Read number of faces
        num_faces = int(line[2])

        # Skip format of triangle faces and end of header
        next(file)
        next(file)

        # Read vertex data from file
        for index in range(num_vertices):  # Iterate over each vertex

            vertex = file.readline().strip().split(" ")  # Split the line's data into components

            for i in range(len(vertex)):  # Iterate over each attribute

                attribute = attribute_indices[i]  # Lookup which attribute the value in this position corrresponds to
                vertex_data[attribute][index] = float(vertex[i])  # Add attribute to correct list


        # Read triangle face indices from file
        indices = []
        for line in range(num_faces):  # Repeat until all faces have been read

            # Read indices from file
            face = file.readline().strip().split(" ")   # Split line to separate indices
            indices.extend([int(i) for i in face[1:]])  # Convert each index to an integer and add to list


    # Create arrays of each vertex attribute
    positions = []
    normals = []
    colors = []
    texture_coords = []
    for i in range(num_vertices):

        positions.extend((vertex_data['x'][i],        # Vertex position
                          vertex_data['y'][i], 
                          vertex_data['z'][i]))

        normals.extend((vertex_data['nx'][i],         # Normal
                        vertex_data['ny'][i], 
                        vertex_data['nz'][i]))

        colors.extend((vertex_data['r'][i],           # Color
                       vertex_data['g'][i],
                       vertex_data['b'][i]))

        texture_coords.extend((vertex_data['u'][i],   # Texture coordinates
                               vertex_data['v'][i]))


    # Convert to arrays
    with warnings.catch_warnings():
        
        # Ignore warnings from arrays with no data in the file
        warnings.simplefilter("ignore", category=RuntimeWarning)

        positions = np.array(positions, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        colors = np.array(colors, dtype=np.uint32)
        texture_coords = np.array(texture_coords, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

    return positions, normals, colors, texture_coords, indices
