
# Classes used to load and render the boat.
# Author:  Joelene Hales

from OpenGL.GL import *
import numpy as np
from helpers import *


class TextureMesh():
    """ Class representing a textured triangle mesh. 

    Vertex attributes and mesh faces are loaded from a PLY file. The mesh's
    texture is loaded from a bitmap image file. This data is contained in a
    vertex array object and restored to render the mesh. The shader program
    includes a geometry shader which shifts the vertex positions up and down.
    This creates the effect of the boat bobbing up and down in the water.

    Attributes
    ----------
    program_ID : int
        Integer ID of shader program.
    VAO : int
	    Integer ID of the vertex array object used to restore state and render
	    the mesh.
    texture_ID : int
        Integer ID of generated texture object.
    MVP_uniform : int
        Integer handle for model view projection matrix uniform variable in
        shader program.
    texture_uniform : int
        Integer handle for the mesh's texture uniform variable in shader program.
    time_uniform : int
        Integer handle for time uniform variable in shader program.
    num_indices : int
        Number of indices in the mesh.

    Methods
    -------
    draw(MVP, time):
        Renders the texture mesh object.

    """

    def __init__(self, ply_file, bitmap_file):
        """ Loads the textured triangle mesh and initializes the shader programs
        to render it.
        
        Vertex attributes and mesh faces are loaded from a PLY file. The mesh's
        texture is loaded from a bitmap image file. This data is contained in a
        vertex array object and restored to render the mesh. The shader program
        includes a geometry shader which shifts the vertex positions up and
        down. This creates the effect of the boat bobbing up and down in the
        water.

        Parameters
        ----------
        ply_file : str
            Filepath to a PLY file.
        bitmap_file : str
            Filepath to a bitmap image file.

        """

        # Read mesh data from PLY file
        positions,normals,_,texture_coordinates,indices = read_ply(ply_file)
        self.num_indices = len(indices)

        # Import shader codes from file
        shader_directory = "Shaders/"
        vertex_shader_code = open(shader_directory+"boat.vs", 
        "r").read()
        geometry_shader_code = open(shader_directory+"boat.gs", "r").read()
        fragment_shader_code = open(shader_directory+"boat.fs", "r").read()

        # Create vertex and fragment shaders
        vertex_shader_ID = glCreateShader(GL_VERTEX_SHADER)
        geometry_shader_ID = glCreateShader(GL_GEOMETRY_SHADER)
        fragment_shader_ID = glCreateShader(GL_FRAGMENT_SHADER)

        # Set shader source code
        glShaderSource(vertex_shader_ID, vertex_shader_code) 
        glShaderSource(geometry_shader_ID, geometry_shader_code)
        glShaderSource(fragment_shader_ID, fragment_shader_code)

        # Compile shaders
        glCompileShader(vertex_shader_ID)
        glCompileShader(geometry_shader_ID)
        glCompileShader(fragment_shader_ID)

        # Check for compilation errors
        if not(glGetShaderiv(vertex_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(vertex_shader_ID))
        if not(glGetShaderiv(geometry_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(geometry_shader_ID))
        if not(glGetShaderiv(fragment_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(fragment_shader_ID))


        # Attach shaders and link shader program
        self.program_ID = glCreateProgram()

        glAttachShader(self.program_ID, vertex_shader_ID)
        glAttachShader(self.program_ID, geometry_shader_ID)
        glAttachShader(self.program_ID, fragment_shader_ID)
        glLinkProgram(self.program_ID)

        # Check for linking error
        if not(glGetProgramiv(self.program_ID, GL_LINK_STATUS)):
            raise RuntimeError(glGetProgramInfoLog(self.program_ID))


        # Unlink shader program
        glDetachShader(self.program_ID, vertex_shader_ID)
        glDetachShader(self.program_ID, geometry_shader_ID)
        glDetachShader(self.program_ID, fragment_shader_ID)

        glDeleteShader(vertex_shader_ID)
        glDeleteShader(geometry_shader_ID)
        glDeleteShader(fragment_shader_ID)

        glUseProgram(0)
        

        # Get handle for each uniform variable
        self.MVP_uniform = glGetUniformLocation(self.program_ID, "MVP")
        self.time_uniform = glGetUniformLocation(self.program_ID, "time")
        self.texture_uniform = glGetUniformLocation(self.program_ID, "textureImage")


        # Read bitmap images
        bitmap_image, texture_width, texture_height = read_bitmap(bitmap_file)

        # Generate textures
        self.texture_ID = glGenTextures(1)

        # Load texture image
        glBindTexture(GL_TEXTURE_2D, self.texture_ID)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, texture_width, texture_height, 0, GL_BGRA, GL_UNSIGNED_BYTE, bitmap_image)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)


        # Create and bind VAO
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        # Create and bind VBO for vertex positions
        vertex_VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_VBO)
        glBufferData(GL_ARRAY_BUFFER, np.dtype(np.float32).itemsize*len(positions), positions, GL_STATIC_DRAW)

        # Set vertex attributes for vertex positions
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0,            # Attribute number
            3,            # Size (Number of components)
            GL_FLOAT,     # Type
            GL_FALSE,     # Normalized?
            0,            # Stride (Byte offset)
            None          # Offset
        )

        # Create and bind VBO for texture coordinates
        texture_VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, texture_VBO)
        glBufferData(GL_ARRAY_BUFFER, np.dtype(np.float32).itemsize*len(texture_coordinates), texture_coordinates, GL_STATIC_DRAW)

        # Set vertex attributes for texture coordinates
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1,            # Attribute number
            2,            # Size (Number of components)
            GL_FLOAT,     # Type
            GL_FALSE,     # Normalized?
            0,            # Stride (Byte offset)
            None          # Offset
        )


        # Create and bind VBO for vertex normals
        normal_VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, normal_VBO)
        glBufferData(GL_ARRAY_BUFFER, np.dtype(np.float32).itemsize*len(normals), normals, GL_STATIC_DRAW)

        # Set vertex attributes for vertex normals
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            2,            # Attribute number
            3,            # Size (Number of components)
            GL_FLOAT,     # Type
            GL_TRUE,      # Normalized?
            0,            # Stride (Byte offset)
            None          # Offset
        )


        # Create and bind EBO for face indices
        face_EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, face_EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.dtype(np.uint32).itemsize*self.num_indices,indices, GL_STATIC_DRAW)

        glBindVertexArray(0)  # Unbind VAO


    def draw(self, MVP, time):
        """ Renders the texture mesh object.

        Parameters
        ----------
        MVP : glm.mat4
            Model view projection matrix.
        time : float
            Time elapsed. Used to calculate the position of the wave at a given
            moment in time, to create the effect of the boat bobbing up and down
            in the water. 

        """

        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Bind water texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_ID)

        # Use program and set uniforms
        glUseProgram(self.program_ID)
        glUniformMatrix4fv(self.MVP_uniform, 1, GL_FALSE, matrix_to_array(MVP, 4))
        glUniform1f(self.time_uniform, time)

        # Bind VAO to restore captured state
        glBindVertexArray(self.VAO)

        # Draw triangles
        glDrawElements(GL_TRIANGLES, self.num_indices, GL_UNSIGNED_INT, None)

        # Unbind VAO and texture, clean up shader program
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glDisable(GL_BLEND)


