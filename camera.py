# Class representing the camera.
# Author:  Joelene Hales

import glm
import numpy as np
from helpers import *


class Camera():
    """ Camera which supports "globe" movements.
    
    The camera supports "globe" movements using spherical coordinates. The
    class stores the camera's center coordinate, look direction, and direction
    of up. Various methods are provided to manipulate the camera's position and
    handle conversions between Cartesian and spherical coordinates.

    Attributes
    ----------
    eye : glm.vec3
        Camera's look direction, in Cartesian coordinates. Does not change.
    up : glm.vec3
        Direction of up, in Cartesian coordinates. Does not change.
    radius : float
        Radius in camera's position in spherical coordinates.
    theta : float
        Azimuthal angle in camera's position in spherical coordinates.
    phi : float
        Polar angle in camera's position in spherical coordinates.

    Methods
    -------
    rotatePhi(increment):
        Rotates the camera up/down by incrementing the polar angle phi by a given amount, in radians.
    rotateTheta(increment):
        Rotates the camera around at a fixed elevation by incrementing the azimuthal angle theta by a given amount, in radians.
    zoomRadius(increment):
        Zooms the camera in/out by incrementing the radius.
    getCenter():
        Calculates the camera's position in Cartesian coordinates. 
    getUp(): 
        Returns the direction of up, in Cartesian coordinates.
    getEye():
        Returns the camera's look direction, in Cartesian coordinates.

    """

    def __init__(self, center, eye, up):
        """ Initializes the camera.

        Parameters
        ----------
        center : glm.vec3
            Camera position, in Cartesian coordinates.
        eye : glm.vec3
            Camera's look direction, in Cartesian coordinates.
        up : glm.vec3
            Direction of up, in Cartesian coordinates.
        
        """

        # Validate input vectors
        for vector in [center, eye, up]:  
            if (type(vector) != glm.vec3):
                raise TypeError("Vectors must be given as GLM 3D vectors.") 

        # Initialize camera vectors that do not change, in Cartesian coordinates
        self.eye = eye
        self.up = up

        # Calculate radius, theta, and phi values by converting center coordinate from Cartesian spherical coordinates
        self.radius = np.sqrt(center.x**2 + center.y**2 + center.z**2)
        self.theta = np.arctan(center.z / center.x)
        self.phi = np.arccos(center.y / self.radius)


    def rotatePhi(self, increment):
        """ Increments the polar angle phi by a given amount, in radians. Has
        the effect of rotating the camera up or down. Clamps the angle between
        epsilon and pi - epsilon to prevent the camera from flipping.
        
        Parameters
        ----------
        increment : float
            Amount to increment the angle by, in radians.
        
        """

        self.phi += increment
        
        # Clamp between epsilon and pi - epsilon to prevent vector from flipping and producing unwanted effects
        epsilon = 0.001
        self.phi = clamp(self.phi, epsilon, np.pi - epsilon)


    def rotateTheta(self, increment):
        """ Increments the azimuthal angle theta by a given amount, in radians.
        Has the effect of rotating the camera to spin around at a fixed elevation.
        
        Parameters
        ----------
        increment : float
            Amount to increment the angle by, in radians.
        
        """

        self.theta += increment


    def zoomRadius(self, increment):
        """ Increments the radius by a given amount. Has the effect of zooming
        the camera in for a negative value, or out for a positive value. The
        camera is stopped before the radius becomes negative.
        
        Parameters
        ----------
        increment : float
            Amount to increment the radius.
        
        """

        self.radius += increment

        # Do not let radius become negative
        if (self.radius <= 0.0001):
            self.radius = 0.0001


    def getCenter(self):
        """ Calculates the camera's position in Cartesian coordinates. 
        
        Returns
        -------
        center : glm.vec3
            Camera's position, in Cartesian coordinates.

        """

        # Calculate each coordinate from spherical coordinates
        x = self.radius * np.cos(self.theta) * np.sin(self.phi)
        y = self.radius * np.cos(self.phi)
        z = self.radius * np.sin(self.theta) * np.sin(self.phi)

        center = glm.vec3(x, y, z)  # Camera position, in Cartesian coordinates

        return center


    def getUp(self):
        """ Returns the direction of up, in Cartesian coordinates. 
        
        Returns
        -------
        up : glm.vec3
            Direction of up, in Cartesian coordinates.
        
        """

        return self.up


    def getEye(self):
        """ Returns the look direction, in Cartesian coordinates. 
        
        Returns
        -------
        eye : glm.vec3
            Camera's look direction, in Cartesian coordinates.

        """

        return self.eye
    