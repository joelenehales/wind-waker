// Geometry shader

#version 400

layout (triangles) in;  // Type of input primitive expected
layout (triangle_strip, max_vertices=3) out;  // Type of output primitive

// Input data, from vertex shader
in vec3 position_tes[];
in vec2 uv_tes[];
in vec3 normal_tes[];
in vec3 eye_tes[];
in vec3 light_tes[];

// Output data per vertex, passed to primitive assembly and rasterization
out vec3 normal_gs;
out vec3 eye_gs;
out vec3 light_gs;
out vec2 uv_gs;

// Shader variables
vec4 pos[gl_in.length()];  // Perturbed vertex positions

// Uniforms, stay constant for the whole mesh
uniform mat4 MVP;
uniform sampler2D displacementTexture;
uniform float time;

vec3 getNormal(vec4 a, vec4 b, vec4 c) {
    vec3 x = b.xyz - a.xyz;
    vec3 y = c.xyz - b.xyz;
    return normalize(cross(x, y));
}

vec3 Gerstner(vec3 worldpos, float w, float A, float phi, float Q, vec2 D, int N) {

    // Compute sharpness from given normalized value, frequency, amplitude and number of waves
    Q = Q / (w * A * N);
    
    // Compute position of the Gerster wave
    float x = Q * A * D.x * cos(w * dot(D, vec2(worldpos.x, worldpos.z)) + phi * time);
    float z = Q * A * D.y * cos(w * dot(D, vec2(worldpos.x, worldpos.z)) + phi * time);
    float y = A * sin(w * dot(D, vec2(x, z)) + phi * time);

    return vec3(x, y, z);

}

void main() {

    for(int i = 0; i < gl_in.length(); ++i) {  // Iterate over each vertex

        pos[i] = vec4(position_tes[i], 1.0);

        // Compute Gerstner waves and perturb vertex position
        pos[i] += vec4(Gerstner(position_tes[i], 4, 0.08, 1.1, 0.75, vec2(0.3, 0.6), 4), 0.0);
        pos[i] += vec4(Gerstner(position_tes[i], 2, 0.05, 1.1, 0.75, vec2(0.2,
        0.866), 4), 0.0);
        pos[i] += vec4(Gerstner(position_tes[i], 0.6, 0.2, 0.4, 0.1, vec2(0.3, 0.7), 4), 0.0);
        pos[i] += vec4(Gerstner(position_tes[i], 0.9, 0.15, 0.4, 0.1, vec2(0.8,
        0.1), 4), 0.0);

        // Apply displacement mapping to add extra depth to waves
        float strength = 0.5;
        float displacement = texture(displacementTexture, uv_tes[i]).r - 0.5;
        pos[i].y += strength * displacement;

        gl_Position = pos[i];

    }

    // Re-calculate normal of the triangle after perturbing vertex positions
    vec3 normal = getNormal(gl_in[1].gl_Position, gl_in[0].gl_Position, gl_in[2].gl_Position);

    for(int i = 0; i < gl_in.length(); ++i) {

        // Output perturbed vertex positions, in clip space
        gl_Position = MVP * pos[i];

        // Output remaining vertex attributes
        normal_gs = normal;
        uv_gs = uv_tes[i];

        // Output vectors required to compute lighting
        eye_gs = eye_tes[i];
        light_gs = light_tes[i];

        EmitVertex();
    }

    EndPrimitive();

}