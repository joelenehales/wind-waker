// Vertex shader

#version 400

// Input vertex data, different for all executions of this shader
layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec2 textureCoord;
layout(location = 2) in vec3 vertexNormal;

// Output data, passed to fragment shader to interpolate color
out vec2 uv_vs;
out vec3 normal_vs;

void main(){

    // Output data
    gl_Position = vec4(vertexPosition,1);  // Vertex position
    normal_vs = vertexNormal;              // Normal vector
    uv_vs = textureCoord;                  // Texture coordinates

}