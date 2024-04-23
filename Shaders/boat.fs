
// Fragment shader

#version 400

// Input data from vertex shader
in vec2 uv_gs;
in vec3 normal_gs;

// Ouput data
out vec4 fragColor;

// Uniform values that stay constant for the  whole mesh
uniform sampler2D textureImage;

void main(){

    // Output fragment data
    fragColor = texture(textureImage, uv_gs);  // Sample color from texture

}