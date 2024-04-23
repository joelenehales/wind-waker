# Class generates and renders a patch of water.
# Author:  Joelene Hales

from OpenGL.GL import *
import numpy as np
from helpers import *


class Water():
    """ Class generates and stores the data to render a patch of water.
    
    The patch of water is generated as a simple quad mesh, which is manipulated
    using tessellation and geometry shaders to render it as a patch of water.
    Vertex data is contained in a vertex array object and restored to
    render the mesh. Tessellation uses an outer and inner tessellation level of
    16 to generate additional vertices. The geometry shader displaces the
    interpolated vertex positions by a superpositoin of 4 Gerstner waves at a
    given moment in time. The water's color and the displacement map used to
    manipulate the mesh are supplied as bitmap images.

    Attributes
    ----------
    program_ID : int
        Integer ID of shader program.
    VAO : int
	    Integer ID of the vertex array object used to restore state and render
	    the patch of water.
    texture_ID : int
        Integer ID of generated texture objects (water and displacement map).
    MVP_uniform : int
        Integer handle for model view projection matrix uniform variable in
        shader program.
    V_uniform : int
        Integer handle for view matrix uniform variable in shader program.
    M_uniform : int
        Integer handle for model matrix uniform variable in shader program.
    light_direction_uniform : int
        Integer handle for light direction vector uniform variable in shader program.
    outer_tess_uniform : int
        Integer handle for outer tessellation level uniform variable in shader program.
    inner_tess_uniform : int
        Integer handle for inner tessellation level uniform variable in shader
        program.
    displacement_map_uniform : int
        Integer handle for displacement map uniform variable in shader program.
    water_texture_uniform : int
        Integer handle for water texture image uniform variable in shader program.
    time_uniform : int
        Integer handle for time uniform variable in shader program.
    num_indices : int
        Number of indices in the mesh.

    Methods
    -------
    draw(MVP, V, M, time, light_direction):
        Renders the patch of water at a given moment in time.
    
    """


    def _generate_mesh(self, range_min, range_max, stepsize):
        """ Generates a mesh of quads in the xz plane. 
        
        Both x and z range over [range_min, range_max]. The coordinate system used assumed that the origin is at (range_min, 0, range_min). The algorithm then builds the mesh from the origin down in z then to the right in x. The size of each quad is specified by the stepsize.
        
        Parameters
        ----------
        range_min : float
            Maximum value of x and z in the generated mesh.
        range_max : float
            Maximum value of x and z in the generated mesh.
        stepsize : float
            Size of each quad.

        Returns
        -------
        vertices : np.ndarray, dtype=np.float32
            Vertices in the mesh.
        normals : np.ndarray, dtype=np.float32
            Normal to each vertex.
        indices : np.ndarray, dtype=np.uint32
            Indices defining each quad in the mesh.

        
        """
        
        # Initialize arrays to store each vertex attribute
        vertices = []
        normals = []
        indices = []

        y = 0  # Mesh in the xz plane

        # Build the mesh
        for z in np.arange(range_min, range_max+stepsize, stepsize):
            for x in np.arange(range_min, range_max+stepsize, stepsize):
                vertices.extend((x, y, z))
                normals.extend((0,1,0))


        # Create list of vertex indices defining each quad in the mesh
        num_quads = int((range_max - range_min) / stepsize)  # Quads in each row/column
        num_columns = num_quads +1
        
        for x_i in range(num_quads):

            for z_i in range(num_quads):
                
                # Define indices, in counter clockwise winding order
                top_left = x_i*num_columns + z_i
                top_right = x_i*num_columns + z_i + 1
                bottom_right = (x_i+1)*num_columns + z_i + 1
                bottom_left = (x_i+1)*num_columns + z_i

                indices.extend((top_left, top_right, bottom_right, bottom_left))


        # Convert to arrays
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

        return vertices, normals, indices



    def __init__(self, range_min, range_max, stepsize):
        """ Generates the mesh and initializes the shaders to create waves.

        The simple quad mesh is manipulated using tessellation and geometry
        shaders to render it as a patch of water. Vertex data is contained in a
        vertex array object and restored to render the mesh. Tessellation uses
        an outer and inner tessellation level of 16. The geometry shader
        displaces the interpolated vertex positions by a superpositoin of 4
        Gerstner waves at a given moment in time. The water's color and the
        displacement map used to manipulate the mesh are supplied as bitmap
        images.
        
        Parameters
        ----------
        range_min : float
            Maximum value of x and z in the generated mesh.
        range_max : float
            Maximum value of x and z in the generated mesh.
        stepsize : float
            Size of each quad.
        
        """

        # Define directories to shader codes and texture images
        assets_directory = "Assets/"
        shader_directory = "Shaders/"

        # Generate the quad mesh
        vertices, normals, indices = self._generate_mesh(range_min, range_max, stepsize)

        self.num_indices = int(len(indices))

        
        # Import shader codes from file
        vertex_shader = open(shader_directory+"water.vs", "r").read()
        tessellation_control_shader = open(shader_directory+"water.tcs", "r").read()
        tessellation_evaluation_shader = open(shader_directory+"water.tes", "r").read()
        geometry_shader = open(shader_directory+"water.gs", "r").read()
        fragment_shader = open(shader_directory+"water.fs", "r").read()


        # Create vertex and fragment shaders
        vertex_shader_ID = glCreateShader(GL_VERTEX_SHADER)
        tessellation_control_shader_ID = glCreateShader(GL_TESS_CONTROL_SHADER)
        tessellation_evaluation_shader_ID = glCreateShader(GL_TESS_EVALUATION_SHADER)
        geometry_shader_ID = glCreateShader(GL_GEOMETRY_SHADER)
        fragment_shader_ID = glCreateShader(GL_FRAGMENT_SHADER)

        # Set shader source codes
        glShaderSource(vertex_shader_ID, vertex_shader)
        glShaderSource(tessellation_control_shader_ID, tessellation_control_shader)
        glShaderSource(tessellation_evaluation_shader_ID, tessellation_evaluation_shader)
        glShaderSource(geometry_shader_ID, geometry_shader)
        glShaderSource(fragment_shader_ID, fragment_shader)
        
        
        # Compile each shader
        glCompileShader(vertex_shader_ID)
        glCompileShader(tessellation_control_shader_ID)
        glCompileShader(tessellation_evaluation_shader_ID)
        glCompileShader(geometry_shader_ID)
        glCompileShader(fragment_shader_ID)


        # Check for compilation errors
        if not(glGetShaderiv(vertex_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(vertex_shader_ID))
        if not(glGetShaderiv(tessellation_control_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(tessellation_control_shader_ID))
        if not(glGetShaderiv(tessellation_evaluation_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(tessellation_evaluation_shader_ID))
        if not(glGetShaderiv(geometry_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(geometry_shader_ID))
        if not(glGetShaderiv(fragment_shader_ID, GL_COMPILE_STATUS)):
            raise RuntimeError(glGetShaderInfoLog(fragment_shader_ID))
        

        # Attach shaders and link shader program
        self.program_ID = glCreateProgram()

        glAttachShader(self.program_ID, vertex_shader_ID)
        glAttachShader(self.program_ID, tessellation_control_shader_ID)
        glAttachShader(self.program_ID, tessellation_evaluation_shader_ID)
        glAttachShader(self.program_ID, geometry_shader_ID)
        glAttachShader(self.program_ID, fragment_shader_ID)
        glLinkProgram(self.program_ID)

        # Check for linking error
        if not(glGetProgramiv(self.program_ID, GL_LINK_STATUS)):
            raise RuntimeError(glGetProgramInfoLog(self.program_ID))


        # Unlink shader program
        glDetachShader(self.program_ID, vertex_shader_ID)
        glDetachShader(self.program_ID, tessellation_control_shader_ID)
        glDetachShader(self.program_ID, tessellation_evaluation_shader_ID)
        glDetachShader(self.program_ID, geometry_shader_ID)
        glDetachShader(self.program_ID, fragment_shader_ID)

        glDeleteShader(vertex_shader_ID)
        glDeleteShader(tessellation_control_shader_ID)
        glDeleteShader(tessellation_evaluation_shader_ID)
        glDeleteShader(geometry_shader_ID)
        glDeleteShader(fragment_shader_ID)

        glUseProgram(0)


        # Get handle for each uniform variable
        self.MVP_uniform = glGetUniformLocation(self.program_ID, "MVP")
        self.V_uniform = glGetUniformLocation(self.program_ID, "V")
        self.M_uniform = glGetUniformLocation(self.program_ID, "M")
        self.light_direction_uniform = glGetUniformLocation(self.program_ID, "light_direction")
        self.outer_tess_uniform = glGetUniformLocation(self.program_ID, "outerTess")
        self.inner_tess_uniform = glGetUniformLocation(self.program_ID, "innerTess")
        self.displacement_map_uniform = glGetUniformLocation(self.program_ID, "displacementTexture")
        self.water_texture_uniform = glGetUniformLocation(self.program_ID, "waterTexture")
        self.time_uniform = glGetUniformLocation(self.program_ID, "time")


        # Read bitmap files
        water_image,water_width,water_height = read_bitmap(assets_directory+"water.bmp")
        displacement_map,displacement_width,displacement_height = read_bitmap(assets_directory+"displacement-map1.bmp")


		# Generate textures
        self.texture_ID = glGenTextures(2)   # One for water, one for displacement map

        # Load water texture
        glBindTexture(GL_TEXTURE_2D, self.texture_ID[0])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, water_width, water_height, 0, GL_BGR, GL_UNSIGNED_BYTE, water_image)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

        # Load displacement map
        glBindTexture(GL_TEXTURE_2D, self.texture_ID[1])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, displacement_width, displacement_height, 0, GL_BGR, GL_UNSIGNED_BYTE, displacement_map)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)


		# Create and bind VAO
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

		# Create and bind VBO for vertex positions
        vertex_VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_VBO)
        glBufferData(GL_ARRAY_BUFFER, np.dtype(np.float32).itemsize*len(vertices), vertices, GL_STATIC_DRAW)

        # Set vertex position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0,            # Attribute number
            3,            # Size (Number of components)
            GL_FLOAT,     # Type
            GL_FALSE,     # Normalized?
            0,            # Stride (Byte offset)
            None          # Offset
        )

        # Create and bind VBO for normal vectors
        normal_VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, normal_VBO)
        glBufferData(GL_ARRAY_BUFFER, np.dtype(np.float32).itemsize*len(vertices), normals, GL_STATIC_DRAW)

		# Set normal attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1,            # Attribute number
            3,            # Size (Number of components)
            GL_FLOAT,     # Type
            GL_TRUE,      # Normalized?
            0,            # Stride (Byte offset)
            None          # Offset
        )


        # Create and bind EBO for face indices
        face_EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, face_EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.dtype(np.uint32).itemsize*self.num_indices, indices, GL_STATIC_DRAW)

        glBindVertexArray(0)  # Unbind VAO



    def draw(self, MVP, V, M, time, light_direction):
        """ Renders the patch of water at a given moment in time.

        Parameters
        ----------
		MVP : glm.mat4
			Model view projection matrix.
        V : glm.mat4
            View matrix.
        M : glm.mat4
            Model matrix.
        time : float
            Time elapsed.
        light_direction : glm.vec3
            Light direction.
        
        """

        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Specify patch size
        glPatchParameteri(GL_PATCH_VERTICES, 4)

        # Bind water texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_ID[0])

        # Bind displacement map
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_ID[1])

        # Use program
        glUseProgram(self.program_ID)


        # Set uniforms
        glUniformMatrix4fv(self.MVP_uniform, 1, GL_FALSE, matrix_to_array(MVP, 4))  # Matrices
        glUniformMatrix4fv(self.V_uniform, 1, GL_FALSE, matrix_to_array(V, 4))
        glUniformMatrix4fv(self.M_uniform, 1, GL_FALSE, matrix_to_array(M, 4))

        glUniform3f(self.light_direction_uniform, light_direction.x, light_direction.y, light_direction.z)
        
        glUniform1f(self.inner_tess_uniform, 16)  # Tessellation levels
        glUniform1f(self.outer_tess_uniform, 16)

        glUniform1f(self.time_uniform, time)  # Time elapsed

        glUniform1i(self.water_texture_uniform, 0)     # Water texture, GL_TEXTURE0
        glUniform1i(self.displacement_map_uniform, 1)  # Displacement map, GL_TEXTURE1


        # Bind VAO to restore captured state
        glBindVertexArray(self.VAO)

        # Draw the mesh
        glDrawElements(GL_PATCHES, self.num_indices, GL_UNSIGNED_INT, None)

        # Unbind VAO and textures, clean up shader program
        glBindVertexArray(0)
        glUseProgram(0)
        glDisable(GL_BLEND)