class Boat():
    """ Contains all textured meshes in the boat. 

    Additional details on how each textured mesh is loaded, stored, and rendered
    can be found in the documentation for the TextureMesh class.
    
    Attributes
    ----------
    body : TextureMesh
        Textured triangle mesh for the boat's body (hull and mast).
    head : TextureMesh
        Textured triangle mesh for the boat's head.
    eyes : TextureMesh
        Textured triangle mesh for the eyes of the boat's head.

    Methods
    -------
    draw(MVP, time):
        Renders the boat by rendering the mesh for each individual component of the boat.
    
    """

    def __init__(self):
        """ Creates the textured mesh for each component of the boat. """

        assets = "Assets/"   # Directory containing all assets (PLY files and bitmap images)

        # Create textured triangle mesh for each component of the boat
        self.body = TextureMesh(assets+"boat.ply", assets+"boat.bmp")
        self.head = TextureMesh(assets+"head.ply", assets+"head.bmp")
        self.eyes = TextureMesh(assets+"eyes.ply", assets+"eyes.bmp")


    def draw(self, MVP, time):
        """ Renders the boat by rendering the mesh for each individual component of the boat.
        
        Parameters
        ----------
        MVP : glm.mat4
            Model view projection matrix.
        time : float
            Time elapsed. Used to calculate the position of the wave at a given
            moment in time, to create the effect of the boat bobbing up and down
            in the water. 
    
        
        """

        self.body.draw(MVP, time)
        self.head.draw(MVP, time)
        self.eyes.draw(MVP, time)
