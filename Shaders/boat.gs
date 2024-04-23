// Geometry shader

#version 400

layout (triangles) in;  // Type of input primitive expected
layout (triangle_strip, max_vertices=3) out;  // Type of output primitive

// Input data, from vertex shader
in vec2 uv_vs[];
in vec3 normal_vs[];

// Output data per vertex, passed to primitive assembly and rasterization
out vec3 normal_gs;
out vec2 uv_gs;

// Shader variables
vec4 pos[gl_in.length()];  // Perturbed vertex positions

// Uniforms, stay constant for the whole mesh
uniform mat4 MVP;
uniform float time;

vec3 Gerstner(vec3 worldpos, float w, float A, float phi, float Q, vec2 D, int N) {
    
    // Compute sharpness from given normalized value, frequency, amplitude and number of waves
    Q = Q / (w * A * N);
    
    // Compute position of Gerstner wave
    float x = Q * A * D.x * cos(w * dot(D, vec2(worldpos.x, worldpos.z)) + phi * time);
    float z = Q * A * D.y * cos(w * dot(D, vec2(worldpos.x, worldpos.z)) + phi * time);
    float y = A * sin(w * dot(D, vec2(x, z)) + phi * time);

    return vec3(x, y, z);

}

void main() {

    for(int i = 0; i < gl_in.length(); ++i) {  // Iterate over each vertex

        vec4 position_gs = gl_in[i].gl_Position;

        // Simulate boat bobbing up and down on the water
        position_gs.y += Gerstner(position_gs.xyz, 4, 0.08, 1.1, 0.75, vec2(0.3, 0.6), 4).y;
        position_gs.y += Gerstner(position_gs.xyz, 2, 0.05, 1.1, 0.75, vec2(0.2, 0.866), 4).y;
        position_gs.y += Gerstner(position_gs.xyz, 0.6, 0.2, 0.4, 0.1, vec2(0.3, 0.7), 4).y;
        position_gs.y += Gerstner(position_gs.xyz, 0.9, 0.15, 0.4, 0.1, vec2(0.8, 0.1), 4).y;

        // Output vertex data
        gl_Position = MVP * position_gs;
        normal_gs = normal_vs[i];
        uv_gs = uv_vs[i];

        EmitVertex();
    }
    EndPrimitive();

}