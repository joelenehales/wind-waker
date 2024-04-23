// Vertex shader

#version 400

// Input vertex data, different for all executions of this shader
layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;

// Output data, passed to tesselation control shader and fragment shader
out vec3 eye_vs;
out vec3 light_vs;
out vec3 normal_vs;
out vec2 uv_vs;

// Uniforms, stay constant for the whole mesh
uniform mat4 V;
uniform mat4 M;
uniform float time;
uniform vec3 light_direction;

void main(){
    
    // Output vertex position, in world coordinates
    gl_Position = vec4(vertexPosition,1);

    // Compute and output texture coordinates
    uv_vs = (vertexPosition.xz + 0.1 * time) / 50;

    // Compute and output required vectors for fragment shader
    // Eye direction
    vec3 vertexPosition_cameraspace = ( V * M * vec4(vertexPosition,1)).xyz;
    eye_vs = vec3(0,0,0) - vertexPosition_cameraspace;

    // Light direction
    vec3 light_position = ( V * vec4(light_direction,1)).xyz;
    light_vs = light_position + eye_vs;

    // Normal
    normal_vs = ( V * M * vec4(vertexNormal,0)).xyz;

}